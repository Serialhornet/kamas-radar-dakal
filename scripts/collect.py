import json, os, urllib.parse, urllib.request, datetime, pathlib, re
ROOT = pathlib.Path(__file__).resolve().parents[1]
cfg = json.loads((ROOT/'config/sources.json').read_text(encoding='utf-8'))
out = ROOT/'docs/data.json'
old = json.loads(out.read_text(encoding='utf-8')) if out.exists() else {'items': []}
items = {v['id']: v for v in old.get('items', [])}
key = os.getenv('YOUTUBE_API_KEY')
if not key:
    raise SystemExit('Secret YOUTUBE_API_KEY absent. Configure-le dans GitHub Settings > Secrets and variables > Actions.')
now = datetime.datetime.now(datetime.timezone.utc)
after = (now-datetime.timedelta(days=cfg['lookback_days'])).isoformat().replace('+00:00','Z')
def get(endpoint, args):
    args['key'] = key
    url = 'https://www.googleapis.com/youtube/v3/' + endpoint + '?' + urllib.parse.urlencode(args)
    with urllib.request.urlopen(url, timeout=30) as response:
        return json.load(response)
ids = []
for query in cfg['queries']:
    try:
        found = get('search', {'part':'snippet', 'type':'video', 'q':query, 'order':'date', 'publishedAfter':after, 'maxResults':min(50,cfg['max_results_per_query']), 'relevanceLanguage':'fr', 'regionCode':'FR'})
    except Exception as exc:
        print('Erreur YouTube pour', query, str(exc))
        continue
    for entry in found.get('items',[]):
        vid = entry.get('id',{}).get('videoId')
        if not vid: continue
        sn = entry['snippet']
        ids.append(vid)
        items[vid] = {'id':vid, 'title':sn.get('title',''), 'description':sn.get('description','')[:500], 'channel':sn.get('channelTitle',''), 'date':sn.get('publishedAt',''), 'url':'https://www.youtube.com/watch?v='+vid, 'views':items.get(vid,{}).get('views'), 'source':'YouTube officiel'}
for start in range(0,len(set(ids)),50):
    chunk = list(dict.fromkeys(ids))[start:start+50]
    try:
        stats = get('videos', {'part':'statistics', 'id':','.join(chunk)})
        for v in stats.get('items',[]):
            if v['id'] in items:
                views = v.get('statistics',{}).get('viewCount')
                items[v['id']]['views'] = int(views) if views is not None else None
    except Exception as exc:
        print('Statistiques indisponibles:',str(exc))
for x in items.values():
    try: age = max(0,(now-datetime.datetime.fromisoformat(x['date'].replace('Z','+00:00'))).total_seconds()/86400)
    except Exception: age = 30
    views = x.get('views')
    x['score'] = round(max(0,50-age*1.5)+(25 if views is None else max(0,25-views/1000))+ (15 if re.search('brisage|craft|métier|farm',x['title'],re.I) else 0),1)
    x['fiche_fr'] = 'Piste à étudier : regarder la vidéo, relever les ressources et recettes, puis comparer les prix et frais sur Dakal. Rentabilité non vérifiée.'
ordered = sorted(items.values(),key=lambda x:x['score'],reverse=True)[:250]
out.write_text(json.dumps({'server':'Dakal','updated_at':now.isoformat(),'items':ordered},ensure_ascii=False,indent=2),encoding='utf-8')
print(len(ordered),'pistes enregistrées')
