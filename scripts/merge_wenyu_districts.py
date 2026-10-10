"""Normalize preserved WebIQ evidence into the dining-page schema."""
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
D=ROOT/'data'
def load(name): return json.loads((D/name).read_text())
a=load('wenyu-hubs-aosen.json'); b=load('wenyu-hubs-beiyuan.json'); l=load('wenyu-district-laiguangying.json'); old=load('wenyu-late-start-dining.json')
def source(s):
    url=s['url']
    crawled=s.get('crawled_at',s.get('source_crawled_at')) or '未知'
    updated=s.get('source_updated_at',s.get('last_updated_at'))
    return {'publisher':('大众点评公开索引/笔记' if 'dianping.com' in url else '地址/营业/停车补证'), 'url':url,'source_date':updated or '发布日期未知；历史信息仅参考','crawled_at':crawled,'evidence':s.get('excerpt','')[:2200]}
def raw_sources(doc, ids):
    rows={r['id']:r for r in doc['raw_evidence']}
    return [source(rows[i]) for i in dict.fromkeys(ids)]
a_park='导航“新奥购物中心东区-地下停车场”，湖景东路9号。具体车行坡道、小时费率与车架限高未知；2023年消费减免资料仅作历史线索，不能保证今天免费。'
b_park='北苑东路19号院，中国铁建广场/龙湖北京北苑天街商业节点；有地下停车场资料，当前访客入口、费用、限高未知，出发前按地图核对。'
districts=[
 {'id':'aosen','name':'奥森南侧｜北投新奥购物中心','anchor':'新奥购物中心东区-地下停车场','address':a['hub']['address'],'parking':a_park,'route_note':'五道口先向东到奥林匹克公园南侧落座，吃完再向东北去P20/P21。适合希望早些吃上饭；不是贴着五环的无绕行停靠，导航须比较两段路线。商场内换店不需要移车，不另加奥森游览。','decision':'首选南拳十三姨：粥和粤菜最贴合早午餐。姚姚、御京轩按菜系作榜单备选。','sources':raw_sources(a,['e7','e74','e24']),'candidate_ids':[]},
 {'id':'beiyuan','name':'北苑｜龙湖北京北苑天街','anchor':'龙湖北京北苑天街 停车场','address':b['hub']['address'],'parking':b_park,'route_note':'北苑东路19号院的单一商业落点，不是清河营南街所有店都在楼里。四家资料均指向这座商场；先停一处再选菜系，饭后自驾去P20/P21。是否比来广营更顺，以当天导航为准。','decision':'想吃一顿有体验感的选水木锦堂；想烤肉选西塔。另列两家特色待核，不混称高分店。','sources':raw_sources(b,['e40','e56','e54']),'candidate_ids':[]},
 {**l['district'],'decision':'优先滇大池；想吃烤鸭选北平盛世，徽菜选皖江宴。皖江宴是独立停车落点。','candidate_ids':[]}
]
cards=[]
for c in a['candidates']:
    if c['id'] not in ['nanquan-shisanyi','yaoyao','yujingxuan']:continue
    dp=c['dianping']; lunch=c['lunch']
    ss=[source(s) for s in c['sources']]
    card={'id':c['id'],'district_id':'aosen','name':c['name'],'role':{'nanquan-shisanyi':'本商圈首选｜早午餐适配：砂锅粥＋粤菜','yaoyao':'川菜榜单备选｜旧快照，先核仍营业','yujingxuan':'北京菜榜单备选｜有区域榜，不等于高分店'}[c['id']], 'rating':f"点评公开索引 {dp['score']}/5；评论量未知",'average_cost_per_person':f"约{dp['per_person_cny']}元（索引快照，非报价）", 'rank':dp['ranking_full_text']+'；非全城榜。'+('2025-04-19旧快照，非当前榜位。' if c['id']=='yaoyao' else ''),'address':c['address'],'opening_hours':(lunch['hours'] or '固定午市时段未知')+'；'+lunch['evidence_level'],'menu_evidence':c['menu_three_items'],'family_use':c['family_fit_editorial'],'indoor_seating':'商场餐厅；实时桌型/座位未知','parking':a_park,'gate_and_parking_relation':'先在新奥吃饭，再取车去温榆河P20/P21；不是园边店或骑行补给。','priority':lunch['note']+' 不默认允许桌游。','sources':ss,'evidence_tier':'点评分/榜单候选'}
    if c['id']=='yujingxuan':card['address']='北京市朝阳区湖景东路新奥购物中心；确切楼层/铺号待核，不把工商注册地址当营业门牌'
    cards.append(card);districts[0]['candidate_ids'].append(card['id'])
# Parent directly rechecked this exact branch; a menu-only browse had dropped its score.
parent_shuimu={'publisher':'大众点评商户公开索引（主代理补核）','url':'https://m.dianping.com/shop/1518661917','source_date':'动态页，发布日期未知','crawled_at':'工具元数据2026-10-10T08:22:00Z；晚于查询时刻，时间可靠性未核','evidence':'水木锦堂·自助铁板烧（北苑天街店）；4.7；¥268/人；北苑家园自助餐销量榜·第1名；菲力牛排、奶香凤尾虾、蒜蓉鲍鱼。查询日期2026-10-10。此为实际检索返回，非实时营业证明。'}
bs={c['id']:c for c in b['restaurants']}
for cid in ['shuimu-beiyuan','xita-beiyuan','meatu-beiyuan','yunli-beiyuan']:
    c=bs[cid];dp=c['dianping'];lunch=c['lunch'];ss=raw_sources(b,c['source_ids']);score=dp['score'];rank=dp['ranking_full_text'];risks=c['risks']
    if cid=='shuimu-beiyuan':
        score=4.7;rank='北苑家园自助餐销量榜 · 第1名';ss=[parent_shuimu]+[s for s in ss if s['url']!=parent_shuimu['url']];risks=['午市固定时段、儿童收费规则未知；自助用餐可能挤占下午骑行，提前控时']
    qualified=score is not None
    note='历史营业参考 '+lunch['hours'] if lunch['hours'] else '固定午市时段未知'
    if lunch.get('evidence_excerpt'):note+='；'+lunch['evidence_excerpt']
    card={'id':cid,'district_id':'beiyuan','name':c['name'],'role':{'shuimu-beiyuan':'本商圈体验首选｜现场铁板料理，自助需控时','xita-beiyuan':'烤肉榜单备选｜区域回头客榜，不等于高分店','meatu-beiyuan':'特色待核，不列高分头部｜花园西餐、牛排烩饭','yunli-beiyuan':'特色待核，不列高分头部｜蒸汽石锅鱼'}[cid],'rating':f'点评公开索引 {score}/5；评论量未知' if qualified else '点评评分未知；不能用其它平台评分代替','average_cost_per_person':f"约{dp['per_capita_cny']}元（{'商户索引' if qualified else '历史点评笔记关联卡片'}，非实时报价）",'rank':(rank+'；仅所示区域与榜单维度，非全城榜') if rank else '未核到本分店点评榜单；仅作为特色候选，不冒称头部','address':c['address'],'opening_hours':note,'menu_evidence':c['menu_3'],'family_use':'编辑建议：'+c['specialty'],'indoor_seating':'商场内餐厅；实时座位和桌型未知','parking':b_park,'gate_and_parking_relation':'北苑商场用餐后另行自驾至P20/P21，儿童不骑公共道路接驳。','priority':'；'.join(risks)+'；不默认允许自带桌游','sources':ss,'evidence_tier':'点评分/榜单候选' if qualified else '特色待核'}
    cards.append(card);districts[1]['candidate_ids'].append(cid)
for c in l['candidates']:
    c['district_id']='laiguangying';c['evidence_tier']='点评分/榜单候选';cards.append(c);districts[2]['candidate_ids'].append(c['id'])
# Preserve original named coffee fallback without promoting it to a dining destination.
coffee=next(c for c in old['candidates'] if c['id']=='chunhejingming');coffee['evidence_tier']='原有茶咖待核';cards.append(coffee)
result={'checked_on':'2026-10-10','method':'WebIQ中文检索与正文补证，公开索引不是实时App；按确切分店归组，历史营业与未知项分开。8家有点评评分/榜单依据，2家特色备选未核到点评评分，另保留原茶咖。未宣称穷尽所有头部店。','candidate_count':len(cards),'restaurant_count':sum(len(d['candidate_ids']) for d in districts),'shortlist':'早午餐选南拳十三姨；特色鱼锅选滇大池；现场料理选水木锦堂；烤鸭选北平盛世','districts':districts,'candidates':cards,'excluded':l['excluded']+[{'name':'馋人小馆（新奥购物中心店）','reason':'虽见区域北京菜热门榜第4，但点评索引仅4.1，与御京轩烤鸭菜系重复，本次不为数量加进头部清单'},{'name':'云海肴（新奥店）','reason':'未核到本分店点评评分；与已收录石锅鱼重复，本次不以普通连锁补数'}]}
western=load('wenyu-western-dining.json')
for c in western['candidates']:
    c['evidence_tier']='西餐特色补充；平台分数独立标注'
cards.extend(western['candidates'])
districts[:0]=western['districts']
for c in cards:
    c['gate_and_parking_relation']=c['gate_and_parking_relation'].replace('P20/P21','沈家闸起点').replace('P20','沈家闸起点')
for d in districts:
    d['route_note']=d['route_note'].replace('P20/P21','沈家闸起点').replace('P20','沈家闸起点')
result.update(candidate_count=len(cards),restaurant_count=sum(len(d['candidate_ids']) for d in districts),western_count=len(western['candidates']),shortlist='西餐先看安酷／Bellota；牛排选MEAT；庭院选ParkSide；中餐早午餐选南拳十三姨',method='新增6家顺义特色西餐，评分按平台单列，不冒充点评高分；保留原10家餐厅和1家历史茶咖备选。所有商圈用餐后自驾至沈家闸，下午野餐桌游不绑定餐厅。')
assert len({c['id'] for c in cards})==len(cards)
assert all(c['sources'] for c in cards)
(D/'wenyu-dining-districts.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({'merchants':len(cards),'restaurants':result['restaurant_count'],'districts':{d['name']:len(d['candidate_ids']) for d in districts},'rated_or_ranked':sum(c['evidence_tier']=='点评分/榜单候选' for c in cards)},ensure_ascii=False))
