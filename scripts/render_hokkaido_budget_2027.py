"""Data-driven budget section; CNY prices must not pass the JPY decorator."""
import json
from decimal import Decimal, ROUND_HALF_UP
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
def render_budget():
    d=json.loads((ROOT/'data/hokkaido-2027-budget.json').read_text())
    q=d['quotes']; a,b=d['scenarios']; money=lambda n:f'人民币{n:,}元'
    cite=lambda k:f"[{q[k]['source_id']}]"
    lines=['## 预算模块：提前出发，缩到8–9天 {#budget}',
      '**先按北京出发、2成人＋毛豆（10岁）、1间可住3人的房核算；这是比较假设，不默认老人同行。** 价格采集于2026-10-27。酒店使用整段含税列表总价；机票使用3位旅客查询的往返列表合计，**不是最终订单报价**。未进入选定返程/确认页，返程具体班次、托运行李与最终费用仍未核实。会员/促销价仅对当前页面条件有效；未减积分、返现、未领优惠券。',
      '**当前更值得保留8天7晚：1/30—2/6，富良野＋札幌。机票＋酒店样本合计'+money(a['subtotal_cny'])+'（约3.8万元），不含课费、雪票雪具、餐饮、地面交通、签证保险与地方附加费。** 留寿都课程优势仍保留，但当前度假酒店样本明显更贵，不能再无条件称为预算主案。',
      '### 时间和请假：先算工作日，不冒充已公布调休',
      '| 窗口 | 时长与骨架 | 日历周一至五 | 仅扣现行法定日期后的估计 |',
      '|---|---|---|---|',
      f"| **1/30周六—2/6周六** | 8天7晚；札幌1晚＋富良野4晚＋札幌2晚 | {a['weekdays']}天 | 约{a['estimated_leave_before_adjustment']}天年假，年度调休及公司安排待核 |",
      f"| 1/29周五—2/6周六 | 9天8晚；札幌2晚＋富良野4晚＋札幌2晚 | {b['weekdays']}天 | 约{b['estimated_leave_before_adjustment']}天年假，同上；多一天主要用于恢复 |",
      '| 1/23周六—1/30周六 | 提前一周8天7晚；不看2月雪祭 | 5天 | 通常需覆盖5个工作日；不能据此锁定年假 |',
      '| 原1/31—2/11 | 12天11晚，继续作为长版备选 | 9天 | 仅扣2/5、2/8后为7天，年度补休/补班未计 |',
      f"除夕2/5、初一2/6；现行法律春节假日含除夕至初三，但**本轮没有核实2027年度调休表**，不把第三方预测当放假通知。[6][{d['calendar_source_ids'][0]}] 北京市教委义务教育寒假为1/18—2/21，以上都在校历寒假内，仍以毛豆学校通知为准。[{d['calendar_source_ids'][1]}] 雪祭已公布2/4—11，短版尾段可覆盖。[7]",
      '### 机票：避开“最低价其实跨夜或次日到”的坑',
      '| 北京⇄新千岁窗口 | 三人往返列表合计 | 已读到的去程与取舍 |',
      '|---|---|---|']
    for key in ['flight8','flight9','flight9_low','flight_early','flight12']:
        x=q[key];lines.append(f"| {x['start']}—{x['end']} | {money(x['amount_cny'])} | {x['room_or_route']}。{x['notes']} {cite(key)} |")
    lines += ['当前这些列表未显示直飞，不据此断言航司整个雪季没有直飞。ANA边栏的“最低价”也不等于已验证的日间、无换机场行程；东京羽田/成田、香港及首尔中转条件须逐段复核。国泰样本符合优先非大陆航司的偏好，但经香港绕行，不能仅按便宜选红眼。',
      '### 酒店：同一入住人数，明确第三张床，按完整晚数核算',
      '| 日期／酒店 | 房型、床位与整段价格 | 餐食、取消与限制 |',
      '|---|---|---|']
    for key in ['city1','ski4','city2end','city2start','westin4','early_city']:
        x=q[key];lines.append(f"| {x['start']}—{x['end']} · {x['title'].replace('Trip.com ','')} | {x['room_or_route']}。**{money(x['amount_cny'])}** | {x['notes']} {cite(key)} |")
    lines += ['所有主预算酒店样本均**不含早餐**，不是免费早餐套餐。房间出现“2大1小”不自动证明第三床，沙发床是否已铺设、地方住宿税/入汤税和套餐人数均须确认。库存、优惠与取消条款可能变化。',
      '### 两个短版机酒小计：精确加总，不声称锁价',
      '| 方案 | 三人机票 | 全程酒店 | 机票＋酒店 |',
      '|---|---|---|---|']
    for s in d['scenarios']:
        ids=''.join(cite(k) for k in s['components'])
        lines.append(f"| **{s['title']}** {ids} | {money(s['flight_cny'])} | {money(s['hotel_cny'])} | **{money(s['subtotal_cny'])}** |")
    diff=a['subtotal_cny']-b['subtotal_cny']; snowdiff=q['city2end']['amount_cny']-q['early_city']['amount_cny']
    westin_total=a['subtotal_cny']-q['ski4']['amount_cny']+q['westin4']['amount_cny']
    lines += [f"- 9天样本仅比8天少**{diff}元**：额外一晚基本吃掉机票差价，还换成03:25起飞。**不为这点账面差价多请一天假**；若想多留一天，应为恢复或家庭活动而留。两者航班舒适度并不等价。",
      f"- 京王同一Standard Triple、不含早、相同促销口径，两晚1/28—30为{money(q['early_city']['amount_cny'])}，雪祭2/4—6为{money(q['city2end']['amount_cny'])}，样本差{snowdiff:,}元。但提前一周的雪场查询仅出现未证第三床的角套房，**没有凑齐同房型合法三人连住价，不能得出全程便宜的结论**。{cite('early_city')}{cite('city2end')}{cite('early_ski_unmatched')}",
      f"- 若8天改留寿都威斯汀三床4晚，只保持同一机票和札幌房的量级比较，机酒约**{money(westin_total)}**。这是不同雪场方案，不是可无缝换酒店；课费、交通和集合点要重做。{cite('westin4')}",
      f"- 留寿都Resort Hotel当前4晚列表显示{money(q['rusutsu_unresolved']['amount_cny'])}，但房名为`Standard Twin Room 2 Occupanacy`、未证第三床，**排除出预算**。不把稀缺库存的高价当酒店通常价，也不把改为两人入住后的低价当家庭三人价。{cite('rusutsu_unresolved')}",
      '- 原12天版只读到三人往返机票样本，未凑齐同标准11晚酒店，故不编造“比原版省几万元”。',
      '### 8天怎么缩：砍转场，不砍掉全部训练',
      '| 日期 | 住宿与安排 |', '|---|---|',
      '| 1/30 | 飞抵新千岁，札幌住1晚；17:50到达的样本不再连夜赶富良野 |',
      '| 1/31 | 白天转富良野，住4晚；入住、取器材、熟悉学校集合点，不把转场算训练日 |',
      '| 2/1—2/3 | 保留3个完整雪日；建议2天教学＋1天巩固/休息，若想3天全课先确认体力、进阶目标与午餐责任 |',
      '| 2/4 | 白天回札幌，住2晚；看雪祭，预留冬季交通余量 |',
      '| 2/5 | 札幌雪祭／城市家庭日；温泉尽量用雪场酒店设施，不另搬一晚温泉旅馆 |',
      '| 2/6 | 从札幌前往新千岁返京；返程班次尚未选定，确定后核雪天出门缓冲 |',
      '**短版取舍**：取消独立洞爷湖/登别两晚和旭川过夜段，保留一个雪场基地。富良野区与北之峰区不是同一上课集合点，先问FISS是否能在新王子侧接课；若不能，先换酒店/学校，不默认免费跨区接送。[2][3]',
      '### 未包含的费用与下一步预算闸门',
      '- 以上只是**机票＋酒店**，绝不冒充全家旅行总价。早餐和正餐、两段雪场接驳、机场交通、滑雪课、雪票、雪具/衣物、签证保险、地方税、汇兑费均另计。',
    ]
    rate=Decimal(json.loads((ROOT/'data/hokkaido-2027-fx.json').read_text())['rate'])
    lesson=54600*3;cny=int((Decimal(lesson)*rate).quantize(Decimal('1'),rounding=ROUND_HALF_UP))
    lines += [f'- 若另取FISS公开普通价5小时私教3天，按每位教练54600日元/天（约人民币{int((Decimal(54600)*rate).quantize(Decimal("1"),rounding=ROUND_HALF_UP)):,}元），3天163800日元（约人民币{cny:,}元）；仅数学示例，不保证午餐看护、指定教练或3天连续空档，也不是已包含课程。早鸟须在10/31前满足学校条件，不能默认所有人享受。[3][11]',
      '- **本轮已核组合的3人机酒尚未压到3万元以内**；若目标是更低，应优先重查非雪场酒店、避雪祭最后两晚或缩成7天，而不是拿双人房、跨夜最低票和免费拼班凑账。尚未完成的7天改价不报虚构总额。',
      '- 下单前确认：是否2大1小还是有老人、可用年假、总预算上限、是否接受香港绕行/红眼、毛豆板类与水平。优先可退房，机票选好返程和行李后一起重核，不先买不可退课。',
      '[预算结构化数据](../data/hokkaido-2027-budget.json) · [带采集时间的列表文本证据](../data/hokkaido-2027-budget-evidence.json) · 下方仍保留原12天长版，不能把其五天课费与本短版相加成同一订单。', '']
    result=''
    previous=''
    for line in lines:
        result += ('\n' if line.startswith('|') and previous.startswith('|') else '\n\n') + line
        previous=line
    return result.strip()+'\n'
