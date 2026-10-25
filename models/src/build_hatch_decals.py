"""Manhole (state_ok / state_loose, separate cover node, 'open'/'close' animation) and floor decals (blood, oil, puddle).
Run: D:\Cosmoteer\blender.exe -b -P D:\Faceless\models\src\build_hatch_decals.py"""
exec(open("D:/Faceless/models/src/lib_props.py", encoding="utf-8").read())

def cover(name, parent=None, loc=(0, 0, 0), rot=(0, 0, 0)):
    iron = MATS["cast_iron"]
    root = empty(name, loc, parent=parent, rot=rot, size=.05)
    lathe([(0, 0), (.35, 0), (.35, .036), (.33, .045), (0, .045)], iron, parent=root, seg=24, name=name + "_disc")
    for k in range(2):                       # concentric ribs
        r = .12 + k * .09
        lathe([(r - .012, .044), (r - .008, .052), (r + .008, .052), (r + .012, .044)], iron, parent=root, seg=20, name=name + "_rib")
    for k in range(6):                       # radial ribs
        a = k * math.pi / 3
        o = box((.26, .014, .006), iron, loc=(math.cos(a) * .2, math.sin(a) * .2, .048), bev=.0015, rot=(0, 0, a), parent=root, name=name + "_spoke")
    for a in (.0, math.pi):                  # hook slots
        box((.07, .02, .02), MATS["soot"], loc=(math.cos(a) * .27, math.sin(a) * .27, .042), bev=0, rot=(0, 0, a), parent=root, name=name + "_slot")
    return root

fresh(); palette()
# frame + shaft are always there
iron = MATS["cast_iron"]
lathe([(.36, -.02), (.455, -.02), (.455, .012), (.43, .02), (.37, .02), (.36, -.005), (.36, -.02)], iron, name="manhole_frame", seg=28)
lathe([(.38, -.02), (.38, -1.6), (.43, -1.6), (.43, -.02)], MATS["concrete"], name="shaft", seg=16)
for i in range(5): box((.03, .26, .03), MATS["steel"], loc=(.36, 0, -.25 - i * .3), bev=.004, name="rung")
lathe([(0, -1.6), (.43, -1.6), (.43, -1.62), (0, -1.62)], MATS["soot"], name="shaft_floor", seg=16)
box((.9, .9, .02), MATS["asphalt"], loc=(0, 0, -.012), bev=0, name="street_patch")
# states
so = empty("state_ok", size=.1); cover("cover_ok", so)
sl = empty("state_loose", size=.1); cover("cover_off", sl, loc=(.95, -.25, .0), rot=(0, 0, .5))
# animated cover (open/close): game uses it for the transition
ca = cover("cover_anim")
animate(ca, "open", [(1, dict(loc=(0, 0, 0), rot=(0, 0, 0))), (8, dict(loc=(.05, -.02, .14), rot=(.04, 0, .15))), (20, dict(loc=(.55, -.16, .05), rot=(0, 0, .4))), (30, dict(loc=(.95, -.25, 0), rot=(0, 0, .5)))])
animate(ca, "close", [(1, dict(loc=(.95, -.25, 0), rot=(0, 0, .5))), (10, dict(loc=(.55, -.16, .05), rot=(0, 0, .4))), (22, dict(loc=(.05, -.02, .14), rot=(.04, 0, .15))), (30, dict(loc=(0, 0, 0), rot=(0, 0, 0)))])
box((.9, .9, .02), None, loc=(0, 0, .0), bev=0, name="manhole-col").hide_render = False
empty("ip_use", (0, -.75, 0), size=.15); empty("ip_hand", (.33, 0, .06), size=.08); empty("ip_hit", (0, 0, -.3), size=.08)
smooth_angle([o for o in bpy.data.objects if o.type == 'MESH'], 40)
export("manhole", anims=True)

# ---------------- decals: flat blobs just above the floor (z=0.003), UV 0..1 across the blob bounding box ----------------
def blob(name, material, seed, r=.5, wob=.35, n=28, drops=0, stretch=(1, 1), parent=None):
    rnd = random.Random(seed); bm = bmesh.new()
    ctr = bm.verts.new((0, 0, .003)); ring = []
    ph = [rnd.uniform(0, 6.28) for _ in range(4)]
    for i in range(n):
        a = 2 * math.pi * i / n
        k = 1 + wob * (math.sin(2 * a + ph[0]) * .5 + math.sin(3 * a + ph[1]) * .35 + math.sin(5 * a + ph[2]) * .15)
        ring.append(bm.verts.new((math.cos(a) * r * k * stretch[0], math.sin(a) * r * k * stretch[1], .003)))
    for i in range(n): bm.faces.new((ctr, ring[i], ring[(i + 1) % n]))
    for d in range(drops):
        a = rnd.uniform(0, 6.28); dist = r * rnd.uniform(1.25, 1.9); rr = r * rnd.uniform(.05, .13); c = Vector((math.cos(a) * dist * stretch[0], math.sin(a) * dist * stretch[1], .003))
        vs = [bm.verts.new((c.x + math.cos(t) * rr, c.y + math.sin(t) * rr, .003)) for t in [i * 2 * math.pi / 8 for i in range(8)]]
        bm.faces.new(vs)
    xs = [v.co.x for v in bm.verts]; ys = [v.co.y for v in bm.verts]
    uv = bm.loops.layers.uv.new("UVMap")
    for f in bm.faces:
        for l in f.loops: l[uv].uv = ((l.vert.co.x - min(xs)) / (max(xs) - min(xs)), (l.vert.co.y - min(ys)) / (max(ys) - min(ys)))
    for f in bm.faces: f.normal_update()
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    for f in bm.faces:
        if f.normal.z < 0: f.normal_flip()
    return mesh_obj(name, bm, material, parent=parent, smooth=False)
for dname, col, rough, seeds, kw in (("decal_blood", (.16, .015, .015), .25, (3, 11), dict(r=.32, wob=.4, drops=7)),
                                      ("decal_oil", (.025, .02, .015), .15, (5, 12), dict(r=.5, wob=.45, drops=3, stretch=(1.15, .8))),
                                      ("decal_puddle", (.12, .16, .2), .05, (8, 21), dict(r=.7, wob=.5, drops=0, stretch=(1.2, .85)))):
    for vi, sd in enumerate(seeds):
        fresh(); palette(); m = mat(dname, col, rough, 0.0)
        blob(dname + ("" if vi == 0 else "2"), m, sd, **kw)
        empty("ip_hit", (0, 0, 0), size=.1)
        export(dname + ("" if vi == 0 else "2"))
