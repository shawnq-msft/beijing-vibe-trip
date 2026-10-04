"""Validate guide data, navigation, images and responsive filters.
Run with requests, beautifulsoup4, pillow and playwright installed.
Usage: python scripts/test_national_day_2026.py [base_url]
"""
import json, sys, subprocess
from pathlib import Path
from urllib.parse import unquote, urlsplit
import requests
from bs4 import BeautifulSoup
from PIL import Image
from playwright.sync_api import sync_playwright
ROOT=Path(__file__).resolve().parents[1]
BASE=(sys.argv[1] if len(sys.argv)>1 else 'http://127.0.0.1:18766').rstrip('/')
REL='pages/national-day-2026-family-events.html'
data=json.loads((ROOT/'data/national-day-2026-ranked.json').read_text())
a=data['activities'];assert len(a)==10 and len({x['id'] for x in a})==10
r=requests.get(BASE+'/'+REL,timeout=30);r.raise_for_status();r.encoding='utf-8'
soup=BeautifulSoup(r.text,'html.parser')
assert len(soup.select('article.event'))==len(a)
ids={x.get('id') for x in soup.select('[id]')}
for el in soup.select('[href],[src]'):
    v=el.get('href') or el.get('src');u=urlsplit(v)
    if u.scheme or u.netloc:continue
    if u.path:assert (ROOT/'pages'/unquote(u.path)).resolve().exists(),v
    elif u.fragment:assert u.fragment in ids,v
index_response=requests.get(BASE+'/',timeout=30);index_response.raise_for_status();index_response.encoding='utf-8'
index=BeautifulSoup(index_response.text,'html.parser')
cards=index.select('a.index-card')
assert sum(x.get('href')=='./'+REL for x in cards)==1
assert cards[0].get('href')=='./'+REL
old=BeautifulSoup(subprocess.check_output(['git','show','HEAD:index.html'],cwd=ROOT,text=True),'html.parser')
old_links={x.get('href') for x in old.select('a.index-card')};new_links={x.get('href') for x in cards}
assert old_links<=new_links
for im in json.loads((ROOT/'data/national-day-2026-images.json').read_text()):
    with Image.open(ROOT/im['file']) as image:assert image.format=='WEBP' and image.size==(im['width'],im['height'])
checks=[]
with sync_playwright() as p:
    browser=p.chromium.launch(headless=True)
    for width in (390,1440):
        page=browser.new_page(viewport={'width':width,'height':950})
        errors=[];page.on('pageerror',lambda err:errors.append(str(err)))
        page.goto(BASE+'/'+REL,wait_until='networkidle')
        imgs=page.locator('img').evaluate_all('(xs)=>xs.map(x=>({ok:x.complete&&x.naturalWidth>0,ratio:Math.abs(x.height/x.width-x.naturalHeight/x.naturalWidth)}))')
        assert all(x['ok'] and x['ratio']<0.015 for x in imgs),imgs
        assert page.evaluate('document.documentElement.scrollWidth<=innerWidth'),width
        for day in ('all','4','5','6','7'):
            for kind in ('all','indoor','outdoor','sport'):
                page.select_option('#day',day);page.select_option('#kind',kind)
                expected=sum((day=='all' or int(day) in x['dates']) and (kind=='all' or x['type']==kind) for x in a)
                assert page.locator('article.event:visible').count()==expected,(day,kind,expected)
                assert page.locator('tbody tr:visible').count()==expected
        page.select_option('#day','all');page.select_option('#kind','all')
        page.screenshot(path=f'/tmp/national-day-2026-{width}.png',full_page=True)
        assert not errors,errors
        checks.append({'width':width,'images_ok':len(imgs),'filter_combinations':20,'overflow':False,'js_errors':errors})
        page.goto(BASE+'/',wait_until='domcontentloaded')
        page.locator(f'a.index-card[href="./{REL}"] img').wait_for()
        assert page.locator(f'a.index-card[href="./{REL}"] img').evaluate('(x)=>x.complete&&x.naturalWidth>0')
        page.close()
    browser.close()
print(json.dumps({'base':BASE,'activities':len(a),'rank_order':[x['rank'] for x in a],'existing_index_cards_preserved':len(old_links),'new_homepage_entry':True,'responsive_checks':checks},ensure_ascii=False))
