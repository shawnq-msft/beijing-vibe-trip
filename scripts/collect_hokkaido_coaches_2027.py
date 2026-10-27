"""Preserve current original-page coach evidence; do not infer availability."""
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
import hashlib,json
from pathlib import Path
import requests
from bs4 import BeautifulSoup
ROOT=Path(__file__).resolve().parents[1]
URLS=['https://www.fuyuski.co/zh-hans/team','https://www.fuyuski.co/zh-hans/book','https://www.fuyuski.co/zh-hans/kids-ski-lessons','https://www.propeak.org/','https://www.propeak.org/private-lessons']
def fetch(url):
    stamp=datetime.now(timezone.utc).isoformat()
    r=requests.get(url,timeout=45);r.raise_for_status()
    s=BeautifulSoup(r.text,'html.parser')
    for x in s.select('script,style,noscript'):x.decompose()
    text=s.get_text(' ',strip=True)
    return dict(url=url,final_url=r.url,retrieved_at=stamp,status=r.status_code,title=s.title.get_text() if s.title else '',sha256=hashlib.sha256(r.content).hexdigest(),text=text)
results=list(ThreadPoolExecutor(max_workers=5).map(fetch,URLS))
(ROOT/'data/hokkaido-2027-coach-primary-recheck.json').write_text(json.dumps(results,ensure_ascii=False,indent=2))
for x in results:
    print(x['url'],x['status'],len(x['text']))
    if 'book' in x['url'] or 'private-lessons' in x['url']:
        t=x['text'];print(t[:18000])
