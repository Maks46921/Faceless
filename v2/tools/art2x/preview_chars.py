import sys, os
from PIL import Image
from common import *
A = sys.argv[1]
C = 48
frames = {}
for line in open(os.path.join(A, "fig", "frames.txt")):
    k, v = line.split(); frames[k] = [int(x) for x in v.split(",")]
sheets = {}
def sh(n):
    if n not in sheets: sheets[n] = Image.open(os.path.join(A, "fig", n + ".png")).convert("RGBA")
    return sheets[n]
def colorize(img, pal):
    out = Image.new("RGBA", img.size, (0,0,0,0)); px = img.load(); po = out.load()
    for y in range(img.size[1]):
        for x in range(img.size[0]):
            p = px[x, y]
            if p[3] == 0: continue
            m = p[0] // 16; s = p[1] / 255.0 * 1.25
            c = pal.get(m, (255, 0, 255))
            po[x, y] = (min(255, int(c[0]*s)), min(255, int(c[1]*s)), min(255, int(c[2]*s)), 255)
    return out
def person(spec, fi):
    img = Image.new("RGBA", (C, C), (0,0,0,0))
    for n in spec["layers"]:
        fr = sh(n).crop((fi*C, 0, fi*C+C, C))
        img.alpha_composite(colorize(fr, spec["pal"]))
    return img
P1 = {"layers": ["armb","legs_pants","body","torso_coat","hair_short","beard_mustache","hat_fedora","scarf","armf","item_briefcase"],
      "pal": {0:(200,160,130),1:(60,45,35),2:(55,55,62),3:(40,40,44),4:(30,28,26),5:(70,60,50),6:(120,30,30),7:(20,20,20),8:(220,220,210),9:(150,150,160),10:(200,200,190),11:(140,40,40)}}
P2 = {"layers": ["armb","legs_skirt","body","torso_jacket","hair_bob","hat_beret","armf","item_bag"],
      "pal": {0:(225,185,160),1:(120,70,40),2:(140,40,50),3:(50,50,60),4:(30,28,26),5:(180,40,40),6:(90,60,40),7:(20,20,20),8:(220,220,210),9:(150,150,160),10:(220,220,210),11:(40,35,40)}}
P3 = {"layers": ["armb","legs_pants","body","torso_uniform","hair_short","hat_police","armf"],
      "pal": {0:(200,160,130),1:(40,35,30),2:(70,80,100),3:(60,70,90),4:(20,20,20),5:(70,80,100),6:(0,0,0),7:(20,20,20),8:(230,230,220),9:(160,160,170),10:(200,200,190),11:(170,40,40)}}
P4 = {"layers": ["armb","legs_skirt","body","torso_coat","hair_bun","hat_kerchief","armf","item_cane"],
      "pal": {0:(215,175,150),1:(150,150,150),2:(80,70,90),3:(60,50,60),4:(40,30,30),5:(150,60,80),6:(70,50,40),7:(20,20,20),8:(220,220,210),9:(150,150,160),10:(200,200,190),11:(80,70,70)}}
rows = []
order = ["idle","walk","run","jump","fall","climb","crouch","sneak","sit","lie","slump","carry","strangle","push","phone","smoke","talk","reach","look","kneel","choke","cower","stagger","walk_hunch","walk_limp"]
allf = []
for k in order: allf += frames[k]
W = len(allf)
for spec in (P1, P2, P3, P4):
    row = Image.new("RGBA", (W*C, C), (90, 95, 100, 255))
    for i, fi in enumerate(allf):
        row.alpha_composite(person(spec, fi), (i*C, 0))
    rows.append(row)
out = Image.new("RGBA", (W*C, C*4))
for i, r in enumerate(rows): out.paste(r, (0, i*C))
out = out.resize((out.size[0]*3, out.size[1]*3), Image.NEAREST)
# split into 3 chunks for viewing
n = 3; cw = out.size[0] // n + 1
for i in range(n):
    out.crop((i*cw, 0, min(out.size[0], (i+1)*cw), out.size[1])).save(sys.argv[2] + "_%d.png" % i)
