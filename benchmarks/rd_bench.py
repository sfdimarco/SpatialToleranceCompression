import subprocess, os, io, json, glob
import numpy as np
from PIL import Image
from skimage.metrics import peak_signal_noise_ratio as psnr, structural_similarity as ssim
import sys
G=sys.argv[1] if len(sys.argv)>1 else "../go/geocoder"
def load(p): return np.asarray(Image.open(p).convert("RGB"))
def m(a,b): return psnr(a,b,data_range=255), ssim(a,b,channel_axis=2,data_range=255)
res={}
for f in sorted(glob.glob("*.png")):
    if f.startswith("kodim"): continue
    ref=load(f); r={"geoi":[],"jpeg":[]}
    for q in [255,254,252,250,248,245,240,235,230,220,200,180,150,100,50]:
        subprocess.run([G,"encode","-i",f,"-o","t.geoi","-q",str(q)],check=True,capture_output=True)
        subprocess.run([G,"decode","-i","t.geoi","-o","t.png"],check=True,capture_output=True)
        dec=load("t.png")[:512,:512]; p,s=m(ref,dec)
        r["geoi"].append((q,os.path.getsize("t.geoi"),p,s))
    for q in [100,98,95,92,90,85,80,75,70,60,50,40,30,20,10]:
        b=io.BytesIO(); Image.fromarray(ref).save(b,"JPEG",quality=q); n=b.tell(); b.seek(0)
        p,s=m(ref,load(b)); r["jpeg"].append((q,n,p,s))
    b=io.BytesIO(); Image.fromarray(ref).save(b,"PNG",optimize=True); r["png"]=b.tell()
    b=io.BytesIO(); Image.fromarray(ref).save(b,"WEBP",lossless=True,method=6); r["webp_ll"]=b.tell()
    res[f]=r
json.dump(res,open("results.json","w"))
for f,r in res.items():
    print("\n==",f,"PNG",r["png"],"WebP-lossless",r["webp_ll"])
    print(" geoi q=255 (lossless?)", r["geoi"][0])
    for row in r["geoi"]: print("  geoi q=%3d %7d B  PSNR %6.2f  SSIM %.4f"%row)
    for row in r["jpeg"][:10]: print("  jpeg q=%3d %7d B  PSNR %6.2f  SSIM %.4f"%row)
