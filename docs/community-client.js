"use strict";
// Client communautaire. Seule la clef ANON/publishable Supabase est visible dans le navigateur.
(() => {
const cfg=window.RADAR_COMMUNITY_CONFIG||{};
const ready=Boolean(cfg.enabled&&/^https:\/\//.test(cfg.url)&&cfg.anonKey&&window.supabase?.createClient);
const client=ready?window.supabase.createClient(cfg.url,cfg.anonKey,{auth:{persistSession:true,autoRefreshToken:true,detectSessionInUrl:false}}):null;
let member=null;
const keyEmail=(key)=>{
 const cleaned=String(key||"").trim().toUpperCase().replace(/\s/g,"");
 const parts=cleaned.match(/^RD-([A-F0-9]{16}|ADMIN)-([A-F0-9]{24,100})$/);
 if(!parts)throw Error("Clé invalide. Format RD-IDENTIFIANT-SECRET.");
 return {email:"radar-"+parts[1].toLowerCase()+"@radar-dakal.example.com",password:parts[2]};
};
async function current(){
 if(!client)return null;
 const {data:{user},error}=await client.auth.getUser();
 if(error||!user){member=null;return null}
 const {data:p,error:profileError}=await client.from("radar_profiles").select("id,pseudo,role,active").eq("id",user.id).single();
 if(profileError||!p?.active){member=null;return null}
 member=p;return p;
}
async function login(key){
 if(!client)throw Error("Espace communautaire non activé. Configure d'abord Supabase.");
 const creds=keyEmail(key);
 const {error}=await client.auth.signInWithPassword(creds);
 if(error)throw Error("Clé incorrecte ou compte indisponible.");
 const profile=await current();
 if(!profile){await client.auth.signOut();throw Error("Profil inactif ou non enregistré.")}
 return profile;
}
async function logout(){await client?.auth.signOut();member=null}
async function admin(action,params={}){
 const p=await current();if(p?.role!=="admin")throw Error("Accès administrateur refusé");
 const {data:{session}}=await client.auth.getSession();
 if(!session?.access_token)throw Error("Session expirée");
 const res=await fetch(cfg.url.replace(/\/$/,"")+"/functions/v1/radar-admin",{
  method:"POST",headers:{"Content-Type":"application/json","Authorization":"Bearer "+session.access_token,"apikey":cfg.anonKey},
  body:JSON.stringify({action,...params})
 });
 const json=await res.json().catch(()=>({error:"Réponse serveur illisible"}));
 if(!res.ok)throw Error(json.error||"Action administrateur impossible");
 return json;
}
async function getPrices(){
 if(!await current())throw Error("Connexion nécessaire");
 const {data,error}=await client.from("radar_shared_prices").select("item_id,unit_price,updated_at,updated_by").eq("server","Dakal").limit(10000);
 if(error)throw error;return data||[];
}
async function savePrice(itemId,price){
 const p=await current();if(!p)throw Error("Connexion nécessaire");
 if(!Number.isSafeInteger(Number(itemId))||Number(itemId)<=0||!Number.isSafeInteger(Number(price))||Number(price)<0)throw Error("ID ou prix invalide");
 const {error}=await client.from("radar_shared_prices").upsert({item_id:Number(itemId),unit_price:Number(price),server:"Dakal",updated_by:p.id,updated_at:new Date().toISOString()},{onConflict:"item_id"});
 if(error)throw error;
}
async function getVotes(id){
 if(!await current())throw Error("Connexion nécessaire");
 const {data,error}=await client.from("radar_votes").select("user_id,value").eq("trick_id",id);
 if(error)throw error;return data||[];
}
async function vote(id,value){
 const p=await current();if(!p)throw Error("Connexion nécessaire");
 if(!id||id.length>250||![-1,0,1].includes(value))throw Error("Vote invalide");
 if(value===0){const {error}=await client.from("radar_votes").delete().eq("trick_id",id).eq("user_id",p.id);if(error)throw error}
 else{const {error}=await client.from("radar_votes").upsert({trick_id:id,user_id:p.id,value,updated_at:new Date().toISOString()},{onConflict:"trick_id,user_id"});if(error)throw error}
}
async function getComments(id){
 if(!await current())throw Error("Connexion nécessaire");
 const {data,error}=await client.from("radar_comments").select("id,user_id,body,created_at").eq("trick_id",id).order("created_at",{ascending:false}).limit(100);
 if(error)throw error;return data||[];
}
async function comment(id,body){
 const p=await current();if(!p)throw Error("Connexion nécessaire");
 body=String(body||"").trim();
 if(!id||id.length>250||!body||body.length>1200)throw Error("Commentaire invalide");
 const {error}=await client.from("radar_comments").insert({trick_id:id,user_id:p.id,body});
 if(error)throw error;
}
async function getState(tool){
 const p=await current();if(!p)throw Error("Connexion nécessaire");
 const {data,error}=await client.from("radar_personal_state").select("state").eq("user_id",p.id).eq("tool",tool).maybeSingle();
 if(error)throw error;return data?.state??null;
}
async function saveState(tool,state){
 const p=await current();if(!p)throw Error("Connexion nécessaire");
 const {error}=await client.from("radar_personal_state").upsert({user_id:p.id,tool,state,updated_at:new Date().toISOString()},{onConflict:"user_id,tool"});
 if(error)throw error;
}
window.RadarCommunity={ready,client,keyEmail,current,login,logout,admin,getPrices,savePrice,getVotes,vote,getComments,comment,getState,saveState,get member(){return member}};
})();
