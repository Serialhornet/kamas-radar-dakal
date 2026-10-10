"use strict";
// Un outil imbriqué réutilise l'accès validé par la page principale.
// Seule une page ouverte directement vérifie indépendamment son compte.
(async()=>{
 const home=new URL("./index.html",location.href).href;
 const embedded=window.parent!==window;
 if(embedded){
  try{
   const host=window.parent;
   if(host.location.origin!==location.origin)throw Error("Origine différente");
   const update=()=>{
    const allowed=host.document.getElementById("communityLock")?.hidden===true
      && !host.document.documentElement.classList.contains("community-locked");
    document.documentElement.classList.toggle("members-authorized",allowed);
   };
   update();
   host.addEventListener("pageshow",update);
   host.addEventListener("radar-auth-changed",update);
   document.addEventListener("visibilitychange",update);
   setInterval(update,15000);
  }catch{
   // Ne jamais naviguer dans la page parente depuis un outil : cela dupliquait le site.
   document.documentElement.classList.remove("members-authorized");
  }
  return;
 }
 const redirect=()=>window.location.replace(home);
 try{
  const community=window.RadarCommunity;
  if(!community?.ready||!await community.current()){redirect();return}
  document.documentElement.classList.add("members-authorized");
  const refresh=async()=>{
   try{
    if(!await community.current()){redirect();return}
    if(!document.hidden)await community.heartbeat?.();
   }catch{redirect()}
  };
  void community.heartbeat?.().catch(()=>{});
  setInterval(()=>{if(!document.hidden)void refresh()},45000);
  document.addEventListener("visibilitychange",()=>{if(!document.hidden)void refresh()});
 }catch{redirect()}
})();
