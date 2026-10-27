"""Capture Japanese coaches, English shortlist and FX primary pages."""
import datetime, hashlib, json
from pathlib import Path
import requests
from bs4 import BeautifulSoup
ROOT=Path(__file__).resolve().parents[1]
urls=[
'https://rusutsu.com/snow_school/ski-lessons/',
'https://kk-ss.com/message.html',
'https://www.snowpro.jp/our-instructors',
'https://www.snowpro.jp/private-lessons-guiding',
'https://www.jdsskiing.com/about',
'https://pinnaclesnow.com/en/instructors/alex',
'https://wise.com/in/currency-converter/jpy-to-cny-rate/history']
rows=[]
for url in urls:
 r=requests.get(url,timeout=60); r.raise_for_status(); r.encoding='utf-8'
 s=BeautifulSoup(r.text,'html.parser')
 for x in s.select('script,style'): x.decompose()
 text=s.get_text(' ',strip=True)
 rows.append(dict(url=url,retrieved_at=datetime.datetime.now(datetime.timezone.utc).isoformat(),status=r.status_code,sha256=hashlib.sha256(r.content).hexdigest(),text=text))
 print(url, len(text))
 if 'rusutsu.com/snow_school' in url:
  for term in ['成田伊織ハイ','押切 凌','日本語でコミュニケーション']:
   i=text.find(term);print(term,text[max(0,i-100):i+850])
 if 'wise.com' in url:
  i=text.find('CNY');print(text[max(0,i-160):i+200])
(ROOT/'data/hokkaido-2027-jp-fx-recheck.json').write_text(json.dumps(rows,ensure_ascii=False,indent=2))
