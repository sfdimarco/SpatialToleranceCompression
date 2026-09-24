import os, urllib.request
from PIL import Image, ImageDraw
for n in ["03","05","15","23"]:
    if not os.path.exists(f"kodim{n}.png"): urllib.request.urlretrieve(f"https://r0k.us/graphics/kodak/kodak/kodim{n}.png", f"kodim{n}.png")
import random
random.seed(7)
for n in ["03","05","15","23"]:
    im=Image.open(f"kodim{n}.png").convert("RGB"); w,h=im.size
    im.crop(((w-512)//2,(h-512)//2,(w-512)//2+512,(h-512)//2+512)).save(f"photo_kodim{n}.png")
S=2048
# flat vector illustration (antialiased by 4x supersample)
im=Image.new("RGB",(S,S),(120,190,235)); d=ImageDraw.Draw(im)
d.ellipse((1400,200,1800,600),fill=(255,214,90))
d.ellipse((-600,1100,1500,2900),fill=(90,170,90)); d.ellipse((700,1250,2800,3200),fill=(60,140,75))
d.polygon([(300,1500),(500,900),(700,1500)],fill=(40,100,60)); d.rectangle((470,1500,530,1650),fill=(110,70,40))
d.rectangle((1100,1100,1500,1500),fill=(230,90,70)); d.polygon([(1050,1100),(1300,850),(1550,1100)],fill=(150,50,50))
d.rectangle((1250,1300,1350,1500),fill=(80,50,30))
im.resize((512,512),Image.LANCZOS).save("illustration_flat.png")
# pixel art: 64x64 limited palette, 8x nearest
pal=[(20,20,40),(240,200,120),(200,60,60),(60,120,200),(250,250,250),(90,180,90)]
sm=Image.new("RGB",(64,64),pal[0]); p=sm.load()
for y in range(64):
    for x in range(64):
        if 16<=x<48 and 12<=y<52 and random.random()<0.85: p[x,y]=pal[1+((x//4+y//6)%5)]
        elif random.random()<0.03: p[x,y]=pal[4]
sm.resize((512,512),Image.NEAREST).save("pixelart.png")
# sparse line-art cel (~2% ink), antialiased
im=Image.new("RGB",(S,S),(255,255,255)); d=ImageDraw.Draw(im)
for _ in range(14):
    pts=[(random.randint(200,1850),random.randint(200,1850)) for _ in range(4)]
    d.line(pts,fill=(20,20,20),width=10,joint="curve")
d.ellipse((800,700,1250,1150),outline=(20,20,20),width=10)
im.resize((512,512),Image.LANCZOS).save("lineart_cel.png")
# UI screenshot-like
im=Image.new("RGB",(512,512),(245,246,248)); d=ImageDraw.Draw(im)
d.rectangle((0,0,512,48),fill=(40,44,52)); d.rectangle((0,48,120,512),fill=(230,232,236))
for i in range(8): d.rectangle((140,70+i*52,490,110+i*52),fill=(255,255,255),outline=(210,212,218))
for i in range(8): d.text((152,82+i*52),f"Item number {i+1}  status: ok",fill=(30,30,30))
for i in range(6): d.text((12,70+i*30),f"Menu {i}",fill=(60,60,60))
d.text((12,16),"Dashboard",fill=(255,255,255))
im.save("ui_screenshot.png")
import numpy as np
for f in ["lineart_cel.png","pixelart.png","illustration_flat.png","ui_screenshot.png"]:
    a=np.asarray(Image.open(f).convert("L")); print(f, "non-white/ink frac" , round(float((a<200).mean()),4))
random.seed(3)
im=Image.new("RGB",(S,S),(255,255,255)); d=ImageDraw.Draw(im)
for _ in range(3):
    pts=[(random.randint(300,1700),random.randint(300,1700)) for _ in range(3)]
    d.line(pts,fill=(20,20,20),width=10,joint="curve")
im.resize((512,512),Image.LANCZOS).save("lineart_sparse.png")
