"""Capture text-only budget evidence from the existing real host browser.
Never launches or connects a replacement browser; the caller checks CDP reuse.
"""
import argparse, datetime, hashlib, json, subprocess, time
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
parser=argparse.ArgumentParser();parser.add_argument('key');parser.add_argument('--url');parser.add_argument('--wait',type=int,default=10)
a=parser.parse_args()
def ab(*args):
 return subprocess.check_output(['timeout','50','agent-browser',*args],text=True,timeout=55).strip()
ab('tab','hokkaidobudget')
if a.url:
 print(ab('open',a.url));time.sleep(a.wait)
expr='''JSON.stringify({url:location.href,title:document.title,text:document.body.innerText,ua:navigator.userAgent,price_labels:[...document.querySelectorAll('[aria-label]')].map(x=>x.getAttribute('aria-label')).filter(x=>/price: CNY|Total CNY/.test(x)),inputs:[...document.querySelectorAll('input:not([type=hidden])')].filter(x=>x.placeholder||x.getAttribute('aria-label')).map(x=>({placeholder:x.placeholder,value:x.value,aria:x.getAttribute('aria-label')})),headings:[...document.querySelectorAll('h1,h2')].map(x=>x.innerText)})'''
raw=ab('eval',expr)
obj=json.loads(raw)
if isinstance(obj,str):obj=json.loads(obj)
obj['retrieved_at']=datetime.datetime.now(datetime.timezone.utc).isoformat();obj['sha256_text']=hashlib.sha256(obj['text'].encode()).hexdigest()
p=ROOT/'data/hokkaido-2027-budget-browser';p.mkdir(exist_ok=True)
(p/f'{a.key}.json').write_text(json.dumps(obj,ensure_ascii=False,indent=2))
print(json.dumps({'key':a.key,'url':obj['url'],'inputs':obj['inputs'],'price_labels':obj.get('price_labels',[])[:12],'text':obj['text'].split('Guest Reviews')[0][:14000]},ensure_ascii=False))
