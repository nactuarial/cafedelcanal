# Convert a photo into a watercolor painting: few light, transparent washes over a pencil
# underdrawing, uneven pigment with wet blooms, darker pigment pooled at wash borders,
# lots of white paper and cold-press grain.
import sys, numpy as np
from PIL import Image, ImageFilter
src, dst = sys.argv[1], sys.argv[2]
im = Image.open(src).convert('RGB')
im = im.resize((im.width*2, im.height*2), Image.LANCZOS)
rgb = np.asarray(im, dtype=np.float32)/255
H, W = rgb.shape[:2]
rng = np.random.default_rng(5)
def to_img(a): return Image.fromarray((np.clip(a,0,1)*255).astype(np.uint8))
def blur(a, r): return np.asarray(to_img(a).filter(ImageFilter.GaussianBlur(r)),np.float32)/255
def lum(a): return a @ np.array([.299,.587,.114], np.float32)
def noise(r): n = blur(rng.random((H,W),np.float32), r); return (n-n.min())/(np.ptp(n)+1e-6)
paper = np.array([.99,.975,.94], np.float32)
# big simple shapes: paint at quarter size, then bring back up
small = to_img(rgb).resize((W//4, H//4), Image.LANCZOS)
for _ in range(2): small = small.filter(ImageFilter.MedianFilter(5))
simp = np.asarray(small.resize((W, H), Image.BICUBIC).filter(ImageFilter.GaussianBlur(3)), np.float32)/255
sg = lum(simp)[..., None]
simp = sg+(simp-sg)*1.5
# wet bleeding
yy, xx = np.mgrid[0:H, 0:W]
dx = (noise(22)-.5)*22; dy = (noise(22)-.5)*22
wash = simp[np.clip((yy+dy).astype(int),0,H-1), np.clip((xx+dx).astype(int),0,W-1)]
# transparent, high-key pigment: lift the darks, leave highlights as bare paper
amt = np.clip((1-lum(wash))*1.25, 0, 1)
amt = np.where(lum(wash) > .8, amt*.25, amt)
# uneven pigment and wet-in-wet blooms
blot = noise(30)
bloom = noise(14)
rings = np.exp(-((bloom-.55)/.035)**2)   # thin darker rings where blooms dried
dens = np.clip(.55+.5*blot+.18*rings, .35, 1.1)
k = (amt*dens*.8)[..., None]
out = paper-(paper-wash)*np.clip(k*1.15, 0, .85)
# pigment pooling at the wash borders
gy, gx = np.gradient(blur(lum(wash), 2))
edge = np.clip(np.hypot(gx, gy)*18, 0, 1)
out = out*(1-.22*edge)[..., None]
# granulation and paper tooth
gran = noise(.8); tooth = noise(2.5)
out = out*((1-(gran-.5)*.12*(1.1-lum(out)))*(1-(tooth-.5)*.07))[..., None]
# pencil underdrawing
g = lum(rgb)
sk = np.clip(g/np.maximum(1-blur(1-g, 2.5), 1e-3), 0, 1)**3.5
out = out*(1-(1-sk)*.5)[..., None]
to_img(out).save(dst, quality=82, optimize=True, progressive=True)
