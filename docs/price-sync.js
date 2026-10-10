"use strict";
/* Dakal: prix HDV communautaires. Le cache local reste intact. */
(()=>{
 const api=()=>window.RadarCommunity;
 const records=new Map(),authors=new Map();
 const listeners=new Set();
 let active=false,loading=null,lastError="",lastRefresh=0;
 const channel=typeof BroadcastChannel==="function"?new BroadcastChannel("radar-dakal-prices"):null;
 function emit(){for(const fn of listeners){try{fn()}catch(e){console.warn("PriceSync listener",e)}}}
 async function refresh(){
  if(loading)return loading;
  loading=(async()=>{
   try{
    const client=api();
    if(!client?.ready){active=false;lastError="Supabase indisponible";return false}
    const user=await client.current();
    if(!user){active=false;records.clear();lastError="Connexion communautaire nécessaire";emit();return false}
    const prices=await client.getPrices();
    records.clear();
    for(const p of prices)records.set(Number(p.item_id),{value:Number(p.unit_price),at:p.updated_at,by:p.updated_by});
    active=true;lastError="";lastRefresh=Date.now();emit();return true;
   }catch(e){lastError=e?.message||String(e);emit();return false}
   finally{loading=null}
  })();
  return loading;
 }
 async function save(id,value){
  if(!active)return {shared:false,reason:lastError||"Connexion inactive"};
  if(!Number.isSafeInteger(Number(id))||Number(id)<=0||!Number.isSafeInteger(value)||value<0)return {shared:false,reason:"Prix communautaire entier positif requis"};
  try{
   await api().savePrice(id,value);
   records.set(Number(id),{value,at:new Date().toISOString(),by:api().member?.id||null});
   channel?.postMessage({source:"shared-cloud",server:"Dakal"});
   emit();return {shared:true};
  }catch(e){lastError=e?.message||String(e);emit();return {shared:false,reason:lastError}}
 }
 function get(id){return active?records.get(Number(id))||null:null}
 function author(id){return authors.get(id)||'Membre Radar'}
 channel?.addEventListener("message",e=>{if(e.data?.source==="shared-cloud")void refresh()});
 window.addEventListener("focus",()=>{if(Date.now()-lastRefresh>10000)void refresh()});
 document.addEventListener("visibilitychange",()=>{if(!document.hidden&&Date.now()-lastRefresh>10000)void refresh()});
 setInterval(()=>{if(!document.hidden&&active)void refresh()},60000);
 window.RadarPriceSync={refresh,save,get,author,onChange:fn=>{listeners.add(fn);return()=>listeners.delete(fn)},get active(){return active},get error(){return lastError},get count(){return records.size}};
})();
