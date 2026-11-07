# Метрики всех фото старых карточек WB: резкость hf по изделию, dhash (для поиска служебных картинок), доля белого
import json,io,urllib.request,concurrent.futures as cf
import numpy as np
from PIL import Image
C=json.load(open('wbcheck/cards.json'))
def get(u):
    for i in range(4):
        try: return urllib.request.urlopen(urllib.request.Request(u,headers={'User-Agent':'Mozilla/5.0'}),timeout=60).read()
        except Exception: pass
def feat(im):
    im=im.convert('RGB');w,h=im.size;a=np.asarray(im).astype(np.int16);mn=a.min(2);sat=a.max(2)-mn
    bg=(mn>=236)&(sat<=14);fg=~bg
    g=np.asarray(im.convert('L'),dtype=np.float32)
    sm=np.asarray(im.convert('L').resize((w//2,h//2),Image.LANCZOS).resize((w,h),Image.LANCZOS),dtype=np.float32)
    hf=float(np.abs(g-sm)[fg].mean()) if fg.sum()>1000 else 0
    s=np.asarray(im.convert('L').resize((9,8),Image.LANCZOS),dtype=np.int16);dh=''.join('1' if x else '0' for x in (s[:,1:]>s[:,:-1]).flatten())
    skin=(((a[...,0]>150)&(a[...,0]>a[...,1]+15)&(a[...,1]>a[...,2]))).mean()
    return dict(hf=round(hf,2),white=round(float(bg.mean()),3),skin=round(float(skin),3),dh=hex(int(dh,2)))
def card(c):
    out=[]
    for k,u in enumerate(c['photos']):
        b=get(u)
        if not b: out.append(dict(i=k+1,err=1));continue
        m=feat(Image.open(io.BytesIO(b)));m['i']=k+1;out.append(m)
    return dict(nm=c['nm'],vc=c['vc'],photos=out)
with cf.ThreadPoolExecutor(8) as ex: R=list(ex.map(card,C))
json.dump(R,open('wbcheck/out/metrics2.json','w'),ensure_ascii=False)
print('done')
