"""Build the static Hokkaido plan, with a task-local source ledger."""
import hashlib, html, json, re, subprocess, sys
from pathlib import Path
import markdown
from bs4 import BeautifulSoup
ROOT=Path(__file__).resolve().parents[1]
DATA=ROOT/'data'
REL='pages/spring-festival-2027-hokkaido-ski-onsen.html'
SOURCES=Path.home()/'.hermes/skills/research/grounded-citations/scripts/sources.py'
LEDGER=DATA/'hokkaido-2027-citations.json'
skis=json.loads((DATA/'hokkaido-2027-ski-research.json').read_text())
urls={x['id']:x['url'] for x in skis['sources']}
for a,b in {'rhythm':'rhythm-five','fss-rental':'fss-rentalski'}.items(): urls[a]=urls[b]
urls.update({
'calendar':'https://www.hko.gov.hk/en/Observatorys-Blog/109092/No-Lunar-New-Year%E2%80%99s-Eve-on-the-30th-Day-for-Five-Consecutive-Years',
'snowfes':'https://www.snowfes.com/news/948.html',
'jma-sapporo':'https://www.data.jma.go.jp/stats/etrn/view/nml_sfc_ym.php?prec_no=14&block_no=47412&year=&month=&day=&view=',
'jma-asahikawa':'https://www.data.jma.go.jp/stats/etrn/view/nml_sfc_ym.php?prec_no=12&block_no=47407&year=&month=&day=&view=',
'jma-kutchan':'https://www.data.jma.go.jp/stats/etrn/view/nml_sfc_ym.php?prec_no=16&block_no=47433&year=&month=&day=&view=',
'kotobuki':'https://rusutsu.com/en/onsen-wellness/kotobukinoyu',
'rusutsu-snowshoe':'https://rusutsu.com/en/winter-activities/nature-tour-w/',
'pool':'https://rusutsu.com/en/onsen-wellness/indoor-pool=',
'mori':'https://www.princehotels.com/shinfurano/restaurants/mori-no-tokei-forest-clock-cafe/',
'ningle':'https://www.princehotels.com/shinfurano/facilities/ningle-terrace-shop/',
'shisai':'https://www.princehotels.com/shinfurano/facilities/furano-hot-spring/',
'biei':'https://www.biei-hokkaido.jp/ja/27188',
'road1':'https://www.biei-hokkaido.jp/ja/27178',
'road2':'https://www.biei-hokkaido.jp/ja/27142',
'zoo':'https://www.city.asahikawa.hokkaido.jp/asahiyamazoo/event/event.html',
'adc':'https://asahikawa-kagu.or.jp/',
'hanazono-snowshoe':'https://hanazononiseko.com/en/winter/activities/snowshoe-tour',
'diamond':'https://hanazononiseko.com/en/winter/activities/snowshoe-tour-dx',
'hirafutei':'http://hirafutei.info/hotspring/',
'toyako':'http://www.toyako-vc.jp/',
'noboribetsu':'https://noboribetsu-spa.jp/spot/spot0055/',
'bigruns':'https://rusutsu.com/en/access-shuttle-bus-new-chitose-airport',
'liner':'https://www.access-n.jp/winter2026/en/skibus/detail/101chitose_rusutsu_niseko.html',
'crossresort':'https://www.access-n.jp/winter2026/en/skibus/detail/furano_rusutsu_niseko.html',
'lavender':'https://furanobus.jp/lavender/index.html',
'license':'https://www.police.pref.hokkaido.lg.jp/guide/menkyo/gai_menkyo-kirikae.html',
'winterdrive':'https://hokkaido-safe-travel.mlit.go.jp/images/pdf/winter_drive_eng.pdf',
})
raw=(DATA/'hokkaido-2027-plan.md').read_text()
rechecks=json.loads((DATA/'hokkaido-2027-official-recheck.json').read_text())
retrieved={x['url']:x for x in rechecks}
def ledger(*args):
    return subprocess.check_output([sys.executable,str(SOURCES),'--ledger',str(LEDGER),*args],text=True)
for key in dict.fromkeys(re.findall(r'\[@([\w-]+)\]',raw)):
    url=urls[key]
    assert url in retrieved,url
    title=retrieved[url].get('title') or key
    result=ledger('add',url,'--title',title)
    n=int(re.search(r'\[(\d+)\]',result).group(1))
    raw=raw.replace(f'[@{key}]',f'[{n}]')
assert '[@' not in raw
(DATA/'hokkaido-2027-plan.md').write_text(raw)
ledger('render','--replace-in',str(DATA/'hokkaido-2027-plan.md'))
ledger('verify',str(DATA/'hokkaido-2027-plan.md'))
raw=(DATA/'hokkaido-2027-plan.md').read_text()
# Use a hash of the actual task content, not a guessed git revision.
revision=hashlib.sha256(raw.encode()).hexdigest()[:16]
body=markdown.markdown(raw,extensions=['tables','attr_list','fenced_code'])
soup=BeautifulSoup(body,'html.parser')
# Link inline citation numbers to the mechanically rendered Sources block.
source_heading=next(x for x in soup.find_all('h2') if x.get_text(strip=True)=='Sources')
source_heading['id']='sources'
source_links={}
# The ledger's default Markdown format is plain [n] URL lines, not a list.
for sibling in list(source_heading.next_siblings): sibling.extract()
source_list=soup.new_tag('ul'); source_heading.insert_after(source_list)
for rec in json.loads(LEDGER.read_text())['sources']:
    n=str(rec['id']); li=soup.new_tag('li',id='source-'+n)
    link=soup.new_tag('a',href=rec['url']); link.string=f"[{n}] {rec.get('title') or rec['url']}"
    li.append(link); source_list.append(li);source_links[n]=rec['url']
for node in list(soup.find_all(string=re.compile(r'\[\d+\]'))):
    if node.parent.name=='a' or node.find_parent('li') and node.find_parent('li').get('id','').startswith('source-'): continue
    escaped=html.escape(str(node))
    linked=re.sub(r'\[(\d+)\]',lambda m:f'<sup><a href="#source-{m.group(1)}" aria-label="来源{m.group(1)}">[{m.group(1)}]</a></sup>',escaped)
    node.replace_with(BeautifulSoup(linked,'html.parser'))
# Put each main section in a flat panel, not nested cards.
sections=[]; current=None
for el in list(soup.contents):
    if getattr(el,'name',None)=='h1': continue
    if getattr(el,'name',None)=='h2':
        current=soup.new_tag('section',attrs={'class':'panel'})
        if el.get('id'): current['id']=el['id']; del el['id']
        sections.append(current)
    if current is None:
        current=soup.new_tag('section',attrs={'class':'panel intro'});sections.append(current)
    current.append(el)
for table in soup.find_all('table'): pass # tables moved to section fragments below
for section in sections:
    for table in list(section.find_all('table')):
        hint=soup.new_tag('p',attrs={'class':'table-hint'});hint.string='↔ 手机端可在表格内左右滑动查看全部列。'
        table.insert_before(hint)
        wrap=soup.new_tag('div',attrs={'class':'table-wrap','tabindex':'0','role':'region','aria-label':section.h2.get_text() if section.h2 else '行程摘要'})
        table.wrap(wrap)
    for a in section.select('a[href^="http"]'): a['rel']='noopener noreferrer'
css='''*{box-sizing:border-box}html{scroll-behavior:smooth;scroll-padding-top:18px}body{margin:0;background:#f0f3f3;color:#203038;font:16px/1.85 system-ui,-apple-system,"Microsoft YaHei",sans-serif}main{max-width:1140px;margin:auto;padding:24px}a{color:#185966;text-underline-offset:3px;overflow-wrap:anywhere}nav{font-size:14px;margin:0 0 18px;display:flex;flex-wrap:wrap;gap:10px 20px}.hero{background:#17343f;color:#fff;border-radius:24px;padding:38px;display:grid;grid-template-columns:1.1fr 1fr;gap:32px;align-items:center}.hero h1{font-size:clamp(29px,4vw,47px);line-height:1.3;margin:10px 0 20px}.hero p{color:#d4e7e8}.hero img{width:100%;height:auto;display:block;border-radius:14px}.hero a{color:#d8e4d9}figure{margin:0}figcaption{font-size:12px;line-height:1.6;color:#637980;margin:8px 0}.hero figcaption{color:#d4e7e8}.eyebrow{font-size:12px;letter-spacing:.14em;color:#94c3c8}.gallery{margin-top:20px;display:grid;grid-template-columns:1fr 1fr;align-items:center;gap:24px}.gallery img{width:100%;height:auto;border-radius:16px;display:block}.gallery p{margin:8px 0}.panel{background:#fff;border:1px solid #dce4e4;border-radius:20px;padding:28px;margin:20px 0;min-width:0}.panel h2{margin:0 0 18px;font-size:25px;line-height:1.45}.panel h3{font-size:19px;margin:28px 0 12px}p{margin:13px 0}strong{color:#9c4e28}.hero strong{color:#fff}.toc{background:#e0ebeb;border-radius:16px;padding:18px 22px;margin:20px 0}.toc a{display:inline-block;margin:4px 18px 4px 0;font-weight:600}.table-wrap{overflow-x:auto;max-width:100%;border:1px solid #dce4e4;border-radius:10px}table{border-collapse:collapse;width:100%;min-width:710px;font-size:14px;line-height:1.75}th,td{text-align:left;border-bottom:1px solid #e1e7e7;padding:14px 13px;vertical-align:top}th{background:#e7efee}td:first-child{font-weight:600;min-width:120px}tr:last-child td{border:0}#schools table{min-width:1030px}#equipment table{min-width:900px}#itinerary table{min-width:850px}sup{font-size:11px;white-space:nowrap}blockquote{margin:18px 0;padding:16px 22px;background:#eef4f3;border-left:3px solid #69a09d;font-size:14px}li{margin:8px 0}#sources{font-size:13px}#sources li{margin:10px 0}footer{font-size:12px;color:#536d75;overflow-wrap:anywhere;padding:12px}.notice{padding:12px 18px;background:#fff4df;border-left:4px solid #b97b37;border-radius:5px;font-size:14px}@media(max-width:700px){main{padding:14px}.hero{display:block;padding:24px}.hero figure{margin-top:20px}.panel{padding:20px 16px;border-radius:16px}.panel h2{font-size:22px}.gallery{display:block}.gallery figure{margin-bottom:12px}.toc{padding:14px}table{font-size:13px}th,td{padding:10px}ul,ol{padding-left:23px}}'''
head=f'''<!doctype html><html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>2027北海道春节滑雪温泉 · 毛豆训练与父母冬假 · Beijing Vibe Trip</title><meta name="description" content="10–14天北海道家庭滑雪温泉：8家儿童训练选项、官方当季课费与器材，家长只滑2–3次，12天行程和10/14天改法。非实时余位。"><meta name="plan-revision" content="{revision}"><style>{css}</style></head><body><main><nav><a href="../index.html">← Beijing Vibe Trip 首页</a><span>2027春节特别 · 资料2026-10-26</span></nav><header class="hero"><div><span class="eyebrow">HOKKAIDO / SNOW & SLOW</span><h1>孩子练技术，<br>家长过冬假。</h1><p>北海道 10–14 天 · 滑雪 × 温泉<br>父母滑 2 天，可选第 3 天；其它日子不再陪滑耗全天。</p><p>先核课程，再选同区住宿。<br>留寿都主案 / 富良野与二世古备选</p><small>公开资料研究，不是已订产品或库存保证。</small></div><figure><img src="../assets/hokkaido-2027/winter.webp" width="748" height="451" alt="留寿都官网冬季滑雪宣传照片" loading="eager"><figcaption><a href="https://rusutsu.com/en/rusutsu-in-winter/">留寿都官网冬季照片</a> · 氛围参考，不代表儿童上课地点或目标日雪况。</figcaption></figure></header><div class="gallery"><figure><img src="../assets/hokkaido-2027/onsen.webp" width="1440" height="620" alt="留寿都官网雪景露天温泉宣传照片" loading="eager"><figcaption><a href="https://rusutsu.com/en/onsen-wellness/">留寿都官网温泉照片</a> · 不据图认定具体酒店套餐包含。</figcaption></figure><div><p class="eyebrow">ONE BASE, THEN TRAVEL</p><h2>先连续住，<br>再离开雪场旅行。</h2><p>6晚训练基地＋2晚温泉＋3晚札幌。送课日留近场，家庭日再去湖边、雪祭与城市。</p><div class="notice">真实当季价、旧价与混价分开列；不把全天看护时长当净训练时长。</div></div></div><nav class="toc" aria-label="专题目录">'''
for anchor,label in [('decision','选基地'),('schools','课程与专业性'),('equipment','设备与费用'),('parents','家长非滑雪活动'),('itinerary','12天行程'),('logistics','住宿交通'),('next','询价清单'),('sources','原始来源')]: head+=f'<a href="#{anchor}">{label}</a>'
head+='</nav>'
output=head+''.join(str(s) for s in sections)+f'<footer>内容修订 <code id="plan-revision">{revision}</code> · 官方页可变；2026-10-26核验，不承诺余位。<br><a href="../index.html">返回普通路线卡片流</a></footer></main></body></html>'
(ROOT/REL).write_text(output)
print(json.dumps({'page':REL,'content_revision':revision,'cited_sources':len(source_links),'bytes':len(output.encode())},ensure_ascii=False))
