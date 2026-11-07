# Скачивает фото старых карточек WB, считает метрики и собирает контактные листы
import json,io,os,urllib.request,concurrent.futures as cf
import numpy as np
from PIL import Image,ImageDraw
C=json.load(open('wbcheck/cards.json'));os.makedirs('wbcheck/out/sheets',exist_ok=True);os.makedirs('wbcheck/out/first',exist_ok=True)
def get(u):
    for i in range(4):
        try: return urllib.request.urlopen(urllib.request.Request(u,headers={'User-Agent':'Mozilla/5.0'}),timeout=60).read()
        except Exception: pass
    return None
def metr(im):
    g=np.asarray(im.convert('L'),dtype=np.float32)
    lap=g[1:-1,1:-1]*4-g[:-2,1:-1]-g[2:,1:-1]-g[1:-1,:-2]-g[1:-1,2:]
    a=np.asarray(im.convert('RGB')).astype(np.int16);mn=a.min(2);mx=a.max(2)
    white=((mn>=236)&((mx-mn)<=14)).mean()
    return dict(w=im.size[0],h=im.size[1],sharp=round(float(lap.var()),1),white=round(float(white),3))
def card(c):
    res=[];ims=[]
    for k,u in enumerate(c['photos']):
        b=get(u)
        if not b: res.append(dict(i=k+1,err=1));ims.append(None);continue
        im=Image.open(io.BytesIO(b));im.load();m=metr(im);m['i']=k+1;m['kb']=len(b)//1024;res.append(m)
        if k==0: im.convert('RGB').save(f"wbcheck/out/first/{c['nm']}.jpg",quality=88)
        t=im.convert('RGB');t.thumbnail((180,240));ims.append(t)
    return dict(nm=c['nm'],vc=c['vc'],subj=c['subj'],photos=res),ims
R=[];rows=[]
with cf.ThreadPoolExecutor(8) as ex:
    for r,ims in ex.map(card,C): R.append(r);rows.append((r['vc'],ims))
json.dump(R,open('wbcheck/out/metrics.json','w'),ensure_ascii=False,indent=0)
for s in range(0,len(rows),12):
    part=rows[s:s+12];W=200+10*185;H=len(part)*250
    sh=Image.new('RGB',(W,H),'white');d=ImageDraw.Draw(sh)
    for j,(vc,ims) in enumerate(part):
        d.text((5,j*250+110),vc[:28],fill='black')
        for k,t in enumerate(ims[:10]):
            if t: sh.paste(t,(200+k*185,j*250+5))
            d.text((200+k*185,j*250+235),str(k+1),fill='red')
    sh.save(f'wbcheck/out/sheets/s{s//12:02d}.jpg',quality=80)
print('done',len(R),'errors',sum(1 for r in R for p in r['photos'] if p.get('err')))
