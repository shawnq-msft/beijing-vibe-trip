"""Archive article photos with DOM context; no inferred route geolocation."""
from pathlib import Path
from urllib.parse import urljoin
import json,io,requests
from bs4 import BeautifulSoup
from PIL import Image,ImageOps,ImageDraw
ROOT=Path(__file__).resolve().parents[1]
URL='https://xinwen.bjd.com.cn/content/s6ab3cabae4b0e42f8f00ba4f.html?innerId=1'
r=requests.get(URL,timeout=40);r.raise_for_status();r.encoding='utf-8'
soup=BeautifulSoup(r.text,'html.parser')
rows=[];thumbs=[]
for i,img in enumerate([i for i in soup.select('img') if 'dams-res/editing/image/202609/23/' in i.get('src','')],1):
    url=urljoin(URL,img['src']);r=requests.get(url,headers={'User-Agent':'Mozilla/5.0','Referer':URL},timeout=40);r.raise_for_status()
    im=Image.open(io.BytesIO(r.content)).convert('RGB');im.thumbnail((1600,1600))
    path=f'assets/wenyu-cycling/greenway/report-sep-{i}.webp';(ROOT/path).parent.mkdir(exist_ok=True,parents=True);im.save(ROOT/path,'WEBP',quality=87)
    context=' | '.join(x.get_text(' ',strip=True)[:450] for x in img.parent.find_previous_siblings(limit=2))
    rows.append({'id':f'greenway-{i}','path':path,'source_url':URL,'image_url':url,'publisher':'北京日报客户端','source_date':'2026-09-23','credit':'报道署名：胡子傲、潘之望、杨易铮；单图摄影未单独标注','width':im.width,'height':im.height,'context':context,'caption':{1:'报道全线示意图（非本次往返轨迹）',2:'林荫路上的休闲骑行｜区域参考实景',3:'树冠遮荫与铺装道路｜区域参考实景',4:'林间道路与斑驳树影｜区域参考实景'}[i],'visual_review':'照片主体已通过视觉检查；无可确认两闸间位置的路牌','verified_route_segment':False})
    (ROOT/'data/wenyu-greenway-photos.json').write_text(json.dumps(rows,ensure_ascii=False,indent=2)+'\n')
    thumb=ImageOps.contain(im,(600,400));panel=Image.new('RGB',(620,440),'white');panel.paste(thumb,((620-thumb.width)//2,30));ImageDraw.Draw(panel).text((10,10),str(i),fill='black');thumbs.append(panel)
    print(json.dumps(rows[-1],ensure_ascii=False))
canvas=Image.new('RGB',(1240,880),'#ddd')
for i,im in enumerate(thumbs):canvas.paste(im,((i%2)*620,(i//2)*440))
canvas.save('/tmp/wenyu-greenway-contact.jpg')
