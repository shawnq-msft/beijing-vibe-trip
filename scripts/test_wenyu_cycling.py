"""Static references, index regression, responsive/image browser checks."""
from pathlib import Path
from bs4 import BeautifulSoup
from urllib.parse import urlsplit, unquote
from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler
from functools import partial
from threading import Thread
import subprocess, json, sys
from playwright.sync_api import sync_playwright
ROOT=Path(__file__).resolve().parents[1]
PAGE='pages/wenyu-cycling-wudaokou.html'
changed=['index.html',PAGE,'pages/五月-北京-骑行专区-亲子绿道总览.html']
for name in changed:
    soup=BeautifulSoup((ROOT/name).read_text(),'html.parser')
    ids=[x['id'] for x in soup.select('[id]')]
    assert len(ids)==len(set(ids)),(name,'duplicate ids')
    for el in soup.select('[href], [src]'):
        link=el.get('href',el.get('src','')); u=urlsplit(link)
        if u.scheme or u.netloc: continue
        target=(ROOT/name).parent/unquote(u.path) if u.path else ROOT/name
        assert target.exists(),(name,link)
        if u.fragment and target.suffix=='.html':
            assert BeautifulSoup(target.read_text(),'html.parser').find(id=unquote(u.fragment)),(name,link)
index=BeautifulSoup((ROOT/'index.html').read_text(),'html.parser')
old=BeautifulSoup(subprocess.check_output(['git','show','HEAD:index.html'],cwd=ROOT).decode(),'html.parser')
oldlinks={x['href'] for x in old.select('a.index-card')} - {'./'+PAGE}
newlinks=[x['href'] for x in index.select('a.index-card')]
assert len(newlinks)==len(oldlinks)+1
assert set(newlinks)-oldlinks=={'./'+PAGE}
assert oldlinks-set(newlinks)==set()
assert len(newlinks)==len(set(newlinks))
soup=BeautifulSoup((ROOT/PAGE).read_text(),'html.parser')
assert len(soup.select('#merchants .district'))==7, 'Expected seven grouped dining areas including Shunyi Western options'
assert len(soup.select('.merchant'))>=16, 'Expected expanded dining options'
data=json.loads((ROOT/'data/wenyu-dining-districts.json').read_text())
assert len(soup.select('.merchant'))==data['candidate_count']
assert {c['id'] for c in data['candidates']}=={x['id'] for x in soup.select('.merchant')}
assert {'wanjiangyan','beipingshengshi','chunhejingming'}.issubset({x['id'] for x in soup.select('.merchant')})
for d in data['districts']:
    group=soup.find(id='district-'+d['id'])
    assert len(group.select('.merchant'))==len(d['candidate_ids'])
    for c in d['candidate_ids']:
        assert group.find(id=c),c
assert len(soup.select('#schedule tbody tr'))==9
for phrase in ['Bellota','安酷','MEAT by Ernest','ParkSide','弗萨塔可','罗马湖9号','Trip.com','沈家闸','沙子营闸','粉色段','往返约10km','野餐垫','水果','零食','自带桌游','分时段开放机动车','具体园名','未知','非GPS轨迹','皖江宴','北平盛世','10:30','15:30—16:45','索引']:
    assert phrase in soup.get_text(),phrase
for selector in ['header','#route','#schedule']:
    section_text=soup.select_one(selector).get_text()
    assert '沙子营闸' in section_text, (selector,'missing corrected endpoint')
    assert '沙子营南路' not in section_text and '京密路方向' not in section_text
assert soup.select_one('#map img[src="../assets/wenyu-cycling/user-pink-route.webp"]')
assert '沈家闸—沙子营闸' in index.select_one(f'a.index-card[href="./{PAGE}"]').get_text()
assert len(soup.select('#greenway-photos img'))==3, 'Expected sourced greenway photo gallery'
photo_sets=[json.loads((ROOT/f'data/{name}').read_text()) for name in ['wenyu-western-photos.json','wenyu-original-photos.json']]
photo_entries=[entry for batch in photo_sets for entry in batch]
restaurant_ids={cid for d in data['districts'] for cid in d['candidate_ids']}
assert {entry['id'] for entry in photo_entries}==restaurant_ids
for entry in photo_entries:
    merchant=soup.find(id=entry['id'])
    assert len(merchant.select('.merchant-photos img'))==len(entry['images']),entry['id']
    if not entry['images']:
        assert merchant.select_one('.photo-missing'),entry['id']
    for photo in entry['images']:
        assert (ROOT/photo['path']).exists()
        assert photo['source_url'].startswith('http') and photo['verified_branch'],entry['id']
        assert merchant.select_one(f'img[src="../{photo["path"]}"]'),entry['id']
assert len(soup.select('#greenway-photos img'))==3
for fig in soup.select('.merchant-photos figure, #greenway-photos figure'):
    assert fig.select_one('figcaption a[href]'), 'Missing photo source link'
class Quiet(SimpleHTTPRequestHandler):
    def log_message(self,format,*args):pass
server=ThreadingHTTPServer(('127.0.0.1',0),partial(Quiet,directory=str(ROOT)))
Thread(target=server.serve_forever,daemon=True).start()
base=sys.argv[1].rstrip('/') if len(sys.argv)>1 else f'http://127.0.0.1:{server.server_port}'
results=[]
with sync_playwright() as p:
    browser=p.chromium.launch()
    for width in [390,1440]:
        tab=browser.new_page(viewport={'width':width,'height':950},device_scale_factor=1)
        errors=[];tab.on('pageerror',lambda exc:errors.append(str(exc)))
        r=tab.goto(base+'/'+PAGE,wait_until='networkidle');assert r.status==200
        tab.locator('#map').scroll_into_view_if_needed()
        tab.locator('#merchants').scroll_into_view_if_needed()
        tab.wait_for_function('Array.from(document.images).every(i=>i.complete&&i.naturalWidth>0)')
        checks=tab.evaluate('''() => ({width:innerWidth,scroll:document.documentElement.scrollWidth,images:Array.from(document.images).map(i=>({src:i.getAttribute('src'),ok:i.complete&&i.naturalWidth>0,ratio:Math.abs(i.height/i.width-i.naturalHeight/i.naturalWidth)<.015}))})''')
        assert checks['scroll']<=width,checks
        assert all(i['ok'] and i['ratio'] for i in checks['images']),checks
        tab.locator('header a[href="#lunch"]').click();assert tab.evaluate('location.hash')=='#lunch'
        tab.locator('#lunch a[href="#wanjiangyan"]').click();assert tab.evaluate('location.hash')=='#wanjiangyan'
        tab.locator('header a[href="#rest"]').click();assert tab.evaluate('location.hash')=='#rest'
        assert tab.locator('.merchant').count()==data['candidate_count']
        assert tab.locator('#merchants .district').count()==7
        assert '10:30—11:30' in tab.locator('#schedule').inner_text()
        assert '15:30—16:45' in tab.locator('#schedule').inner_text()
        assert '沈家闸' in tab.locator('#route').inner_text()
        assert 'P20首选' not in tab.locator('header').inner_text()
        assert '08:30' not in tab.locator('body').inner_text()
        assert not errors,errors
        tab.goto(base+'/'+PAGE,wait_until='networkidle')
        tab.screenshot(path=f'/tmp/wenyu-{width}.png',full_page=True)
        tab.locator('#greenway-photos').screenshot(path=f'/tmp/wenyu-greenway-{width}.png')
        tab.locator('#bellota').screenshot(path=f'/tmp/wenyu-bellota-{width}.png')
        results.append(checks)
        tab.goto(base+'/index.html',wait_until='networkidle')
        card=tab.locator(f'a.index-card[href="./{PAGE}"]');assert card.count()==1
        assert card.locator('img').evaluate('(i)=>i.complete&&i.naturalWidth>0')
        assert tab.evaluate('document.documentElement.scrollWidth<=innerWidth')
        tab.close()
    browser.close()
server.shutdown()
print(json.dumps({'status':'PASS','base':base,'unique_home_cards':len(newlinks),'old_home_cards_preserved':len(oldlinks),'merchant_count':data['candidate_count'],'schedule_rows':9,'viewport_checks':results},ensure_ascii=False))
