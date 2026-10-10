"use strict";
// Contrôle de navigation : GitHub Pages reste un hébergement public.
// Les données sensibles sont protégées par Supabase RLS.
(async () => {
  const login = "./connexion-admin.html";
  try {
    const community = window.RadarCommunity;
    if (!community?.ready) throw Error("Service de connexion indisponible");
    const profile = await community.current();
    if (!profile) {
      window.location.replace(login);
      return;
    }
    document.documentElement.classList.add("members-authorized");
    const heartbeat = () => { if (!document.hidden) void community.heartbeat?.().catch(() => {}); };
    heartbeat();
    setInterval(heartbeat, 45000);
    document.addEventListener("visibilitychange", async () => {
      if (document.hidden) return;
      try {
        if (!await community.current()) window.location.replace(login);
        else heartbeat();
      } catch { window.location.replace(login); }
    });
    setInterval(async () => {
      if (document.hidden) return;
      try { if (!await community.current()) window.location.replace(login); }
      catch { window.location.replace(login); }
    }, 45000);
  } catch {
    window.location.replace(login);
  }
})();
