"""Archive original reporting and its images, with attribution metadata."""
from pathlib import Path
from io import BytesIO
from urllib.parse import urljoin
import requests,json
from bs4 import BeautifulSoup
from PIL import Image
ROOT=Path(__file__).resolve().parents[1]
u='https://xinwen.bjd.com.cn/content/s6a86ac84e4b0e45f3fd6436a.html'
r=requests.get(u,timeout=30);r.raise_for_status();r.encoding='utf-8'
s=BeautifulSoup(r.text,'html.parser')
a=ROOT/'assets/wenyu-cycling';a.mkdir(exist_ok=True)
records=[]
for i,img in enumerate(s.select('img[src*="dams-res/editing/image/202608/20/"]')):
    src=urljoin(u,img['src']);rr=requests.get(src,timeout=30);rr.raise_for_status()
    im=Image.open(BytesIO(rr.content)).convert('RGB')
    p=a/f'report-{i+1}.webp';im.save(p,'WEBP',quality=88)
    records.append({'file':str(p.relative_to(ROOT)),'source_url':u,'image_url':src,'source_date':'2026-08-20','credit':'北京日报客户端，记者胡子傲；报道配图','width':im.width,'height':im.height})
    print(records[-1])
(ROOT/'data/wenyu-image-sources.json').write_text(json.dumps(records,ensure_ascii=False,indent=2))
(ROOT/'data/wenyu-official-source.json').write_text(json.dumps({'source_url':u,'access_date':'2026-10-10','source_date':'2026-08-20','text':s.get_text('\n',strip=True),'images':records},ensure_ascii=False,indent=2))
