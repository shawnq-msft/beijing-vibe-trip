"""Freeze manually inspected live listing quotes; fail if evidence changed.
No network calls, booking, or inferred prices. Raw browser files remain local.
"""
import json, hashlib
from datetime import date, timedelta
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / 'data'
RAW = DATA / 'hokkaido-2027-budget-browser'
ledger_path = DATA / 'hokkaido-2027-citations.json'
ledger = json.loads(ledger_path.read_text())
evidence = {}
quotes = {}
frozen_path = DATA / 'hokkaido-2027-budget-evidence.json'
frozen = json.loads(frozen_path.read_text()) if frozen_path.exists() else {}
def add(key, snapshot, amount, kind, title, start, end, room_or_route, needle, notes, eligible=True):
    raw_path = RAW / (snapshot + '.json')
    obj = json.loads(raw_path.read_text()) if raw_path.exists() else frozen[snapshot]
    searchable = obj['text'] + '\n' + '\n'.join(obj.get('price_labels', []))
    if kind == 'hotel': needle = 'CNY ' + format(amount, ',')
    assert needle in searchable, (key, needle)
    assert start in obj['url'] and end in obj['url'], obj['url']
    if snapshot not in evidence:
        evidence[snapshot] = {k: obj[k] for k in ('url', 'title', 'text') if k in obj}
        evidence[snapshot]['text'] = obj['text'].split('Guest Reviews')[0] if kind == 'hotel' else obj['text']
        evidence[snapshot]['sha256_text'] = hashlib.sha256(evidence[snapshot]['text'].encode()).hexdigest()
        evidence[snapshot]['retrieved_at'] = obj.get('retrieved_at', obj.get('collected_at'))
        evidence[snapshot]['price_labels'] = obj.get('price_labels', [])
    url = obj['url']
    rec = next((r for r in ledger['sources'] if r['url'] == url), None)
    if rec is None:
        rec = {'id': max(r['id'] for r in ledger['sources']) + 1, 'url': url, 'title': title, 'accessed': '2026-10-27'}
        ledger['sources'].append(rec)
    quotes[key] = dict(amount_cny=amount, kind=kind, title=title, start=start, end=end,
                       room_or_route=room_or_route, notes=notes, eligible=eligible,
                       source_id=rec['id'], snapshot=snapshot, evidence_needle=needle)
add('flight8', 'flight-jan30-feb06-final', 12585, 'flight', 'Trip.com 北京—新千岁 1/30—2/6 往返列表', '2027-01-30', '2027-02-06', '国泰；去程 PEK 07:30—CTS 17:50，香港转机，总时长9h20', 'Round-trip price: CNY 12,585', '3位旅客查询的往返列表合计；不是成人单价×3。返程航班、托运和最终税费尚未进入选定返程/确认页核实。')
add('flight9', 'flight-jan29-feb06-complete', 11089, 'flight', 'Trip.com 北京—新千岁 1/29—2/6 往返列表', '2027-01-29', '2027-02-06', '国泰；去程 PEK 03:25—CTS 16:00，香港转机，总时长11h35', 'Round-trip price: CNY 11,089', '红眼出发；3人往返列表合计，返程航班与行李未锁定。不能与8天早班样本视为同等舒适度。')
add('flight9_low', 'flight-jan29-feb06-complete', 9882, 'flight', 'Trip.com 北京—新千岁 1/29—2/6 往返列表', '2027-01-29', '2027-02-06', '国泰；去程 PEK 03:25—CTS 17:50，总时长13h25', 'Round-trip price: CNY 9,882', '低价代价是凌晨出发＋长中转；不作为主预算。', False)
add('flight12', 'flight-jan31-feb11-loaded', 14371, 'flight', 'Trip.com 北京—新千岁 1/31—2/11 往返列表', '2027-01-31', '2027-02-11', '国泰；去程 PEK 03:25—CTS 14:50，香港转机，总时长10h25', 'Round-trip price: CNY 14,371', '红眼出发；原12天方案的机票样本，未凑齐相同住宿组合，不能给出精确机酒节省额。')
add('flight_early', 'flight-jan23-30-retry', 14622, 'flight', 'Trip.com 北京—新千岁 1/23—1/30 往返列表', '2027-01-23', '2027-01-30', 'ANA；去程 PEK 08:25—CTS 16:35，东京转机，总时长7h10', 'Round-trip price: CNY 14,622', '提前一周的日间、非大陆航司样本；不证明全市场最低价。更低的4,267元/人样本含国航＋Jin Air联运，不按用户偏好作为首选。')
add('ski4', 'hotel-furano-jan31-feb04', 16222, 'hotel', 'Trip.com 新富良野王子 1/31—2/4', '2027-01-31', '2027-02-04', 'Standard Twin Room with Mt.Tokachi View and Sofabed Non smoking；2单人床＋1沙发床，4晚', 'CNY 16,222 total', '2成人＋1名10岁儿童；不含早；12/31前可取消、线上预付。含税列表合计，第三张沙发床铺设和地方附加费须最终确认。含3早餐版本为17,640元，不混用。')
add('city1', 'hotel-grand-jan30-31', 1718, 'hotel', 'Trip.com 札幌格兰 1/30—1/31', '2027-01-30', '2027-01-31', '[Grand Classic]Superior Twin Room/3 People Use；2小双人床＋1单人床，禁烟，1晚', 'CNY 1,718 total', '不含早、不退款、线上预付，Silver Tier Deal；含税列表合计。可取消版本1,826元。')
add('city2start', 'hotel-grand-jan29-31', 3158, 'hotel', 'Trip.com 札幌格兰 1/29—1/31', '2027-01-29', '2027-01-31', '[Grand Classic]Superior Twin Room/3 People Use；2小双人床＋1单人床，禁烟，2晚', 'CNY 3,158 total', '与city1同房型、不含早、线上预付；该卡未清晰列出取消截止，需确认；不是单晚乘2。')
add('city2end', 'hotel-keio-feb04-06', 7392, 'hotel', 'Trip.com 札幌京王广场 2/4—2/6', '2027-02-04', '2027-02-06', 'Standard Triple Room；3张单人床，禁烟，2晚', 'CNY 7,392 total', '不含早；2/2前可取消、线上预付、33% Special Discount；含税列表合计。含3早餐版本8,158元。排除下方Select multiple rooms区不满足全组的单房价。')
add('westin4', 'hotel-westin-jan31-feb04', 32856, 'hotel', 'Trip.com 留寿都威斯汀 1/31—2/4', '2027-01-31', '2027-02-04', 'Standard 3 Single beds 1 bedroom two-story；3张小双人床，4晚', 'CNY 32,856 total', '不含早；1/1前可取消，可到店付；页面标Children stay for free，但本房3张床，不拿双床免费同睡价当三床价。非富良野同地替换，课程接驳须重报。')
add('rusutsu_unresolved', 'hotel-rusutsu-jan31-feb04', 57648, 'hotel', 'Trip.com 留寿都 Resort Hotel 1/31—2/4', '2027-01-31', '2027-02-04', 'Standard Twin Room 2 Occupanacy；2张单人床，4晚', 'CNY 57,648 total', '虽然搜索为2大1小且套餐列3早餐，房名明确2 Occupancy、未证第三床。排除出合法三人机酒预算；不是酒店正常价或不可订结论。', False)
add('early_ski_unmatched', 'hotel-furano-jan24-28', 41292, 'hotel', 'Trip.com 新富良野王子 1/24—1/28', '2027-01-24', '2027-01-28', 'Corner Suite Non Smoking；2单人床，4晚', 'CNY 41,292 total', '仅见套房样本，未证第三床，不计总预算；不能与后周双床加沙发床作同房型涨跌比较。', False)
add('early_city', 'hotel-keio-jan28-30', 4086, 'hotel', 'Trip.com 札幌京王广场 1/28—1/30', '2027-01-28', '2027-01-30', 'Standard Triple Room；3张单人床，禁烟，2晚', 'CNY 4,086 total', '不含早；1/26前可取消、线上预付、33% Special Discount。与雪祭周同房型，可比较两段列表总价，但非保证未来价差。')
calendar_urls = [
 ('https://www.gov.cn/zhengce/content/202411/content_6986380.htm', '国务院：春节法定假日为除夕及正月初一至初三'),
 ('https://jw.beijing.gov.cn/xxgk/2024zcwj/2024qtwj/202604/t20260417_4588623.html', '北京市教委2026—2027校历'),
]
calendar_ids = []
for url,title in calendar_urls:
    rec=next((x for x in ledger['sources'] if x['url']==url),None)
    if rec is None:
        rec={'id':max(r['id'] for r in ledger['sources'])+1,'url':url,'title':title,'accessed':'2026-10-27'}
        ledger['sources'].append(rec)
    calendar_ids.append(rec['id'])
model = {'as_of':'2026-10-27', 'party':{'adults':2,'children':1,'child_age':10,'rooms':1,'status':'预算比较假设；未确认是否有老人同行'},
         'currency':'CNY','status':'实时搜索列表快照，未预订；机票未到选定返程/最终确认页',
         'quotes':quotes, 'calendar_source_ids':calendar_ids,
         'scenarios':[
          {'id':'short8','title':'8天7晚：缩短主比较','start':'2027-01-30','end':'2027-02-06','components':['flight8','city1','ski4','city2end']},
          {'id':'early9','title':'9天8晚：多请一天不一定省','start':'2027-01-29','end':'2027-02-06','components':['flight9','city2start','ski4','city2end']},
         ]}
for s in model['scenarios']:
    a,b=date.fromisoformat(s['start']),date.fromisoformat(s['end'])
    s['nights']=(b-a).days;s['days']=s['nights']+1
    s['weekdays']=sum((a+timedelta(days=i)).weekday()<5 for i in range(s['days']))
    s['estimated_leave_before_adjustment']=s['weekdays']-1 # 2/5 statutory New Year's Eve
    s['hotel_cny']=sum(quotes[k]['amount_cny'] for k in s['components'] if quotes[k]['kind']=='hotel')
    s['flight_cny']=sum(quotes[k]['amount_cny'] for k in s['components'] if quotes[k]['kind']=='flight')
    s['subtotal_cny']=s['hotel_cny']+s['flight_cny']
ledger_path.write_text(json.dumps(ledger,ensure_ascii=False,indent=2)+'\n')
(DATA/'hokkaido-2027-budget-evidence.json').write_text(json.dumps(evidence,ensure_ascii=False,indent=2)+'\n')
(DATA/'hokkaido-2027-budget.json').write_text(json.dumps(model,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({'scenarios':model['scenarios'],'quotes':len(quotes),'source_count':len(ledger['sources'])},ensure_ascii=False,indent=2))
