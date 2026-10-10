"""Kamas Radar: YouTube Data API v3, sans extraction de sous-titres ni de DoFocus."""
import datetime, email.utils, html, json, os, pathlib, re, urllib.parse, urllib.request, xml.etree.ElementTree as ET

ROOT = pathlib.Path(__file__).resolve().parents[1]
CFG = json.loads((ROOT / "config/sources.json").read_text(encoding="utf-8"))
OUT = ROOT / "docs/data.json"
KEY = os.getenv("YOUTUBE_API_KEY")
NOW = datetime.datetime.now(datetime.timezone.utc)

RETRO = re.compile(r"\b(?:dofus\s*retro|retro\s*dofus|dofus\s*touch|boune|dofus\s*1[.,]29|dofus\s*2[.,]\d+)\b", re.I)
UNITY = re.compile(r"\b(?:dofus\s*(?:unity|3(?:[.,]\d+)?|3d)|unity\s*dofus|dakal(?:\s*\d+)?|monocompte\s+dakal)\b", re.I)
# Exclure les methodes aleatoires ou necessitant une equipe multicompte.
EXCLUDE_TITLE = re.compile(r"\b(?:songes?|dreams?\s+infinis?|infinit[eé]\s+dreams?|multicompte|multi[- ]comptes?|multi[- ]account|team\s+(?:de\s+)?(?:4|5|6|8)|team\s+(?:cr[aâ]|sadi|enu|panda)|8\s+(?:personnages|comptes|persos)|PL\s+songes?)\b", re.I)
EXCLUDE_DESCRIPTION = re.compile(r"\b(?:songes?\s+infinis?|farm\s+songes?|team\s+de\s+8|en\s+multicompte|multi[- ]comptes?)\b", re.I)
MONO = re.compile(r"\b(?:monocompte|mono[- ]compte|single[- ]account|solo|dakal|pionnier)\b", re.I)
PREFERRED = re.compile(r"lurk|brisage|bris(er|[ée])|runes?|craft|fabrication|m[ée]tier|r[ée]colte|achat[- ]revente|commerce|flipping|farm|drop|ressources?|zone", re.I)
KAMAS = re.compile(r"kamas?|brisage|briser|runes?|craft|farm|m[ée]tier|rentabilit[ée]|astuce|ganar|ganhar|making money", re.I)
SIGNALS = {
 "attention": re.compile(r"\b(?:nerf|nerfed|patch|plus\s+rentable|pas\s+rentable|obsol[èe]te|arnaque|faux|no\s+funciona|n[aã]o\s+funciona|not\s+working)\b", re.I),
 "prix": re.compile(r"\b(?:prix|hdv|hotel\s+de\s+vente|march[ée]|co[uû]t|kamas?|precio|pre[cç]o)\b", re.I),
 "confirmation": re.compile(r"\b(?:merci|test[ée]|fonctionne|rentable|valide|works|funciona|obrigad[oa]|gracias)\b", re.I)
}
CATEGORY = [(r"lurk","Lurk / marché"),
            (r"achat[- ]revente|commerce|flipping","Commerce / revente"),
            (r"brisage|briser|runes?","Brisage / runes"),
            (r"craft|m[ée]tier|fabrication|recette","Craft / métiers"),
            (r"farm|drop|zone|combat","Farm / drop")]
def clean(x):
    return re.sub(r"\s+"," ",html.unescape(re.sub(r"<[^>]+>"," ",x or ""))).strip()
def request(endpoint, args):
    url = "https://www.googleapis.com/youtube/v3/" + endpoint + "?" + urllib.parse.urlencode(dict(args, key=KEY))
    with urllib.request.urlopen(urllib.request.Request(url,headers={"User-Agent":"KamasRadarDakal/2.0"}),timeout=25) as response:
        return json.load(response)
def category(title):
    return next((label for pattern,label in CATEGORY if re.search(pattern,title,re.I)),"Astuces kamas")
def comments_for(vid):
    """Top-level public comments only; bounded, no replies, no transcript, no usernames."""
    try:
        data=request("commentThreads", {"part":"snippet","videoId":vid,"maxResults":20,
                                        "order":"relevance","textFormat":"plainText"})
    except Exception as exc:
        print("Commentaires indisponibles pour",vid,str(exc)[:170])
        return {"status":"indisponibles","analysed":0,"signals":{},"examples":[]}
    texts=[clean(c.get("snippet",{}).get("topLevelComment",{}).get("snippet",{}).get("textDisplay",""))[:350]
           for c in data.get("items",[])]
    signals={}
    for kind,pattern in SIGNALS.items():
        examples=[t for t in texts if pattern.search(t)]
        signals[kind]={"count":len(examples),"examples":examples[:2]}
    return {"status":"echantillon","analysed":len(texts),"signals":signals,
            "examples":[],"notice":"Commentaires publics non verifies; echantillon limite. Pas de traduction automatique."}
def detail_for(item):
    label=category(item["title"])
    return {"categorie":label,"resume_source":item["description"] or "Description absente.",
            "methode":"Non verifiee : la transcription de la video n'est pas disponible par cette API.",
            "prerequis":"A verifier : niveau, metiers, materiel et acces a la zone.",
            "budget":"Inconnu; verifier les prix sur Dakal.",
            "rentabilite":"Non calculee; donnees du marche Dakal manquantes.",
            "fiabilite":"Fiche descriptive basee sur les metadonnees; pas une analyse du contenu integral.",
            "langue":"Non verifiee"}

def community_feed_items():
    """Only user-authorized public RSS/Atom URLs; no page scraping or DoFocus harvesting."""
    feeds=CFG.get("rss_feeds",[])
    found=[]
    for feed in feeds[:8]:
        url=feed.get("url","")
        if not url.startswith("https://") or not feed.get("authorized",False):
            print("Flux ignoré (URL HTTPS ou autorisation absente):",feed.get("name","?"))
            continue
        try:
            req=urllib.request.Request(url,headers={"User-Agent":"KamasRadarDakal/2.2 (RSS reader)"})
            with urllib.request.urlopen(req, timeout=20) as response:
                body=response.read(800000)
            root=ET.fromstring(body)
            atom="{http://www.w3.org/2005/Atom}"
            nodes=root.findall(".//item")+root.findall(".//"+atom+"entry")
            for entry in nodes[:35]:
                title=clean(entry.findtext("title") or entry.findtext(atom+"title") or "")
                description=clean(entry.findtext("description") or entry.findtext(atom+"summary") or entry.findtext(atom+"content") or "")
                urlpost=entry.findtext("link") or ""
                linknode=entry.find(atom+"link")
                if not urlpost and linknode is not None: urlpost=linknode.attrib.get("href","")
                if not urlpost.startswith("https://") or not title:continue
                combined=title+" "+description
                if RETRO.search(combined) or EXCLUDE_TITLE.search(title) or EXCLUDE_DESCRIPTION.search(description):continue
                if not UNITY.search(combined) or not KAMAS.search(combined):continue
                rawdate=entry.findtext("pubDate") or entry.findtext(atom+"published") or entry.findtext(atom+"updated") or ""
                try:
                    date=email.utils.parsedate_to_datetime(rawdate).astimezone(datetime.timezone.utc).isoformat()
                except Exception:
                    date=rawdate if re.match(r"^\d{4}-\d\d-\d\d",rawdate) else NOW.isoformat()
                item={"id":"rss:"+urlpost,"title":title,"description":description[:500],
                    "channel":feed.get("name","Communauté"),"date":date,"url":urlpost,
                    "views":None,"source":"Sites / communautés","source_platform":"site","source_format":"article","source_type":"article","langue":"Non vérifiée"}
                found.append(item)
        except Exception as exc:print("Flux communautaire indisponible",feed.get("name",url),str(exc)[:180])
    return found

def main():
    if not KEY: raise SystemExit("Secret YOUTUBE_API_KEY absent.")
    after=(NOW-datetime.timedelta(days=int(CFG.get("lookback_days",30)))).isoformat().replace("+00:00","Z")
    collected={}
    for query in CFG.get("queries",[]):
        try:
            response=request("search", {"part":"snippet","type":"video","q":query,
              "order":"date","publishedAfter":after,"maxResults":min(25,int(CFG.get("max_results_per_query",20))),
              "relevanceLanguage":"fr","regionCode":"FR"})
        except Exception as exc:
            print("Recherche YouTube indisponible",query,str(exc)[:250]);continue
        for entry in response.get("items",[]):
            vid=entry.get("id",{}).get("videoId")
            snippet=entry.get("snippet",{})
            title=clean(snippet.get("title",""))
            description=clean(snippet.get("description",""))
            joined=title+" "+description
            if not vid or RETRO.search(joined) or EXCLUDE_TITLE.search(title) or EXCLUDE_DESCRIPTION.search(description) or not UNITY.search(joined) or not KAMAS.search(joined):
                continue
            collected[vid]={"id":vid,"title":title,"description":description[:500],
               "channel":snippet.get("channelTitle",""),"date":snippet.get("publishedAt",""),
               "url":"https://www.youtube.com/watch?v="+vid,
               "views":None,"source":"YouTube","source_platform":"youtube","source_format":"video","source_type":"video"}
    videos=list(collected)
    for start in range(0,len(videos),50):
        try:
            result=request("videos", {"part":"statistics,snippet,contentDetails","id":",".join(videos[start:start+50])})
            for v in result.get("items",[]):
                item=collected.get(v.get("id"))
                if not item:continue
                count=v.get("statistics",{}).get("viewCount")
                item["views"]=int(count) if count is not None else None
                info=v.get("snippet",{})
                item["langue"]=info.get("defaultAudioLanguage") or info.get("defaultLanguage") or "Non verifiee"
                duration=v.get("contentDetails",{}).get("duration","")
                dm=re.fullmatch(r"P(?:\d+D)?T(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?",duration)
                seconds=(int(dm.group(1) or 0)*3600+int(dm.group(2) or 0)*60+int(dm.group(3) or 0)) if dm else None
                item["duration_seconds"]=seconds
                item["source_platform"]="youtube"
                short_tag=bool(re.search(r"(?:#shorts?\b|\bshorts?\b)",item["title"]+" "+item["description"],re.I))
                item["source_format"]="short" if short_tag and seconds is not None and seconds<=180 else "court" if seconds is not None and seconds<=180 else "video"
                if item["source_format"]=="short":item["url"]="https://www.youtube.com/shorts/"+item["id"]
        except Exception as exc:print("Statistiques indisponibles",str(exc)[:200])
    # Limiter strictement le nombre d'appels pour conserver le budget gratuit.
    top_limit=min(12,int(CFG.get("max_videos_comments",12)))
    recent=sorted(collected.values(),key=lambda x:x.get("date",""),reverse=True)
    for idx,item in enumerate(recent):
        item["detail"]=detail_for(item)
        item["source_platform"]="youtube"
        item["source_format"]=item.get("source_format","video")
        title=item["title"]
        item["monocompte"]=bool(MONO.search(title+" "+item["description"]))
        item["detail"]["compatibilite_mono"]="Mention monocompte / solo / Dakal dans la source" if item["monocompte"] else "A verifier : pas de mention explicite du monocompte"
        item["detail"]["langue"]=item.get("langue","Non verifiee")
        item["commentaires"]=comments_for(item["id"]) if idx<top_limit else {
          "status":"non_analyses","analysed":0,"signals":{},"examples":[]}
        try:age=max(0,(NOW-datetime.datetime.fromisoformat(item["date"].replace("Z","+00:00"))).total_seconds()/86400)
        except Exception:age=30
        count=item.get("views")
        item["score"]=round(max(0,50-age*1.5)+(25 if count is None else max(0,25-count/1000))+
                 (15 if item["detail"]["categorie"]!="Astuces kamas" else 0)+
                 (18 if MONO.search(title) else 7 if item["monocompte"] else 0)+
                 (14 if PREFERRED.search(title) else 5 if PREFERRED.search(item["description"]) else 0),1)
        if item["commentaires"]["signals"].get("attention",{}).get("count",0):
            item["score"]=max(0,item["score"]-8)
        item["fiche_fr"]="Resume descriptif en francais; aucune transcription verifiee."
        if item.get("source_format") in ("short","court"):item["score"]+=9
    for community in community_feed_items():
        community["detail"]=detail_for(community)
        community["detail"]["compatibilite_mono"]="À vérifier dans la publication"
        community["monocompte"]=bool(MONO.search(community["title"]+" "+community["description"]))
        community["commentaires"]={"status":"non_analyses","analysed":0,"signals":{},"examples":[]}
        community["score"]=52+(12 if PREFERRED.search(community["title"]) else 0)+(10 if community["monocompte"] else 0)
        collected[community["id"]]=community
    # Liens TikTok et articles sélectionnés explicitement et vérifiables dans le dépôt.
    curated_file=ROOT/"config"/"liens-communautaires.json"
    try:curated=json.loads(curated_file.read_text(encoding="utf-8")).get("items",[])
    except Exception as exc:print("Liens communautaires indisponibles:",exc);curated=[]
    for entry in curated[:150]:
        try:
            url=entry["url"].strip()
            target=urllib.parse.urlparse(url)
            domain=(target.hostname or "").lower()
            if target.scheme!="https" or not domain or target.username or target.password:continue
            if domain=="tiktok.com" or domain.endswith(".tiktok.com"):
                platform,form="tiktok","courte"
            elif domain in ("youtube.com","www.youtube.com","youtu.be","m.youtube.com"):
                platform,form="youtube","short" if "/shorts/" in target.path else "video"
            else:platform,form="site","article"
            title=clean(str(entry.get("title","")))
            desc=clean(str(entry.get("description","")))
            if not title or RETRO.search(title+" "+desc) or EXCLUDE_TITLE.search(title) or EXCLUDE_DESCRIPTION.search(desc):continue
            if not UNITY.search(title+" "+desc) or not KAMAS.search(title+" "+desc):continue
            item={"id":"link:"+url,"title":title,"description":desc[:500],
                  "channel":clean(str(entry.get("author","Communauté"))),
                  "date":str(entry.get("date",NOW.isoformat())),"url":url,"views":None,
                  "source":"Lien sélectionné","source_platform":platform,"source_format":form,
                  "source_type":"video" if platform in ("youtube","tiktok") else "article",
                  "langue":"Non vérifiée","detail":None,"fiche_fr":"Lien sélectionné : contenu non transcrit."}
            item["detail"]=detail_for(item)
            item["detail"]["compatibilite_mono"]="À vérifier dans la source"
            item["monocompte"]=bool(MONO.search(title+" "+desc))
            item["commentaires"]={"status":"non_analyses","analysed":0,"signals":{},"examples":[]}
            item["score"]=47+(12 if PREFERRED.search(title) else 0)+(10 if item["monocompte"] else 0)
            collected[item["id"]]=item
        except Exception as exc:print("Lien ignoré",str(exc)[:140])
    ordered=sorted(collected.values(),key=lambda x:x["score"],reverse=True)[:250]
    OUT.write_text(json.dumps({"server":"Dakal","updated_at":NOW.isoformat(),"items":ordered,
      "notice":"DOFUS Unity/Dakal; commentaires publics indicatifs; aucune transcription ni verification de prix."},
      ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print(len(ordered),"pistes Unity/Dakal; commentaires analyses pour",min(len(recent),top_limit),"videos")
if __name__=="__main__":main()
