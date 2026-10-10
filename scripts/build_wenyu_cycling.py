"""Build the sourced Wenyu day-trip page; no live prices or GPS inferred."""
from pathlib import Path
import json
from html import escape as e
from urllib.parse import quote
ROOT = Path(__file__).resolve().parents[1]
data = json.loads((ROOT/'data/wenyu-dining-districts.json').read_text())
assert data['candidate_count'] == len(data['candidates'])
assert len({x['id'] for x in data['candidates']}) == data['candidate_count']
assert len(data['districts']) == 7
OFFICIAL='https://www.beijing.gov.cn/fuwu/bmfw/sy/jrts/202608/t20260820_4830458.html'
REPORT='https://xinwen.bjd.com.cn/content/s6a86ac84e4b0e45f3fd6436a.html'
def nav(name):
    return 'https://uri.amap.com/search?keyword='+quote(name)+'&city=北京&view=map'
def button(name,label=None):
    return f'<a class="action" href="{e(nav(name))}" target="_blank" rel="noopener">{e(label or name)} ↗</a>'
photo_entries=[]
for name in ['wenyu-western-photos.json','wenyu-original-photos.json']:
    photo_entries.extend(json.loads((ROOT/'data'/name).read_text()))
photos_by_id={entry['id']:entry for entry in photo_entries}
def photo_figure(photo):
    return f'<figure><a href="../{e(photo["path"])}" target="_blank" rel="noopener"><img src="../{e(photo["path"])}" width="{photo["width"]}" height="{photo["height"]}" alt="{e(photo["caption"])}" decoding="async"></a><figcaption>{e(photo["caption"])} · <a href="{e(photo["source_url"])}" target="_blank" rel="noopener">图片来源</a>（{e(photo.get("source_date") or "日期未知")}）</figcaption></figure>'
def merchant_photos(id):
    entry=photos_by_id[id]
    if not entry['images']:
        return '<p class="photo-missing note">暂无已核实的本分店实拍；不以品牌海报或其它分店图代替。</p>'
    return '<div class="merchant-photos">'+''.join(photo_figure(photo) for photo in entry['images'])+'</div>'
greenway=json.loads((ROOT/'data/wenyu-greenway-photos.json').read_text())
greenway_photos='<section id="greenway-photos"><h2>🌳 先看看绿道的样子</h2><p class="note">以下为北京日报2026-09-23清河—温榆河滨水绿道报道实景图。未逐张定位到沈家闸—沙子营闸粉色段，作为区域环境参考；不代表全程无车或当前路况。点击图片可看大图。</p><div class="photo-grid">'+''.join(photo_figure(photo) for photo in greenway if photo['id']!='greenway-1')+'</div></section>'
cards=[]
for c in data['candidates']:
    id=c['id']
    photo_html=merchant_photos(id) if c.get('district_id') else ''
    sources=' · '.join(f'<a href="{e(s["url"])}" target="_blank" rel="noopener">{e(s["publisher"])}</a>（{e(s["source_date"])}；索引抓取 {e(s["crawled_at"])}）' for s in c['sources'])
    cards.append(f'''<article class="merchant" id="{id}">
<h3>{e(c['name'])}</h3><p class="orange">{e(c['role'])}</p>
<p><strong>{e(c['rating'])}</strong> · 人均：{e(c['average_cost_per_person'])}</p>
<p class="alert">{e(c['rank'])}</p>{photo_html}<dl><dt>地址</dt><dd>{e(c['address'])}</dd><dt>营业参考</dt><dd>{e(c['opening_hours'])}</dd><dt>吃什么 / 休息</dt><dd>{e('、'.join(c['menu_evidence']))}。{e(c['family_use'])}</dd><dt>空间与停车</dt><dd>{e(c['indoor_seating'])}；{e(c['parking'])}</dd><dt>和骑行区的关系</dt><dd>{e(c['gate_and_parking_relation'])}</dd><dt>用前确认</dt><dd>{e(c['priority'])}。当天营业、座位和实际车程未核；不宣称到店几分钟。</dd></dl>
<a class="action" href="{e(c['sources'][0]['url'])}" target="_blank" rel="noopener">来源原页 ↗</a>{button(c['name'],'地图搜店（核对地址）')}<p class="source">证据：{sources}</p></article>''')
cardmap = dict(zip([c['id'] for c in data['candidates']], cards))
groups=[]
choices=[]
for d in data['districts']:
    names=' / '.join(f'<a href="#{cid}">{e(next(c["name"] for c in data["candidates"] if c["id"]==cid))}</a>' for cid in d['candidate_ids'])
    refs=' · '.join(f'<a href="{e(s["url"])}">位置/停车来源</a>（{e(s["source_date"])}）' for s in d['sources'])
    groups.append(f'<div class="district" id="district-{d["id"]}"><h3>{e(d["name"])}</h3><p>{e(d["route_note"])}</p><p><strong>落点：</strong>{e(d["anchor"])} · {e(d["address"])}</p><p><strong>停车：</strong>{e(d["parking"])}</p>{button(d["anchor"],"地图搜落点（核对入口）")}<p class="source">{refs}</p>'+''.join(cardmap[cid] for cid in d['candidate_ids'])+'</div>')
    choices.append(f'<tr><td><a href="#district-{d["id"]}"><strong>{e(d["name"])}</strong></a></td><td>{names}</td><td>{e(d["decision"])}</td></tr>')
groups.append('<details><summary>历史茶咖备选（不纳入本次下午安排）</summary>'+cardmap['chunhejingming']+'</details>')
lunch='<section id="lunch"><h2>🍽️ 先选午餐目的地：西餐也认真选</h2><p><strong>一天只去一个商圈、一家餐厅。</strong>新增顺义中央别墅区、同里市集、祥云小镇与罗马湖6家特色西餐；原有奥森、北苑、来广营10家餐厅保留。吃完再自驾到沈家闸，不让孩子骑公共道路去餐厅。</p><table><thead><tr><th>商圈落点</th><th>分店选项</th><th>怎么选</th></tr></thead><tbody>'+''.join(choices)+'</tbody></table><p class="alert"><strong>'+e(data['shortlist'])+'</strong>。罗马湖是目的型绕行，不冒称顺路；导航预估挤占下午，就改选更靠前的午餐节点。没有实测绕行公里数或分钟数。</p><p class="note">新增西餐按特色、菜单、位置和明确标注的平台口碑筛选，未取得点评实时分数的店不挂头部榜。Trip.com少量评论的高分不能等同稳定口碑。原中餐8家有点评评分或细分类榜依据、2家特色待核；缓存均不是当天营业确认。</p></section>'
activities=[
(60,'五道口 → 选定午餐店','10:30左右出发；60分钟含停车只是预算。顺义目的地以导航为准，晚出发就选近点或缩短后续骑行。'),
(90,'午餐／早午餐','安酷、Bellota、MEAT、庭院西餐或原有中餐择一；预约、出餐时长提前问，不串商圈。'),
(45,'饭后驾车 → 沈家闸附近合法停车点','45分钟仅作接驳预算；不把沈家闸本身视为停车场，泊位与入口尚待核实。'),
(15,'卸车、如厕、核对通行标识','确认可供儿童骑行的隔离非公共道路空间；不能确认则不按原10km计划骑。'),
(75,'沈家闸 → 沙子营闸（粉色段）→ 原路返回','沿用户截图两闸间的粉色段往返；约10km沿用此前计划目标，未核GPS，不为了凑里程延长。'),
(15,'收车、转入周边新公园休息区','具体园名和入口待定；确认可铺垫，必要时先装车再短途自驾，不安排孩子骑公路接驳。'),
(75,'野餐垫＋水果零食＋自带桌游','15:30—16:45以休息为主；UNO、磁吸棋任选，不再为下午茶专程找咖啡店。'),
(15,'收垫、装车、垃圾带走','提前收拾，不临近天黑才回头找车。'),
(60,'返回五道口','约18:00是弹性规划；以光线、天气和实时路况提前返程。')]
rows=[]
minute=10*60+30
for duration,title,detail in activities:
    finish=minute+duration
    rows.append((f'{minute//60:02d}:{minute%60:02d}—{finish//60:02d}:{finish%60:02d}',duration,title,detail))
    minute=finish
assert sum(x[1] for x in rows)==450 and minute==18*60
schedule=''.join(f'<tr><td>{a}<br><small>{b/60:.2f}h</small></td><td><strong>{c}</strong></td><td>{d}</td></tr>' for a,b,c,d in rows)
page=(ROOT/'templates/wenyu-cycling.html').read_text()
page=page.replace('GREENWAY_PHOTOS',greenway_photos).replace('\nLUNCH\n',lunch).replace('NAVPARK',button('北京 沈家闸','地图检索：沈家闸（非停车定位）')).replace('SCHEDULE',schedule).replace('CARDS',''.join(groups)).replace('ROUTE_SOURCE','https://xinwen.bjd.com.cn/content/s6ab3cabae4b0e42f8f00ba4f.html?innerId=1').replace('REPORT',REPORT)
out=ROOT/'pages/wenyu-cycling-wudaokou.html'
out.write_text(page,encoding='utf-8')
print(json.dumps({'page':str(out),'merchant_count':len(cards),'schedule_minutes':sum(x[1] for x in rows)},ensure_ascii=False))
