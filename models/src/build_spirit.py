"""Golden spirit: glowing faceless figure with a flowing tail, rigged (root, body, spine, head, arms, 6 tail bones), pale double, halo,
thread ribbon (UV along the length), animations descend (6 s spiral), enter (1.5 s into the head of the person in front), idle (hover loop).
Run: D:\\Cosmoteer\\blender.exe -b -P D:\\Faceless\\models\\src\\build_spirit.py  -> models/spirit_gold.glb, models/spirit_thread.glb"""
import os
exec(open("D:/Faceless/models/src/lib_props.py", encoding="utf-8").read())
R_ = math.radians

# ---------------------------------------------------------------- thread ribbon (UV u along length 0..1 per segment, v across 0..1)
def ribbon(name, material, length=6.0, width=.05, segs=48, path=None, parent=None):
    """path(t)->(x,y,z) for t in 0..1; default straight up. Double sided (two coincident faces with opposite normals)."""
    path = path or (lambda t: (0.0, 0.0, t * length))
    bm = bmesh.new(); uv = bm.loops.layers.uv.new("UVMap")
    pts = []
    for i in range(segs + 1):
        t = i / segs; p = Vector(path(t)); p2 = Vector(path(min(1, t + .01))); p1 = Vector(path(max(0, t - .01)))
        tan = (p2 - p1).normalized(); side = tan.cross(Vector((0, 1, 0)))
        if side.length < .01: side = tan.cross(Vector((1, 0, 0)))
        side.normalize(); pts.append((p - side * width / 2, p + side * width / 2, t))
    for flip in (0, 1):
        rows = [(bm.verts.new(a), bm.verts.new(b), t) for a, b, t in pts]
        for i in range(segs):
            a, b = rows[i], rows[i + 1]
            vs = [a[0], a[1], b[1], b[0]]; uvs = [(a[2], 0), (a[2], 1), (b[2], 1), (b[2], 0)]
            if flip: vs, uvs = vs[::-1], uvs[::-1]
            f = bm.faces.new(vs)
            for l, u in zip(f.loops, uvs): l[uv].uv = u
    return mesh_obj(name, bm, material, parent=parent, smooth=True)

# ---------------------------------------------------------------- body
fresh(); palette()
mat("thread_glow", (1.0, .75, .25), .3, 0.0, emit=(1.0, .6, .1), emit_strength=3.5)
GOLD, PALE = MATS["gold_glow"], MATS["gold_glow_pale"]
def skin_chain(name, pts, edges, material, sub=2):
    me = bpy.data.meshes.new(name); me.from_pydata([p[:3] for p in pts], edges, [])
    o = bpy.data.objects.new(name, me); collection().objects.link(o); set_active(o)
    o.modifiers.new("skin", "SKIN"); sv = me.skin_vertices[0].data
    for i, p in enumerate(pts): sv[i].radius = (p[3], p[4])
    adj = {i: [] for i in range(len(pts))}
    for a, b in edges: adj[a].append(b); adj[b].append(a)
    seen = set()
    for i in range(len(pts)):
        if i in seen: continue
        sv[i].use_root = True; st = [i]
        while st:
            k = st.pop()
            if k in seen: continue
            seen.add(k); st += adj[k]
    o.modifiers.new("sub", "SUBSURF").levels = sub
    bpy.ops.object.modifier_apply(modifier="skin"); bpy.ops.object.modifier_apply(modifier="sub")
    me.materials.append(material)
    for p in o.data.polygons: p.use_smooth = True
    return o
# spirit hovers: tail reaches back (+Y), lowest point 0.25 above the origin floor
PT = [(0, 0, 1.64, .105, .11),      # 0 head
      (0, 0, 1.48, .045, .05),      # 1 neck
      (0, 0, 1.32, .12, .08),       # 2 chest
      (0, 0, 1.08, .085, .065),     # 3 waist
      (0, .06, .86, .07, .06),      # 4 tail 1
      (0, .2, .62, .056, .05),      # 5 tail 2
      (0, .4, .46, .043, .04),      # 6 tail 3
      (0, .64, .38, .031, .03),     # 7 tail 4
      (0, .88, .40, .02, .02),      # 8 tail 5
      (0, 1.1, .50, .008, .008),    # 9 tail tip
      (-.14, 0, 1.38, .045, .045), (-.3, .1, 1.22, .035, .035), (-.44, .26, 1.06, .026, .026), (-.56, .46, .93, .01, .01),      # 10-13 right arm + wisp
      (.14, 0, 1.38, .045, .045), (.3, .1, 1.22, .035, .035), (.44, .26, 1.06, .026, .026), (.56, .46, .93, .01, .01)]          # 14-17 left arm + wisp
ED = [(0, 1), (1, 2), (2, 3), (3, 4), (4, 5), (5, 6), (6, 7), (7, 8), (8, 9), (2, 10), (10, 11), (11, 12), (12, 13), (2, 14), (14, 15), (15, 16), (16, 17)]
spirit = skin_chain("spirit_gold", PT, ED, GOLD, 1)
double = skin_chain("spirit_double", PT, ED, PALE, 1)
halo = lathe([(.2, -.008), (.26, -.008), (.26, .008), (.2, .008), (.2, -.008)], PALE, loc=(0, .13, 1.66), seg=28, name="spirit_halo", rot=(math.pi / 2, 0, 0))
thread = ribbon("thread_ribbon", MATS["thread_glow"], length=6.0, width=.05, segs=40)
thread.location = (0, 0, 1.8)

# ---------------------------------------------------------------- armature
BONES = [("root", None, (0, 0, 0), (0, 0, .2)), ("body", "root", (0, 0, 1.0), (0, 0, 1.2)), ("chest", "body", (0, 0, 1.2), (0, 0, 1.45)),
         ("head", "chest", (0, 0, 1.45), (0, 0, 1.78))]
tail = [(0, 0, 1.0), (0, .06, .86), (0, .2, .62), (0, .4, .46), (0, .64, .38), (0, .88, .40), (0, 1.1, .50)]
for i in range(6): BONES.append((f"tail_{i + 1}", "body" if i == 0 else f"tail_{i}", tail[i], tail[i + 1]))
for sx, sd in ((-1, "r"), (1, "l")):
    BONES += [(f"arm_{sd}1", "chest", (sx * .14, 0, 1.38), (sx * .3, .1, 1.22)), (f"arm_{sd}2", f"arm_{sd}1", (sx * .3, .1, 1.22), (sx * .44, .26, 1.06)),
              (f"wisp_{sd}", f"arm_{sd}2", (sx * .44, .26, 1.06), (sx * .56, .46, .93))]
bpy.ops.object.armature_add(enter_editmode=True, location=(0, 0, 0))
arm = bpy.context.object; arm.name = "spirit_rig"; arm.data.name = "spirit_rig"
eb = arm.data.edit_bones
for e in list(eb): eb.remove(e)
for n, par, h, t in BONES:
    e = eb.new(n); e.head = Vector(h); e.tail = Vector(t)
    if par: e.parent = eb[par]
bpy.ops.object.mode_set(mode='OBJECT')
segs_ = {n: (Vector(h), Vector(t)) for n, par, h, t in BONES if n != "root"}
def seg_dist(p, a, b):
    ab = b - a; t = max(0, min(1, (p - a).dot(ab) / ab.length_squared)); return (p - (a + ab * t)).length
for o in (spirit, double, halo):
    for n in segs_: o.vertex_groups.new(name=n)
    for v in o.data.vertices:
        p = v.co
        if o is halo: o.vertex_groups["head"].add([v.index], 1.0, 'REPLACE'); continue
        c = sorted(((seg_dist(p, a, b), n) for n, (a, b) in segs_.items()))[:3]
        ws = [(1 / (d + .02) ** 3, n) for d, n in c]; tot = sum(w for w, _ in ws)
        for w, n in ws: o.vertex_groups[n].add([v.index], w / tot, 'REPLACE')
    m = o.modifiers.new("Armature", 'ARMATURE'); m.object = arm; o.parent = arm
# ---- facing: spirit looks towards -Y (glTF +Z) like everything else
# ---------------------------------------------------------------- animation
bpy.context.view_layer.objects.active = arm
bpy.ops.object.mode_set(mode='POSE'); pb = arm.pose.bones
for b in pb: b.rotation_mode = 'XYZ'
def upd(): bpy.context.view_layer.update()
def reset():
    for b in pb: b.rotation_euler = (0, 0, 0); b.location = (0, 0, 0); b.scale = (1, 1, 1)
    upd()
reset(); b = pb["root"]; h0 = b.head.copy(); cols = []
for k in range(3):
    v = [0, 0, 0]; v[k] = .1; b.location = v; upd(); cols.append((b.head - h0) / .1); b.location = (0, 0, 0)
LOCM = Matrix((cols[0], cols[1], cols[2])).transposed().inverted()
reset()
def sstep(x): x = max(0.0, min(1.0, x)); return x * x * (3 - 2 * x)
def put(frame, root_world=(0, 0, 0), yaw=0.0, lean=0.0, scale=1.0, phase=0.0, amp=1.0, bob=0.0):
    reset()
    r = pb["root"]; r.location = LOCM @ Vector(root_world); r.rotation_euler = (0, 0, yaw) if False else (0, yaw, 0)    # local Y = world Z for the vertical root bone
    r.scale = (scale, scale, scale)
    pb["body"].rotation_euler = (lean, 0, 0); pb["chest"].rotation_euler = (lean * .4, 0, .05 * math.sin(phase))
    pb["head"].rotation_euler = (-lean * .5, 0, .08 * math.sin(phase + 1))
    for i in range(6):
        pb[f"tail_{i + 1}"].rotation_euler = (.06 * amp * math.sin(phase * 1.0 - i * .8), 0, .28 * amp * math.sin(phase - i * .7 + .5))
    for sd, sg in (("l", 1), ("r", -1)):
        pb[f"arm_{sd}1"].rotation_euler = (.12 * amp * math.sin(phase + sg), 0, sg * (.12 + .06 * math.sin(phase * 1.3)))
        pb[f"arm_{sd}2"].rotation_euler = (.15 * amp * math.sin(phase - .6 + sg), 0, sg * .1 * math.sin(phase * 1.1))
        pb[f"wisp_{sd}"].rotation_euler = (.3 * amp * math.sin(phase - 1.2), 0, sg * .25 * math.sin(phase * 1.4 - .5))
    pb["body"].location = LOCM @ Vector((0, 0, bob))
    upd()
    for n, bn in pb.items():
        bn.keyframe_insert("rotation_euler", frame=frame); bn.keyframe_insert("location", frame=frame)
        if n == "root": bn.keyframe_insert("scale", frame=frame)
ACT = {}
def action(name, n, fn, step):
    act = bpy.data.actions.new(name); arm.animation_data_create(); arm.animation_data.action = act
    for f in range(0, n + 1, step): fn(f)
    arm.animation_data.action = None; ACT[name] = act; reset()
# idle: hover loop (96 frames)
def idle(f):
    u = f / 96; put(f + 1, (0.0, 0.0, 0.0), yaw=.12 * math.sin(2 * math.pi * u), lean=.05 * math.sin(2 * math.pi * u + 1), phase=2 * math.pi * u * 2, amp=.8, bob=.07 * math.sin(2 * math.pi * u))
action("idle", 96, idle, 6)
# descend: 144 frames (6 s @24) spiral from the sky, slowing down at the ground; ends at the idle pose at the origin
TURNS, H0, R0 = 2.5, 24.0, 6.0
def descend(f):
    u = f / 144.0
    H = H0 * (1 - u) ** 2.4
    Rr = R0 * (1 - u) ** 1.3
    th = 2 * math.pi * TURNS * (1 - (1 - u) ** 1.7)
    th_end = 2 * math.pi * TURNS
    x, y = Rr * math.cos(th), Rr * math.sin(th)
    put(f + 1, (x, y, H), yaw=(th - th_end) * .8, lean=.55 * (1 - u) ** 1.5, phase=u * 40, amp=1.3 - .5 * u, bob=0.07 * math.sin(2 * math.pi * u) * u)
action("descend", 144, descend, 4)
# enter: 36 frames (1.5 s): glide 1.2 m forward (-Y, glTF +Z) and up to head height, shrink into the head of the person standing 1.2 m ahead
def enter(f):
    u = f / 36.0; s = sstep(u)
    put(f + 1, (0.0, -1.2 * s, 1.55 * s ** 1.3), yaw=.6 * s, lean=.7 * s, scale=max(.02, 1 - .95 * sstep((u - .3) / .7)), phase=u * 14, amp=1.0 + .6 * s, bob=0.0)
action("enter", 36, enter, 2)
bpy.ops.object.mode_set(mode='OBJECT')
for name in ("idle", "descend", "enter"):
    act = ACT[name]; tr = arm.animation_data.nla_tracks.new(); tr.name = name; tr.strips.new(name, int(act.frame_range[0]), act)
bpy.context.scene.render.fps = 24
empty("ip_head", (0, 0, 1.78), size=.1); empty("ip_enter", (0, -1.2, 1.6), size=.12)
# ---- export spirit (+ thread node)
for o in bpy.data.objects: o.select_set(True)
bpy.ops.export_scene.gltf(filepath=f"{ROOT}/spirit_gold.glb", export_format='GLB', use_selection=True, export_animations=True, export_animation_mode='NLA_TRACKS', export_skins=True, export_apply=False)
print("RES spirit_gold tris", sum(len(p.vertices) - 2 for o in (spirit, double, halo, thread) for p in o.data.polygons), "bones", len(arm.data.bones))
bpy.ops.wm.save_as_mainfile(filepath=f"{ROOT}/src/spirit_gold.blend")

# ---------------------------------------------------------------- thread set (straight lengths + curved), separate glb
fresh(); palette(); mat("thread_glow", (1.0, .75, .25), .3, 0.0, emit=(1.0, .6, .1), emit_strength=3.5); TG = MATS["thread_glow"]
ribbon("thread_short", TG, 1.0, .04, 16)
ribbon("thread_mid", TG, 3.0, .045, 32).location = (.3, 0, 0)
ribbon("thread_long", TG, 8.0, .05, 64).location = (.6, 0, 0)
ribbon("thread_curve", TG, 4.0, .05, 56, path=lambda t: (math.sin(t * 6.0) * .45 * t, math.sin(t * 3.0 + .7) * .3, t * 4.0)).location = (.9, 0, 0)
ribbon("thread_curve_arc", TG, 3.0, .05, 48, path=lambda t: (math.sin(t * math.pi) * 1.2, 0, t * 2.6 + math.sin(t * math.pi) * .6)).location = (1.4, 0, 0)
export("spirit_thread")
