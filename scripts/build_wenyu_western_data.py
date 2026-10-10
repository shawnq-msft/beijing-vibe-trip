"""Curate six exact branches from archived WebIQ evidence, without inferred ratings."""
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];D=ROOT/'data'
raw=json.loads((D/'wenyu-western-raw.json').read_text())
results=[]
for batch in raw:
 r=batch['response'];results.extend(r.get('webResults',[r]))
def source(url,publisher,date='未标注'):
 found=[r for r in results if r.get('url')==url]
 assert found,url
 r=max(found,key=lambda x:len(x.get('content','')))
 return {'url':url,'publisher':publisher,'source_date':date,'crawled_at':r.get('crawledAt','2026-10-10 查询；索引抓取时刻未知'),'excerpt':r.get('content','')[:6000]}
official=source('https://www.visitbeijing.com.cn/article/4R5lTKSrsWW','北京旅游网／文旅顺义','2026-04-09')
anku=[source('https://m.dianping.com/shop/79293030','大众点评'),source('https://tw.trip.com/restaurant/china/beijing/detail/restaurant-31509523/','Trip.com'),source('https://you.ctrip.com/food/beijing1/15944662.html','携程；2024年旧快照')]
bell=[source('https://m.dianping.com/shop/1484443513','大众点评'),source('https://www.trip.com/restaurant/china/beijing/detail/restaurant-144301625/','Trip.com')]
meat=[source('https://m.dianping.com/shop/97251680','大众点评'),source('https://www.trip.com/restaurant/china/beijing/detail/meat-by-ernest-44244636/','Trip.com')]
luoma=[official,source('https://tw.trip.com/restaurant/china/beijing/detail/restaurant-130966031/','Trip.com')]
restaurants=[]
def add(id,name,district,cuisine,menu,address,hours,rating,cost,why,priority,sources,parking='具体停车入口、收费、车架限高未知；订位时一起确认'):
 restaurants.append({'id':id,'name':name,'district_id':district,'western':True,'role':cuisine+'｜特色西餐扩展；不冒充点评头部榜','rating':rating,'average_cost_per_person':cost,'rank':'大众点评实时分数与当前榜单未获取；不是差评或不存在的结论','address':address,'opening_hours':hours+'；公开资料参考，非当天确认','menu_evidence':menu,'family_use':why,'indoor_seating':'实体餐厅；是否能选庭院位、包间与儿童座椅按店确认','parking':parking,'gate_and_parking_relation':'这是自驾午餐目的地，不在沈家闸骑行道上。吃完装车驾往沈家闸，核对当天导航；不让孩子骑公共道路去餐厅。','priority':priority,'sources':sources})
add('anku','安酷意大利餐厅（荣祥广场店）','rongxiang','意大利菜／披萨意面',['火腿蘑菇披萨','肉酱千层面','海鲜扁意面','提拉米苏'],'顺义榆阳路荣祥广场813号','Trip.com列11:00—14:00、17:00—21:00；2024携程只显示晚市，午市须电话复核','点评分未知；Trip.com 4.8/5（5条，2026-09索引）','当前未知；携程2024旧快照约¥222，不作现价','披萨、千层面与意面适合一家分享；本次最容易和孩子口味兼容的西餐候选。','优先问午市；不把少量评价的4.8直接当稳定头部',anku)
add('bellota','Bellota贝尤塔西班牙餐厅（荣祥广场店）','rongxiang','西班牙菜／海鲜饭',['招牌西班牙海鲜饭','橄榄油爆大虾','伊比利亚火腿丸子','金枪鱼馅饼'],'顺义空港街道馨园一路2号院荣祥广场882号','Trip.com列11:00—22:00','点评分未知；Trip.com 5.0/5（仅2条，2026-07索引）','未知；未获取可靠现价','想吃得更有特色选这家，一锅海鲜饭配小食分享；向店里确认出餐时间，给骑行留足下午。','和安酷同一商业节点二选一；开车的大人不喝酒',bell,'Trip.com列有停车位；入口、收费、限高、余位未知')
add('meat-ernest','MEAT by Ernest吃肉餐厅（新国展店）','tongli','牛排／熟成肉类',['西冷牛排','T骨牛排','烤凯撒色拉','手工薯条'],'顺义裕丰路与天北路交叉口北约200米，同里市集一带（Trip.com位置描述；门牌未知）','Trip.com列11:00—22:00','点评分未知；Trip.com 4.8/5（5条，2026-09索引）','未知；菜单报价与熟成牛排重量须询店','牛排爱好者的目的型午餐，不用把它当便宜轻食；给孩子选充分熟制的菜。','预约时确认牛排重量、报价和用餐时长；未核实2026黑珍珠官方名单，不挂黑珍珠称号',meat,'Trip.com列有停车、露台、儿童餐椅；具体入口、收费、限高未知')
add('parkside','ParkSide园景（祥云店）','xiangyun','庭院西餐／牛排与德式香肠',['28天干式熟成牛排','墨西哥辣味牛肉饼','德式香肠拼盘'],'顺义安泰大街6号院12号楼105，祥云小镇南区','午餐具体时段未知；官方介绍有三餐，不据此推定几点开门','点评分未知；不使用酒仙桥分店评分','未知','想要花园庭院氛围可选；给孩子点不辣款，室外位置需确认天气与座位。','与弗萨塔可在同一栋相邻门牌，停车一次再按菜系选；不套用酒仙桥店营业时间',[official])
add('fousa','HFFOUSA TACO弗萨塔可墨西哥餐厅（顺义店）','xiangyun','墨西哥菜／塔可',['番茄冷汤','缤纷塔可组合'],'顺义中粮祥云小镇南区12号楼104','午餐营业时段未知，先联系确认','点评分、榜单未知；2026-04文旅顺义点名推荐','未知','比常见商场西餐更有区别；塔可适合分享，提前问辣度和孩子可选口味。','官方联系方式010-84728787；未证实儿童菜单或套餐，不编造',[official])
add('luomahu9','罗马湖9号（左堤路店）','luomahu','湖景／融合西餐',['勃艮第青酱蜗牛','韩式班尼迪克','炭烤深海鳕鱼','西班牙蒜香虾'],'顺义后沙峪镇罗马湖左堤路9号（Trip.com/地图标甲9号）','Trip.com列10:00—21:00','点评分未直接核实；Trip.com 4.6/5（5条，公开索引）','未知','湖景、庭院与班尼迪克更贴近悠闲早午餐；是融合西餐，不称纯法餐或全日brunch专门店。','这是更偏北的目的型绕行，午餐后还要开回沈家闸；下午仍按野餐垫＋自带水果零食桌游，不另加咖啡站',luoma)
common='按已核地址作行程策划分组，不是实时导航最短路；绕行分钟数未知。'
districts=[
{'id':'rongxiang','name':'顺义①｜中央别墅区·荣祥广场','anchor':'北京顺义荣祥广场','address':'榆阳路／馨园一路2号院一带，813号安酷、882号Bellota','parking':'Bellota资料列有停车；商业区停车入口、费用与自行车架限高未知','route_note':'西餐优先落脚点：五道口→荣祥广场午餐→沈家闸。不是骑行起点旁边，但可作为专门的午餐节点。'+common,'decision':'优先二选一：孩子偏披萨意面选安酷，想更特别选Bellota海鲜饭。','candidate_ids':['anku','bellota'],'sources':[anku[1],bell[1]]},
{'id':'tongli','name':'顺义②｜天北路·同里市集一带','anchor':'MEAT by Ernest 新国展店','address':'裕丰路与天北路交叉口北约200米；具体门牌未知','parking':'餐厅资料列有停车；入口、收费与限高未知','route_note':'专门吃牛排的目的型午餐点；不是荣祥广场内，不建议两处串店。'+common,'decision':'牛排控选MEAT；预算和用餐时间先问清。','candidate_ids':['meat-ernest'],'sources':[meat[1]]},
{'id':'xiangyun','name':'顺义③｜祥云小镇南区','anchor':'北京中粮祥云小镇南区','address':'安泰大街6号院12号楼104／105','parking':'先导航南区停车入口；本次未核实收费、优惠与车架限高','route_note':'偏北的商圈型绕行，买单后直接自驾去沈家闸，不把逛街加成第二个主节目。'+common,'decision':'同栋两选：ParkSide花园西餐，弗萨塔可墨西哥菜。','candidate_ids':['parkside','fousa'],'sources':[official]},
{'id':'luomahu','name':'顺义④｜后沙峪·罗马湖南岸','anchor':'罗马湖9号 左堤路店','address':'后沙峪罗马湖左堤路甲9号','parking':'湖边停车入口、费用、周末余位未知；不把道路两边视作合法停车位','route_note':'更偏北的湖景目的地，不标“顺路”；适合愿意为一顿湖景午餐绕一下。午后仍返回沈家闸骑行。'+common,'decision':'想把午餐本身变成一段休闲体验选罗马湖9号；不顺带改掉已定骑行线。','candidate_ids':['luomahu9'],'sources':[official,luoma[1]]}]
assert len(restaurants)==len({x['id'] for x in restaurants})==6
out={'checked_on':'2026-10-10','method':'WebIQ原始公开索引和正文；菜单用点评，地址/营业/评分用明确标注的平台。没有登录App实时分数，不擅称头部榜。','candidate_count':len(restaurants),'candidates':restaurants,'districts':districts,'excluded_notes':['2019年的别墅区西餐榜只作线索，不作为当前营业确认','Lakers、七十千克未取得足够当前分店证据，不凑入本批','悦石不是本批西餐优选；不把罗兰湖（丽都公园）错当罗马湖']}
(D/'wenyu-western-dining.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({'western_count':len(restaurants),'district_count':len(districts),'names':[x['name'] for x in restaurants]},ensure_ascii=False))
