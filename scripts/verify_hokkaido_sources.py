"""Re-fetch the plan's public primary sources; never infer availability."""
import concurrent.futures, datetime, hashlib, json, re, urllib.request
from pathlib import Path
from bs4 import BeautifulSoup
ROOT=Path(__file__).resolve().parents[1]
ski=json.loads((ROOT/'data/hokkaido-2027-ski-research.json').read_text())
family=(ROOT/'data/hokkaido-2027-family-research.md').read_text()
urls=list(dict.fromkeys([s['url'] for s in ski['sources']]+re.findall(r'https?://[^\s)]+',family)))
def fetch(url):
    rec={'url':url,'retrieved_at':datetime.datetime.now(datetime.timezone.utc).isoformat()}
    try:
        req=urllib.request.Request(url,headers={'User-Agent':'Mozilla/5.0'})
        with urllib.request.urlopen(req,timeout=25) as r:
            raw=r.read(); rec.update(status=r.status,final_url=r.url,sha256=hashlib.sha256(raw).hexdigest())
            if 'pdf' in r.headers.get('Content-Type',''):
                rec['note']='PDF fetched; not parsed by this HTML recheck'
            else:
                soup=BeautifulSoup(raw,'html.parser')
                for el in soup(['script','style','noscript','svg']): el.decompose()
                rec['title']=soup.title.get_text(' ',strip=True) if soup.title else ''
                rec['text']=soup.get_text('\n',strip=True)
    except Exception as e: rec['error']=str(e)
    return rec
with concurrent.futures.ThreadPoolExecutor(max_workers=8) as ex:
    results=list(ex.map(fetch,urls))
(ROOT/'data/hokkaido-2027-official-recheck.json').write_text(json.dumps(results,ensure_ascii=False,indent=2))
print(json.dumps({'total':len(results),'retrieved':sum(x.get('status')==200 for x in results),'failures':[{k:v for k,v in x.items() if k in ('url','error','status')} for x in results if x.get('status')!=200]},ensure_ascii=False))
