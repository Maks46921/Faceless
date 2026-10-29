import sys,os
from PIL import Image
A=sys.argv[1]; items=[l.split() for l in open(os.path.join(A,'props.txt'))]
W=1000; x=y=0; rowh=0; places=[]
for nm,w,h,n in items:
    im=Image.open(os.path.join(A,'props',nm+'.png'))
    if x+im.size[0]>W: x=0; y+=rowh+4; rowh=0
    places.append((im,x,y)); x+=im.size[0]+4; rowh=max(rowh,im.size[1])
out=Image.new('RGBA',(W,y+rowh),(70,72,80,255))
for im,x,y in places: out.alpha_composite(im.convert('RGBA'),(x,y))
out=out.resize((out.size[0]*2,out.size[1]*2),Image.NEAREST); out.save(sys.argv[2])
print(out.size)
