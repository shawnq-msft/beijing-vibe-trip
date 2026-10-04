"""Merge the source-verified indoor additions into the holiday guide."""
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
p=ROOT/'data/national-day-2026-ranked.json'
d=json.loads(p.read_text())
r=json.loads((ROOT/'data/national-day-2026-indoor-research.json').read_text())
assert r['count']==len(r['activities'])==3
mapping={'craft-heritage-indoor':'craft','natural-history-indoor':'natural','film-museum-indoor':'film'}
old={a['id']:a for a in d['activities']}
for a in r['activities']:
    b={k:a[k] for k in ['name','type','area','dates','full_dates','hours','duration','why','intro','price','booking','elder','sources']}
    b.update(id=mapping[a['id']],plan=a['today_action'],risk=' '.join(a['uncertainties']),evidence=a['category']+'；馆方原文已读，余票未核',navigation=a['name'].split(' · ')[0])
    old[b['id']]=b
order=['geology','science','astro','craft','natural','fossil','cars','film']
order += [a['id'] for a in sorted(old.values(),key=lambda x:x.get('rank',999)) if a['id'] not in order]
assert len(order)==len(set(order))==13
for i,k in enumerate(order,1):old[k]['rank']=i
d['activities']=[old[k] for k in order]
d['ranking_basis']='10/4按家长反馈的大风情境重排：室内优先，其次孩子的地质/科学/动手兴趣、来源可靠性与老人休息条件；户外和赛事保留为天气转稳后的备选。推荐序为编辑判断，不是平台评分；未核实时余票。'
p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({'total':len(order),'indoor':sum(a['type']=='indoor' for a in d['activities']),'order':order},ensure_ascii=False))
