// Supabase Edge Function de gestion des invitations Radar Dakal.
import { createClient } from "npm:@supabase/supabase-js@2";
const headers = { "Access-Control-Allow-Origin": "https://serialhornet.github.io", "Access-Control-Allow-Headers": "authorization, apikey, content-type", "Access-Control-Allow-Methods": "POST, OPTIONS", "Content-Type": "application/json" };
const send = (status: number, data: unknown) => new Response(JSON.stringify(data), { status, headers });
const secret = () => Array.from(crypto.getRandomValues(new Uint8Array(20))).map(x => x.toString(16).padStart(2, "0")).join("").toUpperCase();
Deno.serve(async request => {
  if (request.method === "OPTIONS") return new Response(null, { headers });
  if (request.method !== "POST") return send(405, { error: "Méthode refusée" });
  const url = Deno.env.get("SUPABASE_URL") || "";
  const service = Deno.env.get("SUPABASE_SERVICE_ROLE_KEY") || "";
  if (!url || !service) return send(503, { error: "Configuration manquante" });
  const jwt = (request.headers.get("Authorization") || "").replace(/^Bearer /, "");
  if (!jwt) return send(401, { error: "Connexion requise" });
  const db = createClient(url, service, { auth: { persistSession: false } });
  const check = await db.auth.getUser(jwt);
  if (!check.data.user) return send(401, { error: "Session invalide" });
  const actor = check.data.user.id;
  const { data: owner } = await db.from("radar_profiles").select("role,active").eq("id", actor).single();
  if (!owner?.active || owner.role !== "admin") return send(403, { error: "Administrateur requis" });
  let command: { action?: string; pseudo?: string; email?: string; id?: string };
  try { command = await request.json() } catch { return send(400, { error: "JSON requis" }) }
  if (command.action === "list") {
    const { data, error } = await db.from("radar_profiles").select("id,pseudo,role,active,created_at").order("created_at");
    return error ? send(500, { error: "Lecture impossible" }) : send(200, { profiles: data });
  }
  if (command.action === "create") {
    const pseudo = String(command.pseudo || "").trim();
    const email = String(command.email || "").trim().toLowerCase();
    if (pseudo.length < 2 || pseudo.length > 30 || !/^[\\p{L}\\p{N} _.'-]+$/u.test(pseudo)) return send(400, { error: "Pseudo invalide" });
    if (email.length > 254 || !/^[^\\s@]+@[^\\s@]+\\.[^\\s@]+$/.test(email)) return send(400, { error: "Adresse e-mail invalide" });
    // Un mot de passe provisoire est émis une seule fois au créateur. Le joueur peut le changer.
    const password = secret() + secret();
    const created = await db.auth.admin.createUser({ email, password, email_confirm: true });
    if (!created.data.user) return send(400, { error: "Impossible de créer ce compte : adresse déjà utilisée ou refus Supabase" });
    const profile = await db.from("radar_profiles").insert({ id: created.data.user.id, pseudo, role: "player", active: true });
    if (profile.error) {
      await db.auth.admin.deleteUser(created.data.user.id);
      return send(400, { error: "Pseudo déjà utilisé ou création échouée" });
    }
    return send(200, { email, password, pseudo });
  }
  const id = String(command.id || "");
  if (!/^[0-9a-f-]{36}$/i.test(id) || id === actor) return send(400, { error: "Joueur invalide" });
  const { data: target } = await db.from("radar_profiles").select("id,role").eq("id", id).single();
  if (!target || target.role !== "player") return send(404, { error: "Joueur non trouvé" });
  if (command.action === "disable" || command.action === "enable") {
    await db.from("radar_profiles").update({ active: command.action === "enable" }).eq("id", id);
    // Les politiques RLS refusent immédiatement les opérations aux profils suspendus.
    return send(200, { ok: true });
  }
  if (command.action === "reset") {
    const password = secret() + secret();
    const updated = await db.auth.admin.updateUserById(id, { password });
    if (updated.error) return send(500, { error: "Renouvellement impossible" });
    // Les JWT existants peuvent rester valides jusqu'à expiration : blocage immédiat via RLS si besoin.
    return send(200, { password });
  }
  return send(400, { error: "Action inconnue" });
});
