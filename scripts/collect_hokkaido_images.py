"""Acquire official resort photos and preserve their source pages."""
from pathlib import Path
import json, io
import requests
from bs4 import BeautifulSoup
from PIL import Image
from urllib.parse import urljoin
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'assets/hokkaido-2027';OUT.mkdir(exist_ok=True)
urls=['https://rusutsu.com/en/rusutsu-in-winter/','https://rusutsu.com/en/onsen-wellness/']
manifest=[]
for u in urls:
    r=requests.get(u,timeout=45);print(u,r.status_code)
    if r.status_code!=200:continue
    s=BeautifulSoup(r.text,'html.parser')
    candidates=[]
    for im in s.select('img'):
        src=im.get('data-src') or im.get('src') or ''
        if '/uploads/' in src and not any(x in src.lower() for x in ['banner','logo','720x300','award','img01_en']):
            candidates.append((src,im.get('alt','')))
    for src,alt in candidates[:5]:
        ir=requests.get(urljoin(u,src),timeout=45);ir.raise_for_status()
        try:im=Image.open(io.BytesIO(ir.content));im.load()
        except Exception:continue
        if im.width<700 or im.height<350:continue
        im.thumbnail((1600,1200));name='winter.webp' if 'winter/' in u else 'onsen.webp'
        im.convert('RGB').save(OUT/name,'WEBP',quality=86)
        manifest.append({'file':'assets/hokkaido-2027/'+name,'source_page':u,'image_url':src,'alt':alt,'size':im.size,'status':'official promotional photo, not target-date operating proof'})
        print(manifest[-1]);break
(ROOT/'data/hokkaido-2027-images.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2))
