"""Check every displayed JPY price has a correct adjacent RMB estimate."""
import json,re
from decimal import Decimal, ROUND_HALF_UP
from pathlib import Path
from bs4 import BeautifulSoup
ROOT=Path(__file__).resolve().parents[1]
raw=(ROOT/'data/hokkaido-2027-plan.md').read_text().partition('## Sources')[0]
s=BeautifulSoup((ROOT/'pages/spring-festival-2027-hokkaido-ski-onsen.html').read_text(),'html.parser')
fx=json.loads((ROOT/'data/hokkaido-2027-fx.json').read_text())
prices=s.select('.jpy-price')
expected=re.findall(r'(?<![\d,])(\d{1,3}(?:,\d{3})+)',raw)
assert len(prices)==len(expected) and len(prices)>40,(len(prices),len(expected))
for node,original in zip(prices,expected):
 amount=int(original.replace(',',''));assert int(node['data-jpy'])==amount
 result=int((Decimal(amount)*Decimal(fx['rate'])).quantize(Decimal('1'),rounding=ROUND_HALF_UP))
 assert node.select_one('.cny-estimate').get_text()==f'（约人民币{result:,}元）'
 assert str(node.contents[0])==original+'日元'
assert not s.select('#sources .jpy-price')
text=s.select_one('#coaches').get_text(' ',strip=True)
for term in ['成田伊織','押切凌','木村公宣','Miyuki Sakurai','Joshua Duncan-Smith','Akiko Irie','Alex','13岁以上','日语','SAJ级别2级','未确认']:
 assert term in text,term
rows=s.select('#coaches tbody tr')
assert len(rows)==12,len(rows)
print(json.dumps({'converted_prices':len(prices),'rate':fx['rate'],'rounding':'half-up CNY','named_coaches':len(rows),'japanese_language_age_limits':True},ensure_ascii=False))
