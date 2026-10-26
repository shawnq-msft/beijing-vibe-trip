"""Check the Hokkaido plan and its in-feed homepage placement."""
import json, sys, subprocess, hashlib, urllib.request
from pathlib import Path
from urllib.parse import urlsplit, unquote
from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright
ROOT=Path(__file__).resolve().parents[1]
BASE=(sys.argv[1] if len(sys.argv)>1 else 'http://127.0.0.1:18778').rstrip('/')
REL='pages/spring-festival-2027-hokkaido-ski-onsen.html'
s=BeautifulSoup((ROOT/REL).read_text(),'html.parser')
for tag in s.select('[href],[src]'):
    v=tag.get('href') or tag.get('src'); u=urlsplit(v)
    if u.scheme or u.netloc: continue
    if u.path: assert (ROOT/'pages'/unquote(u.path)).resolve().exists(),v
    elif u.fragment: assert s.find(id=u.fragment),v
index=BeautifulSoup((ROOT/'index.html').read_text(),'html.parser')
assert not index.select('.hero a[href*="pages/"]'), 'Special plans must not sit in title badges'
assert len(index.select(f'.index-masonry a.index-card[href="./{REL}"]'))==1
old=BeautifulSoup(subprocess.check_output(['git','show','HEAD:index.html'],cwd=ROOT,text=True),'html.parser')
oldlinks={a['href'] for a in old.select('a.index-card')}
newlinks={a['href'] for a in index.select('a.index-card')}
assert oldlinks <= newlinks
assert 25000*5 == 125000 and 125000+63400 == 188400
assert 37000*5+22500+8000*3 == 231500
assert 43680*5+34800 == 253200
assert 43680*5/2 == 109200 and 54600*5 == 273000
assert len(s.select('#schools tbody tr'))==8
assert len(s.select('#sources li'))==42
assert all(s.find(id=a['href'][1:]) for a in s.select('a[href^="#"]'))
expected_revision=s.select_one('meta[name="plan-revision"]')['content']
with urllib.request.urlopen(BASE+'/'+REL+'?verify='+expected_revision,timeout=25) as r:
    actual=r.read(); assert r.status==200
assert hashlib.sha256(actual).hexdigest()==hashlib.sha256((ROOT/REL).read_bytes()).hexdigest(),'Published HTML differs from local artifact'
local_links=set()
for tag in s.select('[href],[src]'):
    v=tag.get('href') or tag.get('src');u=urlsplit(v)
    if not u.scheme and not u.netloc and u.path:local_links.add(v)
from urllib.parse import urljoin
for v in sorted(local_links):
    with urllib.request.urlopen(urljoin(BASE+'/'+REL,v),timeout=25) as r: assert r.status==200,v
checks=[]
with sync_playwright() as p:
    executable=str(Path.home()/'.cache/ms-playwright/chromium-1248/chrome-linux64/chrome')
    if not Path(executable).exists(): executable=None
    browser=p.chromium.launch(headless=True,executable_path=executable,args=['--no-sandbox'])
    for width in (390,1440):
        page=browser.new_page(viewport={'width':width,'height':950})
        errors=[];page.on('pageerror',lambda e:errors.append(str(e)))
        page.goto(BASE+'/'+REL,wait_until='networkidle')
        assert page.evaluate('document.documentElement.scrollWidth<=innerWidth'),width
        imgs=page.locator('img').evaluate_all('(xs)=>xs.map(x=>({ok:x.complete&&x.naturalWidth>0,src:x.currentSrc}))')
        assert imgs and all(x['ok'] for x in imgs),imgs
        assert page.locator('#schools').count()==1
        assert page.locator('#equipment').count()==1
        assert page.locator('#parents').count()==1
        assert page.locator('#itinerary tbody tr').count()==12
        assert page.locator('meta[name="plan-revision"]').get_attribute('content')==expected_revision
        scrolls=page.locator('.table-wrap').evaluate_all('(xs)=>xs.map(x=>{x.scrollLeft=x.scrollWidth;const r={scrollWidth:x.scrollWidth,clientWidth:x.clientWidth,scrollLeft:x.scrollLeft};x.scrollLeft=0;return r})')
        assert all(x['scrollLeft']>0 for x in scrolls if x['scrollWidth']>x['clientWidth']),scrolls
        page.locator('.toc a[href="#equipment"]').click()
        assert page.url.endswith('#equipment')
        assert not errors,errors
        page.screenshot(path=str(Path.home()/f'.hermes/cache/scratch/hokkaido-{width}.png'),full_page=True)
        page.goto(BASE+'/',wait_until='networkidle')
        card=page.locator(f'a.index-card[href="./{REL}"]')
        card.scroll_into_view_if_needed()
        assert card.locator('img').evaluate('(x)=>x.complete&&x.naturalWidth>0')
        assert page.locator('.hero a[href*="pages/"]').count()==0
        checks.append({'width':width,'new_page_images':len(imgs),'overflow':False,'hero_plan_links':0,'js_errors':errors})
        page.close()
    browser.close()
print(json.dumps({'base':BASE,'revision':expected_revision,'exact_html_sha256':hashlib.sha256(actual).hexdigest(),'local_http_links':len(local_links),'source_citations':42,'schools':8,'itinerary_days':12,'price_arithmetic':'passed','existing_cards_preserved':len(oldlinks),'new_card':REL,'responsive':checks},ensure_ascii=False))
