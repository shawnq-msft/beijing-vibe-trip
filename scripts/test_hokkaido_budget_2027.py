"""Verify prices, full hotel-night coverage, real evidence and rendered budget."""
import json,re,hashlib
from datetime import date,timedelta
from pathlib import Path
from urllib.parse import urlparse,parse_qs
from bs4 import BeautifulSoup
ROOT=Path(__file__).resolve().parents[1]
d=json.loads((ROOT/'data/hokkaido-2027-budget.json').read_text())
e=json.loads((ROOT/'data/hokkaido-2027-budget-evidence.json').read_text())
q=d['quotes']
for key,x in q.items():
    z=e[x['snapshot']]; text=z['text']+'\n'+'\n'.join(z.get('price_labels',[]))
    assert z['retrieved_at'],key
    assert x['evidence_needle'] in text,key
    query=parse_qs(urlparse(z['url']).query)
    if x['kind']=='flight':
        assert query['quantity']==['2'] and query['childqty']==['1']
        assert f"Round-trip price: CNY {x['amount_cny']:,}" in z['price_labels']
    else:
        assert query['adult']==['2'] and query['children']==['1'] and query['ages']==['10']
        assert '1 room, 2 adults, 1 child' in text
        assert re.search(r'(?:Total price:|Total \(incl\. taxes & fees\):) CNY '+format(x['amount_cny'],','),text),key
for s in d['scenarios']:
    assert all(q[k]['eligible'] for k in s['components'])
    assert sum(q[k]['amount_cny'] for k in s['components'])==s['subtotal_cny']
    assert s['hotel_cny']+s['flight_cny']==s['subtotal_cny']
    nights=[]
    for key in s['components']:
        x=q[key]
        if x['kind']!='hotel':continue
        a,b=date.fromisoformat(x['start']),date.fromisoformat(x['end'])
        nights += [(a+timedelta(days=i)).isoformat() for i in range((b-a).days)]
    a,b=date.fromisoformat(s['start']),date.fromisoformat(s['end'])
    assert len(nights)==len(set(nights))==s['nights']
    assert sorted(nights)==[(a+timedelta(days=i)).isoformat() for i in range((b-a).days)]
assert d['scenarios'][0]['subtotal_cny']==37917
assert d['scenarios'][1]['subtotal_cny']==37861
assert not q['rusutsu_unresolved']['eligible'] and not q['early_ski_unmatched']['eligible']
assert q['ski4']['room_or_route'].startswith('Standard Twin Room with Mt.Tokachi View and Sofabed Non smoking')
s=BeautifulSoup((ROOT/'pages/spring-festival-2027-hokkaido-ski-onsen.html').read_text(),'html.parser')
b=s.select_one('#budget');assert b,'Missing budget section'
t=b.get_text(' ',strip=True)
for needed in ('37,917','37,861','25,332','26,772','未进入选定返程','不含早餐','沙发床','4天年假','5天年假','56元','3,306元'):
    assert needed in t,needed
assert len(b.select('table'))==5
assert len(b.select('tbody tr'))==23
assert s.select_one('.toc a[href="#budget"]')
assert not b.select('.jpy-price'),'CNY sums were misinterpreted as JPY'
assert '54,551' in t
assert '人民币6,929元' in t
print(json.dumps({'scenarios':len(d['scenarios']),'quotes_grounded':len(q),'budget_tables':len(b.select('table')),'complete_hotel_nights':[s['nights'] for s in d['scenarios']],'subtotal_cny':[s['subtotal_cny'] for s in d['scenarios']],'exclusions_tested':True},ensure_ascii=False))
