"""Entrance canopy (state_ok / state_loose / state_broken + debris + 'collapse' animation) and an electrical panel (door open/closed, cut wire with ip_spark).
Run: D:\\Cosmoteer\\blender.exe -b -P D:\\Faceless\\models\\src\\build_canopy_panel.py"""
exec(open("D:/Faceless/models/src/lib_props.py", encoding="utf-8").read())
smoothdeg = 40

def rebar(p0, p1, r=.008, parent=None, name="rebar"):
    p0, p1 = Vector(p0), Vector(p1); d = p1 - p0; mid = (p0 + p1) / 2
    o = cyl(r, d.length, MATS["rebar_rust"], loc=tuple(mid), seg=6, name=name, parent=parent)
    o.rotation_mode = 'QUATERNION'; o.rotation_quaternion = Vector((0, 0, 1)).rotation_difference(d.normalized()); o.rotation_mode = 'XYZ'
    return o

# =====================================================================  CANOPY
fresh(); palette()
C, CD, RB, ST = MATS["concrete"], MATS["concrete_dark"], MATS["rebar_rust"], MATS["steel_dark"]
SLAB_H, SLAB_Z, DEPTH, HALF = .12, 2.5, 1.15, 1.1
# ---- wall with a door opening (always visible)
wall = empty("wall_stub", size=.2)
box((.95, .28, 3.5), C, loc=(-1.125, .14, 1.75), bev=.006, parent=wall, name="pier_l")
box((.95, .28, 3.5), C, loc=(1.125, .14, 1.75), bev=.006, parent=wall, name="pier_r")
box((1.3, .28, 1.2), C, loc=(0, .14, 2.9), bev=.006, parent=wall, name="lintel")
box((1.28, .06, 2.3), ST, loc=(0, .18, 1.15), bev=.004, parent=wall, name="door_leaf")
box((.05, .03, .22), MATS["steel"], loc=(.5, .125, 1.1), bev=.004, parent=wall, name="door_handle")
box((1.38, .03, .05), CD, loc=(0, .01, 2.32), bev=0, parent=wall, name="seam_h")
for sx in (-1.6, -.65, .65, 1.6): pass
box((.04, .3, 3.5), CD, loc=(-.65, .14, 1.75), bev=0, parent=wall, name="seam_v1")
box((.04, .3, 3.5), CD, loc=(.65, .14, 1.75), bev=0, parent=wall, name="seam_v2")
box((1.4, .3, .1), MATS["concrete_dark"], loc=(0, .14, .05), bev=.004, parent=wall, name="step")
box((3.6, .3, 3.5), None, loc=(0, .14, 1.75), bev=0, name="wall_stub-col")

def slab_box(name, parent, z=SLAB_Z, cracked=False):
    box((2 * HALF, DEPTH, SLAB_H), C, loc=(0, -DEPTH / 2 - .02, z), bev=.01, parent=parent, name=name, seg=2)
    box((2 * HALF, .05, .06), C, loc=(0, -DEPTH - .02, z + SLAB_H / 2 + .02), bev=.006, parent=parent, name=name + "_lip")
    box((2 * HALF - .1, DEPTH - .12, .05), CD, loc=(0, -DEPTH / 2 - .04, z - SLAB_H / 2 - .02), bev=.004, parent=parent, name=name + "_under")
    box((.14, DEPTH - .1, .1), CD, loc=(-.6, -DEPTH / 2, z - SLAB_H / 2 - .06), bev=.004, parent=parent, name=name + "_beam")
    box((.14, DEPTH - .1, .1), CD, loc=(.6, -DEPTH / 2, z - SLAB_H / 2 - .06), bev=.004, parent=parent, name=name + "_beam")

def rods(parent, left=True, right=True, z=SLAB_Z, sag=0.0):
    for sx, ok in ((-1, left), (1, right)):
        if not ok: continue
        box((.1, .02, .1), ST, loc=(sx * 1.0, .0, 3.15), bev=.003, parent=parent, name="wall_plate")
        r_ = rebar((sx * 1.0, .0, 3.15), (sx * 1.0, -DEPTH + .1, z + SLAB_H / 2 + .02 + sag), r=.014, parent=parent, name="tie_rod")
        r_.data.materials.clear(); r_.data.materials.append(ST)

# ---- state_ok
so = empty("state_ok"); slab_box("slab", so); rods(so)
# ---- state_loose : sagging, one tie rod snapped and hanging, cracks and chips
sl = empty("state_loose"); pivot = empty("sag_pivot", (0, 0, SLAB_Z + .06), parent=sl)
sub = empty("slab_sag", (0, 0, 0), parent=pivot); slab_box("slab", sub, z=SLAB_Z - (SLAB_Z + .06) + .0)
pivot.rotation_euler = (.1, 0, .02)
rods(sl, left=True, right=False)
rebar((1.0, .0, 3.15), (1.02, -.1, 2.55), r=.014, parent=sl, name="tie_rod_snapped").data.materials.append(ST)
for i, (cx, cy) in enumerate(((-.5, -.5), (.2, -.3), (.6, -.8), (.0, -.95))):
    box((.5 + .1 * i, .015, .008), CD, loc=(cx, cy, SLAB_Z + .1), bev=0, rot=(0, 0, .7 * (i - 1.5)), parent=sl, name="crack")
rebar((.5, -1.15, SLAB_Z - .02), (.5, -1.28, SLAB_Z - .05), r=.01, parent=sl, name="rebar_peek")
for i in range(3): box((.08, .06, .05), C, loc=(-.7 + .5 * i, -1.2 - .05 * i, .05), bev=.008, rot=(.3 * i, .2, .5 * i), parent=sl, name="chip")
# ---- broken pieces (shared geometry with the collapse animation)
zig_a = [(-HALF, 0), (HALF, 0), (HALF, -.62), (.75, -.7), (.42, -.58), (0, -.72), (-.4, -.6), (-.8, -.71), (-HALF, -.6)]
zig_b = [(-HALF, -.6), (-.8, -.71), (-.4, -.6), (0, -.72), (.42, -.58), (.75, -.7), (HALF, -.62), (HALF, -DEPTH), (-HALF, -DEPTH)]
def piece(name, pts, parent, loc=(0, 0, 0)):
    return poly_prism(pts, SLAB_H, C, loc=loc, parent=parent, name=name, bev=.008)
def stubs(parent, pts, z0=0, ang=0):
    for i in range(4):
        x = -.8 + i * .55
        rebar((x, -.64, z0 + SLAB_H / 2), (x, -.64 - .14, z0 + SLAB_H / 2 - .02), r=.009, parent=parent, name="rebar_stub")
# anim rig: pieces hinged at the wall
rig = empty("canopy_fall", size=.15)
ha = empty("slab_a_pivot", (0, 0, SLAB_Z - SLAB_H / 2), parent=rig)
pa = piece("slab_a", zig_a, ha); stubs(pa, zig_a)
hb = empty("slab_b_pivot", (0, -.65, SLAB_Z - SLAB_H / 2), parent=rig)
pb = piece("slab_b", [(x, y + .65) for x, y in zig_b], hb)
for i in range(4):
    x = -.8 + i * .55; rebar((x, -.0, SLAB_H / 2), (x, .12, SLAB_H / 2 - .03), r=.009, parent=pb, name="rebar_stub_b")
rods(rig, left=False, right=True)
# debris chunks (hidden in 'ok', pop in during the fall)
deb = empty("debris", size=.1); chunks = []
rnd = random.Random(4)
for i in range(10):
    c = rock_blob(.09 + .06 * rnd.random(), C, seed=20 + i, loc=(rnd.uniform(-1.0, 1.0), rnd.uniform(-1.4, -.5), .05), flat=.6, subdiv=1, rough=.3, parent=deb, name="chunk")
    chunks.append(c)
for i in range(5): rebar((rnd.uniform(-.9, .9), rnd.uniform(-1.4, -.6), .02), (rnd.uniform(-.9, .9), rnd.uniform(-1.4, -.6), .04), r=.009, parent=deb, name="rebar_piece")
# ---- state_broken: slab_a hanging at 38 deg from the wall, slab_b lying on the ground leaning against the wall edge, debris around
sb = empty("state_broken")
hha = empty("a_pivot", (0, 0, SLAB_Z - SLAB_H / 2), parent=sb); hha.rotation_euler = (.62, 0, .03)
pa2 = piece("slab_a", zig_a, hha); stubs(pa2, zig_a)
hhb = empty("b_pivot", (.25, -1.05, .08), parent=sb); hhb.rotation_euler = (-.12, 0, -.35)
pb2 = piece("slab_b", [(x, y + .65) for x, y in zig_b], hhb)
for i in range(4): rebar((-.8 + i * .55, 0, SLAB_H / 2), (-.8 + i * .55, .12, SLAB_H / 2 - .03), r=.009, parent=pb2, name="rebar_stub_b")
rods(sb, left=False, right=True)
rebar((-1.0, .0, 3.15), (-1.0, -.35, 2.6), r=.014, parent=sb, name="tie_rod_hang").data.materials.append(ST)
# ---- animation 'collapse' (36 frames @24): slab_b breaks away and drops, slab_a swings down, debris pops in
animate(ha, "collapse", [(1, dict(rot=(0, 0, 0))), (6, dict(rot=(.05, 0, 0))), (14, dict(rot=(.62, 0, .03))), (22, dict(rot=(.56, 0, .03))), (36, dict(rot=(.62, 0, .03)))])
animate(hb, "collapse", [(1, dict(loc=(0, -.65, SLAB_Z - SLAB_H / 2), rot=(0, 0, 0))), (8, dict(loc=(0, -.68, SLAB_Z - SLAB_H / 2 - .1), rot=(-.18, 0, 0))),
                         (16, dict(loc=(.2, -1.0, .6), rot=(-.55, 0, -.2))), (22, dict(loc=(.25, -1.05, .09), rot=(-.14, 0, -.3))), (26, dict(loc=(.25, -1.05, .13), rot=(-.08, 0, -.34))), (36, dict(loc=(.25, -1.05, .08), rot=(-.12, 0, -.35)))])
for k, c in enumerate(chunks):
    animate(c, "collapse", [(1, dict(scale=(.001, .001, .001))), (15 + k % 3, dict(scale=(.001, .001, .001))), (19 + k % 3, dict(scale=(1, 1, 1))), (36, dict(scale=(1, 1, 1)))])
# collision / interaction points
box((2.2, 1.2, .12), None, loc=(0, -.6, SLAB_Z), bev=0, name="canopy-convcol")
empty("ip_hit", (0, -.85, 0), size=.2); empty("ip_use", (1.55, -.45, 0), size=.2)
smooth_angle([o for o in bpy.data.objects if o.type == 'MESH'], smoothdeg)
export("canopy", anims=True)

# =====================================================================  ELECTRICAL PANEL
fresh(); palette()
PG, PY = MATS["paint_gray"], MATS["paint_yellow"]; CD = MATS["concrete_dark"]
wallp = empty("wall_section", size=.1)
box((1.3, .12, 2.6), MATS["concrete"], loc=(0, .06, 1.3), bev=.006, parent=wallp, name="wall")
box((1.3, .14, .12), CD, loc=(0, .07, .06), bev=.004, parent=wallp, name="skirting")
box((1.34, .02, 2.2), MATS["paint_green"], loc=(0, -.005, .7), bev=0, parent=wallp, name="paint_band")
W, H, D, Z0 = .62, .86, .17, 1.05
box((W + .06, .02, H + .06), CD, loc=(0, -.01, Z0 + H / 2), bev=.002, parent=wallp, name="frame_back")
box((.03, D, H), PG, loc=(-W / 2, -D / 2, Z0 + H / 2), bev=.003, parent=wallp, name="cab_l")
box((.03, D, H), PG, loc=(W / 2, -D / 2, Z0 + H / 2), bev=.003, parent=wallp, name="cab_r")
box((W, D, .03), PG, loc=(0, -D / 2, Z0 + H - .015), bev=.003, parent=wallp, name="cab_top")
box((W, D, .03), PG, loc=(0, -D / 2, Z0 + .015), bev=.003, parent=wallp, name="cab_bottom")
box((W - .06, .01, H - .06), MATS["steel_dark"], loc=(0, -.01, Z0 + H / 2), bev=0, parent=wallp, name="backplate")
for r in range(3):
    for c in range(8):
        box((.04, .028, .05), MATS["plastic_black"], loc=(-.25 + c * .07, -.03, Z0 + .22 + r * .2), bev=.002, parent=wallp, name="breaker")
        box((.014, .012, .02), MATS["steel"], loc=(-.25 + c * .07, -.048, Z0 + .22 + r * .2 + (.012 if (r + c) % 3 else -.012)), bev=.001, parent=wallp, name="switch")
    box((.5, .012, .006), MATS["steel"], loc=(0, -.025, Z0 + .22 + r * .2 + .04), bev=0, parent=wallp, name="rail")
for i in range(4):
    box((.03, .02, .04), MATS["wire_black"] if i % 2 else MATS["wire_red"], loc=(-.2 + i * .13, -.035, Z0 + .8), bev=.002, parent=wallp, name="terminal")
box((.12, .01, .1), PY, loc=(-.2, -D - .005, Z0 + H - .12), bev=0, parent=wallp, name="warning_plate")

def door(name, parent, loc, rot):
    hinge = empty(name, loc, parent=parent, rot=rot, size=.05)
    box((W - .01, .025, H - .01), PG, loc=((W - .01) / 2, -.0125, 0), bev=.004, parent=hinge, name=name + "_leaf")
    box((.1, .01, .1), PY, loc=(.15, -.03, .22), bev=0, parent=hinge, name=name + "_sign")
    box((.04, .03, .12), MATS["steel"], loc=(W - .07, -.035, 0), bev=.004, parent=hinge, name=name + "_handle")
    box((.02, .02, .02), MATS["steel"], loc=(W - .07, -.055, .0), bev=.002, parent=hinge, name=name + "_lock")
    return hinge
HX = -W / 2
so = empty("state_ok"); door("door_closed", so, (HX, -D, Z0 + H / 2), (0, 0, 0))
sl = empty("state_loose"); door("door_open", sl, (HX, -D, Z0 + H / 2), (0, 0, 1.9))
# cut wire: black + red hanging from the lower terminals, copper ends
def hang(name, x, mat_, parent):
    cu = bpy.data.curves.new(name, 'CURVE'); cu.dimensions = '3D'; cu.bevel_depth = .006; cu.resolution_u = 6; cu.use_fill_caps = True
    sp = cu.splines.new('BEZIER'); sp.bezier_points.add(2)
    pts = [(x, -.035, Z0 + .22), (x + .04, -.1, Z0 - .05), (x + .02, -.12, Z0 - .45)]
    for bp, p in zip(sp.bezier_points, pts): bp.co = p; bp.handle_left_type = bp.handle_right_type = 'AUTO'
    o = bpy.data.objects.new(name, cu); collection().objects.link(o); set_active(o); bpy.ops.object.convert(target='MESH'); o = bpy.context.object
    o.data.materials.append(mat_); o.parent = parent
    return pts[-1]
e1 = hang("wire_cut_a", .08, MATS["wire_red"], sl); e2 = hang("wire_cut_b", .15, MATS["wire_black"], sl)
for e in (e1, e2): cyl(.0045, .04, MATS["copper"], loc=(e[0], e[1], e[2] - .02), seg=6, parent=sl, name="copper_tip")
empty("ip_spark", (e1[0], e1[1], e1[2] - .04), parent=sl, size=.08, display='SPHERE')
empty("ip_spark_2", (e2[0], e2[1], e2[2] - .04), parent=sl, size=.08, display='SPHERE')
empty("ip_spark_box", (-.2, -.06, Z0 + .5), parent=sl, size=.08, display='SPHERE')
# animated door for the transition
dd = door("door_anim", None, (HX, -D, Z0 + H / 2), (0, 0, 0))
animate(dd, "open", [(1, dict(rot=(0, 0, 0))), (6, dict(rot=(0, 0, -.06))), (18, dict(rot=(0, 0, 1.9)))])
animate(dd, "close", [(1, dict(rot=(0, 0, 1.9))), (14, dict(rot=(0, 0, .1))), (18, dict(rot=(0, 0, 0)))])
box((.7, .3, .95), None, loc=(0, -.12, Z0 + H / 2), bev=0, name="panel-col"); box((1.3, .12, 2.6), None, loc=(0, .06, 1.3), bev=0, name="wall-col")
empty("ip_use", (0, -.75, 0), size=.2); empty("ip_hand", (W / 2 - .07 + HX + W / 2 - W / 2, -D - .06, Z0 + H / 2), size=.06)
smooth_angle([o for o in bpy.data.objects if o.type == 'MESH'], smoothdeg)
export("panel_electric", anims=True)
