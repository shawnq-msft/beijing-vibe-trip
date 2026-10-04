"""Build the source-linked 2026 Beijing National Day family guide."""
import html
import json
from pathlib import Path
from urllib.parse import quote

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / 'data/national-day-2026-ranked.json'
OUTPUT = ROOT / 'pages/national-day-2026-family-events.html'
e = html.escape

def build():
    data = json.loads(DATA.read_text())
    items = sorted(data['activities'], key=lambda a: a['rank'])
    assert len(items) == len({a['id'] for a in items}) == 10
    assert [a['rank'] for a in items] == list(range(1, 11))
    rows, cards = [], []
    for a in items:
        days = ' '.join(map(str, a['dates']))
        rows.append(f'<tr data-days="{days}" data-type="{a["type"]}"><td>{a["rank"]:02}</td><td><a href="#{a["id"]}">{e(a["name"])}</a><small>{e(a["area"])}</small></td><td>{e(a["full_dates"])}</td><td>{e(a["duration"])}</td></tr>')
        image = ''
        if a.get('image'):
            image = f'<figure><img src="../assets/national-day-2026/{a["image"]}" width="{a["image_width"]}" height="{a["image_height"]}" alt="{e(a["image_caption"])}" loading="eager"><figcaption>{e(a["image_caption"])}</figcaption></figure>'
        fields = ''.join(f'<dt>{label}</dt><dd>{e(a[key])}</dd>' for label,key in [('时间','hours'),('费用边界','price'),('预约路径','booking'),('带老人','elder'),('建议玩法','plan')])
        sources = ''.join(f'<a href="{e(s["url"],quote=True)}" target="_blank" rel="noopener noreferrer">{e(s["label"])}</a>' for s in a['sources'])
        nav = 'https://uri.amap.com/search?keyword=' + quote(a['navigation']) + '&city=' + quote('北京') + '&callnative=0'
        cards.append(f'''<article id="{a['id']}" class="event" data-days="{days}" data-type="{a['type']}">
<div class="event-title"><span class="rank">{a['rank']:02}</span><div><p class="eyebrow">{e(a['area'])} · {e(a['duration'])}</p><h2>{e(a['name'])}</h2></div></div>
<p class="date-line">{e(a['full_dates'])}</p><p class="why">{e(a['why'])}</p>
<div class="event-body{' with-image' if image else ''}"><div><p>{e(a['intro'])}</p><dl>{fields}</dl></div>{image}</div>
<p class="warning"><b>临出发前：</b>{e(a['risk'])}</p><p class="evidence">证据状态：{e(a['evidence'])}</p>
<div class="sources">{sources}<a href="{e(nav,quote=True)}" target="_blank" rel="noopener noreferrer">高德地点搜索（非实测路线）↗</a></div></article>''')
    page = '''<!doctype html>
<html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>2026北京国庆家庭活动 Top 10 · Beijing Vibe Trip</title>
<meta name="description" content="按10岁孩子的科学、地质、网球兴趣排序，兼顾老人；附国庆活动日期、预约、费用边界与原始来源。">
<style>
:root{--paper:#f5f2eb;--ink:#242e2a;--muted:#626c62;--accent:#b34d2c;--line:#dfded3;--green:#31574a}*{box-sizing:border-box}html{scroll-behavior:smooth}body{margin:0;background:var(--paper);color:var(--ink);font:16px/1.8 system-ui,-apple-system,'Segoe UI','Microsoft YaHei',sans-serif}a{color:var(--green);text-underline-offset:3px;overflow-wrap:anywhere}main{max-width:1120px;margin:auto;padding:24px}nav{font-size:14px;margin-bottom:20px}.hero{background:#203f35;color:#fff;border-radius:24px;padding:40px;display:grid;grid-template-columns:1.6fr 1fr;gap:28px;align-items:center}.hero .eyebrow{color:#d7c18c}.hero h1{font-size:clamp(28px,4vw,48px);line-height:1.25;margin:12px 0 18px}.hero p{color:#e1e8e0}.hero img{display:block;width:100%;height:auto;border-radius:12px}.hero small{color:#ccd8cf;font-size:12px}.eyebrow{font-size:12px;letter-spacing:.08em;color:var(--muted);margin:0}.picks{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:14px;margin:20px 0}.pick{background:#fff;border:1px solid var(--line);padding:20px;border-radius:16px}.pick b{display:block;color:var(--accent)}.pick p{margin:7px 0;font-size:14px}.notice{border-left:4px solid #ca9950;padding:12px 20px;background:#fff5dd;font-size:14px;margin:20px 0}.panel,.event{background:#fff;border:1px solid var(--line);padding:28px;border-radius:18px;margin:20px 0}.panel h2{margin-top:0}.controls{display:flex;flex-wrap:wrap;gap:16px;align-items:center;margin:18px 0}select{font:inherit;border:1px solid var(--line);padding:6px 9px;border-radius:8px;background:white;color:var(--ink);max-width:100%}#count{color:var(--muted);font-size:14px}.table-wrap{overflow-x:auto}table{border-collapse:collapse;width:100%;font-size:14px}th,td{text-align:left;border-bottom:1px solid var(--line);padding:12px 10px;vertical-align:top}td:first-child{font-weight:bold;color:var(--accent)}td small{display:block;color:var(--muted)}.event{scroll-margin-top:16px}.event-title{display:flex;gap:16px;align-items:center}.event-title h2{margin:3px 0;font-size:24px;line-height:1.4}.rank{font-size:34px;font-weight:800;line-height:1;color:var(--accent)}.date-line{color:var(--accent);font-size:14px;margin:12px 0}.why{font-size:18px;font-weight:600;color:var(--green)}.event-body.with-image{display:grid;grid-template-columns:minmax(0,1.8fr) minmax(0,1fr);gap:25px;align-items:start}.event-body p{margin-top:0}figure{margin:0}figure img{width:100%;height:auto;display:block;border-radius:12px}figcaption{font-size:12px;color:var(--muted);padding-top:7px}dl{display:grid;grid-template-columns:80px minmax(0,1fr);gap:12px 16px;font-size:14px}dt{font-weight:700;color:var(--green)}dd{margin:0}.warning{background:#faf3e7;padding:14px;border-radius:10px;font-size:14px}.evidence{font-size:12px;color:var(--muted)}.sources{display:flex;flex-wrap:wrap;gap:8px 18px;font-size:13px}.calendar{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:18px}.calendar h3{margin:0;color:var(--accent)}.calendar p{font-size:14px}footer{color:var(--muted);font-size:13px;padding:15px 0 30px}[hidden]{display:none!important}@media(max-width:760px){main{padding:14px}.hero{padding:24px;grid-template-columns:1fr}.hero figure{max-width:400px}.picks{grid-template-columns:1fr;gap:10px}.pick{padding:15px}.panel,.event{padding:19px}.event-title h2{font-size:21px}.event-body.with-image{grid-template-columns:1fr}.event-body figure{max-width:450px}dl{grid-template-columns:1fr;gap:2px}dd{margin-bottom:10px}.calendar{grid-template-columns:repeat(2,minmax(0,1fr))}.why{font-size:16px}th,td{padding:9px 7px;font-size:12px}.rank{font-size:28px}.controls{gap:10px}.event-title{align-items:flex-start}}@media(prefers-reduced-motion:reduce){html{scroll-behavior:auto}}
</style></head><body><main>
<nav><a href="../index.html">← Beijing Vibe Trip 首页</a> / 国庆特别</nav>
<header class="hero"><div><p class="eyebrow">BEIJING · NATIONAL DAY 2026</p><h1>把假期留给<br>真正想玩的事。</h1><p>北京国庆家庭活动 Top 10<br>矿物化石、科学动手、网球现场，外加一段秋日松弛。</p><small>资料更新：2026-10-04（北京时间）<br>覆盖10/1—7，重点标出10/4—7仍可规划的活动；不是实时余票页。</small></div><figure><img src="../assets/national-day-2026/astro-night.webp" width="1200" height="799" alt="亲子夜间天文观测活动配图"><figcaption><a style="color:#dbe7d7" href="https://m.bjnews.com.cn/detail/1790769625129417.html">新京报9/30夜宿报道配图 · 受访者供图</a></figcaption></figure></header>
<section class="picks" aria-label="快速选择"><div class="pick"><b>孩子兴趣优先</b><p><a href="#geology">地质博物馆</a> / <a href="#science">中国科技馆</a><br>矿物、化石、机械与实验，先查动手课名额。</p></div><div class="pick"><b>限定窗口优先</b><p><a href="#tennis">中网男单后段</a> / <a href="#opera">园博园戏曲周</a><br>男单决赛计划10/6；戏曲周10/5结束。</p></div><div class="pick"><b>带老人轻松一点</b><p><a href="#opera">园博园一个展园＋市集</a><br>或<a href="#rice">上庄小舞台</a>短停，不刷全园、不熬整晚。</p></div></section>
<div class="notice"><b>先看边界：</b>排名是面向约10岁孩子、兼顾老人同行的编辑建议，不是大众点评分。活动确认≠有余位；互动免费≠馆票/夜宿/餐饮全免费。未代订任何门票。时间、天气、临时限流均需出发前复核。</div>
<section class="panel"><h2>先选日期，再挑兴趣</h2><p style="font-size:14px;color:var(--muted)">RANKING_BASIS</p><div class="controls"><label>日期 <select id="day"><option value="all">10/4—7全部</option><option value="4">10月4日</option><option value="5">10月5日</option><option value="6">10月6日</option><option value="7">10月7日</option></select></label><label>类型 <select id="kind"><option value="all">全部类型</option><option value="indoor">室内为主</option><option value="outdoor">户外秋日</option><option value="sport">网球现场</option></select></label><span id="count" role="status" aria-live="polite">共10项</span></div><p style="font-size:12px;color:var(--muted)">筛选保留的是该日仍在活动周期的地点，不保证当天每个子项目都开放；汽车嘉年华含户外区。</p><div class="table-wrap"><table><thead><tr><th>推荐序</th><th>活动</th><th>完整活动窗口</th><th>建议停留</th></tr></thead><tbody>ROWS</tbody></table></div></section>
<section class="panel"><h2>剩余假期怎么排？每天只挑一个主活动</h2><p>下面是可替换建议，不是已预订行程。若要看中网，优先服从实际买到的场次。</p><div class="calendar"><div><h3>10/4 · 周日</h3><p>科技：天文馆月球车手作。<br>网球迷：先查钻石夜场余票。<br>不约票：上庄小舞台备选。</p></div><div><h3>10/5 · 周一</h3><p>带老人：园博园戏曲周最后一天。<br>亲子：地质博物馆或天文馆陨石拓印。</p></div><div><h3>10/6 · 周二</h3><p>科技馆已约课程优先；没约到，换地质馆展厅。<br>网球迷：男单决赛需另核票。</p></div><div><h3>10/7 · 周三</h3><p>留半天给汽车/古动物馆二选一，或附近公园。<br>野鸭湖不必硬挤，可留节后。</p></div></div></section>
<div id="events">CARDS</div>
<section class="panel"><h2>没放进主排行的内容</h2><ul><li>国家自然博物馆“果实有答案”10/1—3、汽车馆3D打印笔10/1等，已错过；不当作剩余假期可参加。</li><li>古观象台10/8、10/17、10/24活动超出10/1—7窗口，留待节后。</li><li>巨C塔可节可顺路吃东西，但不是高参与度亲子主活动；北湖电影也不是儿童专场。</li><li>野鸭湖有自然观察价值，但延续至11/30，因此不为国庆时效强行前排。</li></ul><p class="evidence">已过期与节后日期依据上文文物局、天文馆原始公告。未以AI生成攻略或旧年份文章补齐未知票务。</p></section>
<footer><p>票价未注明者保持未知，不用常规票价冒充国庆实价。停留时长、适配和玩法为编辑建议；未实测自驾公里数或实时路况。地图按钮仅做地点检索，非入口或停车位核验。</p><p><a href="../data/national-day-2026-ranked.json">结构化排行与来源 JSON</a> · <a href="../index.html">返回路线库</a></p></footer>
</main><script>
(()=>{const day=document.getElementById('day'),kind=document.getElementById('kind');function apply(){let n=0;document.querySelectorAll('[data-days]').forEach(el=>{const visible=(day.value==='all'||el.dataset.days.split(' ').includes(day.value))&&(kind.value==='all'||el.dataset.type===kind.value);el.hidden=!visible;if(visible&&el.classList.contains('event'))n++;});document.getElementById('count').textContent='显示 '+n+' 项（保留原推荐序）';}day.addEventListener('change',apply);kind.addEventListener('change',apply);apply();})();
</script></body></html>'''
    page=page.replace('RANKING_BASIS',e(data['ranking_basis'])).replace('ROWS',''.join(rows)).replace('CARDS','\n'.join(cards))
    OUTPUT.write_text(page)
    print(json.dumps({'output':str(OUTPUT),'count':len(items),'names':[a['name'] for a in items]},ensure_ascii=False))

if __name__ == '__main__':
    build()
