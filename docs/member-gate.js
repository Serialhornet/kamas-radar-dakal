"use strict";
// Contrôle de navigation : GitHub Pages reste un hébergement public.
// Les données sensibles sont protégées par Supabase RLS.
(async () => {
  const login = new URL("./connexion-admin.html", location.href).href;
  const toLogin = () => { if (window.top !== window.self) window.top.location.replace(login); else window.location.replace(login); };
  try {
    const community = window.RadarCommunity;
    if (!community?.ready) throw Error("Service de connexion indisponible");
    const profile = await community.current();
    if (!profile) {
      toLogin();
      return;
    }
    document.documentElement.classList.add("members-authorized");
    const heartbeat = () => { if (!document.hidden) void community.heartbeat?.().catch(() => {}); };
    heartbeat();
    setInterval(heartbeat, 45000);
    document.addEventListener("visibilitychange", async () => {
      if (document.hidden) return;
      try {
        if (!await community.current()) toLogin();
        else heartbeat();
      } catch { toLogin(); }
    });
    setInterval(async () => {
      if (document.hidden) return;
      try { if (!await community.current()) toLogin(); }
      catch { toLogin(); }
    }, 45000);
  } catch {
    toLogin();
  }
})();
