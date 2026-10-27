"""Regression checks for evidence-bounded named coach additions."""
import json
from pathlib import Path
from bs4 import BeautifulSoup
ROOT=Path(__file__).resolve().parents[1]
s=BeautifulSoup((ROOT/'pages/spring-festival-2027-hokkaido-ski-onsen.html').read_text(),'html.parser')
c=s.select_one('#coaches')
assert c is not None, 'Named coach section is required'
assert s.select_one('.toc a[href="#coaches"]')
text=c.get_text(' ',strip=True)
for term in ('John John','牛牛','儿童','未确认','准四级','单板','双板'):
    assert term in text, term
assert len(c.select('tbody tr'))>=5
assert len(c.select('sup a[href^="#source-"]'))>=5
assert '指定' in text and '性价比' in text
ledger=json.loads((ROOT/'data/hokkaido-2027-citations.json').read_text())
assert len(s.select('#sources li'))==len(ledger['sources'])
for a in s.select('a[href^="#"]'):
    assert s.find(id=a['href'][1:]), a['href']
print(json.dumps({'named_coaches':len(c.select('tbody tr')),'sources':len(ledger['sources']),'coach_section':True,'citation_anchors':True},ensure_ascii=False))
