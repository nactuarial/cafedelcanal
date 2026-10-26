# Convert a photo into a colored-pencil drawing on paper: graphite contours (color dodge),
# colored pencil laid down in directional strokes, graphite shading in the darks, paper grain.
import sys, numpy as np
from PIL import Image, ImageFilter
src, dst = sys.argv[1], sys.argv[2]
im = Image.open(src).convert('RGB')
im = im.resize((im.width*2, im.height*2), Image.LANCZOS)
rgb = np.asarray(im, dtype=np.float32)/255
H, W = rgb.shape[:2]
rng = np.random.default_rng(11)
def to_img(a): return Image.fromarray((np.clip(a,0,1)*255).astype(np.uint8))
def blur(a, r): return np.asarray(to_img(a).filter(ImageFilter.GaussianBlur(r)),np.float32)/255
def lum(a): return a @ np.array([.299,.587,.114], np.float32)
def strokes(angle, length, seed):
    # random noise smeared along one direction = pencil strokes
    r = np.random.default_rng(seed)
    D = int(np.hypot(H, W))+4
    n = r.random((D, D), np.float32)
    n = (n > .62).astype(np.float32)*r.random((D,D),np.float32)
    c = np.cumsum(n, axis=1); s = (c[:, length:]-c[:, :-length])/length
    s = np.pad(s, ((0,0),(0,length)), mode='edge')
    big = to_img(s/s.max()).rotate(angle, resample=Image.BILINEAR)
    l, t = (D-W)//2, (D-H)//2
    a = np.asarray(big.crop((l, t, l+W, t+H)), np.float32)/255
    return (a-a.min())/(np.ptp(a)+1e-6)
paper = np.array([.975,.95,.9], np.float32)
g = lum(rgb)
# graphite contours
inv = blur(1-g, 4)
sk = np.clip(g/np.maximum(1-inv, 1e-3), 0, 1)**3
sk = 1-(1-sk)*.9
# colored pencil: flattened color, laid down unevenly along strokes
flat = blur(rgb, 2.2)
fg = lum(flat)[..., None]
flat = fg+(flat-fg)*1.15
s1 = strokes(52, 22, 1)
cover = np.clip(.42+.75*s1, 0, 1)[..., None]*np.clip(1.15-blur(g,3)[...,None]*.55, 0, 1)
col = paper+(flat-paper)*cover
# graphite shading in the darks, cross direction
tone = np.clip((1-blur(g, 2.5))-.35, 0, 1)/.65
s2 = strokes(-38, 16, 2)
shade = 1-.55*tone*np.clip(s2*1.4-.2, 0, 1)
grain = 1-(blur(rng.random((H,W),np.float32), .6)-.5)*.14
out = col*(sk*shade*grain)[..., None]
to_img(out).save(dst, quality=84, optimize=True, progressive=True)
