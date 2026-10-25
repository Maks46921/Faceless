"""Animals (stage 5): dogs (3 breeds), cat, pigeon, crow, rigged with simple skeletons and animations.
Run: ANIMAL=<name|all> D:\\Cosmoteer\\blender.exe -b -P build_animals.py -> models/city/animals/<name>.glb
Dogs/cat: idle_loop, walk_loop, run_loop, sit, sit_idle_loop, bark (cat: sleep_loop, lie_loop instead of bark). Birds: idle_loop, peck, walk_loop, fly_loop, take_off, land.
Names ending with _loop become looping animations in Godot (suffix is stripped)."""
import os
exec(open("D:/Faceless/models/src/lib_props.py", encoding="utf-8").read())
OUT = "D:/Faceless/models/city/animals"; os.makedirs(OUT, exist_ok=True)
R = math.radians

def skin_obj(name, pts, edges, material, sub=1):
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

def make_rig(name, bones):
    bpy.ops.object.armature_add(enter_editmode=True, location=(0, 0, 0))
    arm = bpy.context.object; arm.name = name; arm.data.name = name
    eb = arm.data.edit_bones
    for e in list(eb): eb.remove(e)
    for n, par, h, t in bones:
        e = eb.new(n); e.head = Vector(h); e.tail = Vector(t)
        if par: e.parent = eb[par]
    bpy.ops.object.mode_set(mode='OBJECT')
    return arm

def seg_dist(p, a, b):
    ab = b - a; t = max(0, min(1, (p - a).dot(ab) / ab.length_squared)); return (p - (a + ab * t)).length
def weight(objs, arm, bones, skip=()):
    segs = {n: (Vector(h), Vector(t)) for n, par, h, t in bones if n != "root" and n not in skip}
    for o in objs:
        for n in [b[0] for b in bones if b[0] != "root"]: o.vertex_groups.new(name=n)
        for v in o.data.vertices:
            c = sorted(((seg_dist(v.co, a, b), n) for n, (a, b) in segs.items()))[:3]
            ws = [(1 / (d + .012) ** 3, n) for d, n in c]; tot = sum(w for w, _ in ws)
            for w, n in ws: o.vertex_groups[n].add([v.index], w / tot, 'REPLACE')
        m = o.modifiers.new("Armature", 'ARMATURE'); m.object = arm; o.parent = arm

class Posing:
    """pose helper with calibrated axes: F = forward swing (tail moves to -Y for vertical bones, up for horizontal bones), S = sideways (+X), T = twist"""
    def __init__(self, arm):
        self.arm = arm; bpy.context.view_layer.objects.active = arm; bpy.ops.object.mode_set(mode='POSE'); self.pb = arm.pose.bones
        for b in self.pb: b.rotation_mode = 'XYZ'
        self.cal = {}; self.reset()
        Z = Vector((0, 0, 1))
        for n, b in self.pb.items():
            if n == "root": self.cal[n] = (1, 1, 1); continue
            self.reset(); t0 = b.tail.copy(); dirv = (b.tail - b.head).normalized(); a0 = b.matrix.to_3x3() @ Vector((1, 0, 0))
            b.rotation_euler = (R(10), 0, 0); self.upd(); d = b.tail - t0
            sf = (1 if d.y < 0 else -1) if abs(dirv.z) > .5 else (1 if d.z > 0 else -1)
            self.reset(); b.rotation_euler = (0, 0, R(10)); self.upd(); ss = 1 if (b.tail - t0).x > 0 else -1
            self.reset(); b.rotation_euler = (0, R(10), 0); self.upd(); a1 = b.matrix.to_3x3() @ Vector((1, 0, 0))
            st = 1 if (a1 - a0).dot(Z.cross(a0)) > 0 else -1
            self.cal[n] = (sf, ss, st)
        self.reset()
        b = self.pb["root"]; h0 = b.head.copy(); cols = []
        for k in range(3):
            v = [0, 0, 0]; v[k] = .1; b.location = v; self.upd(); cols.append((b.head - h0) / .1); b.location = (0, 0, 0)
        self.locm = Matrix((cols[0], cols[1], cols[2])).transposed().inverted(); self.reset()
        self.acts = {}
    def upd(self): bpy.context.view_layer.update()
    def reset(self):
        for b in self.pb: b.rotation_euler = (0, 0, 0); b.location = (0, 0, 0); b.scale = (1, 1, 1)
        self.upd()
    def apply(self, pose, loc=None):
        for n, b in self.pb.items():
            if n == "root": continue
            f, s, t = pose.get(n, (0, 0, 0)); sf, ss, st = self.cal[n]
            b.rotation_euler = (sf * R(f), st * R(t), ss * R(s))
        d = (loc or {}).get("root", (0, 0, 0)); self.pb["root"].location = self.locm @ Vector(d)
        rr = (loc or {}).get("root_rot", (0, 0, 0)); self.pb["root"].rotation_euler = (R(rr[0]), R(rr[2]), 0) if False else (0, 0, 0)
        self.pb["root"].scale = (loc or {}).get("root_scale", (1, 1, 1))
        for n in (loc or {}):
            if n.startswith("loc:"):
                bn = n[4:]; self.pb[bn].location = self.locm @ Vector(loc[n]) if bn in ("root", "pelvis") else Vector(loc[n])
        self.upd()
    def key(self, frame, pose, loc=None):
        self.apply(pose, loc)
        for n, b in self.pb.items():
            b.keyframe_insert("rotation_euler", frame=frame)
            if n in ("root", "pelvis"): b.keyframe_insert("location", frame=frame)
            if n == "root": b.keyframe_insert("scale", frame=frame)
    def action(self, name, n, fn, step=2):
        act = bpy.data.actions.new(name); self.arm.animation_data_create(); self.arm.animation_data.action = act; self.reset()
        for f in range(0, n + 1, step):
            r = fn(f); self.key(f + 1, r[0], r[1] if len(r) > 1 else None)
        self.arm.animation_data.action = None; self.acts[name] = act; self.reset()
    def finish(self):
        bpy.ops.object.mode_set(mode='OBJECT')
        for name, act in self.acts.items():
            tr = self.arm.animation_data.nla_tracks.new(); tr.name = name; tr.strips.new(name, int(act.frame_range[0]), act)

def cyc(u, pts):
    u %= 1.0
    for (a, va), (b, vb) in zip(pts, pts[1:]):
        if a <= u <= b:
            x = (u - a) / (b - a) if b > a else 0; x = x * x * (3 - 2 * x); return va + (vb - va) * x
    return pts[0][1]

# ============================================================================= quadruped (dog / cat)
SPEC = {
 "dog_shepherd": dict(L=1.0, H=.68, fur=(.18, .11, .05), belly=(.06, .04, .02), snout=1.15, ear="up", tail="long", body=1.1, cat=False),
 "dog_mutt": dict(L=.82, H=.52, fur=(.22, .17, .1), belly=(.3, .26, .18), snout=1.0, ear="fold", tail="mid", body=1.0, cat=False),
 "dog_dachshund": dict(L=.78, H=.3, fur=(.12, .06, .03), belly=(.07, .03, .015), snout=1.0, ear="fold", tail="mid", body=.8, cat=False, short=True),
 "cat": dict(L=.5, H=.3, fur=(.12, .12, .12), belly=(.4, .4, .38), snout=.5, ear="up", tail="long", body=.7, cat=True),
}
def quadruped(name):
    sp = SPEC[name]; fresh(); palette()
    fur = mat(name + "_fur", sp['fur'], .95); belly = mat(name + "_belly", sp['belly'], .95); black = mat("animal_black", (.01, .01, .012), .5); eye = mat("animal_eye", (.04, .03, .02), .3)
    mat("tongue", (.35, .1, .1), .6)
    s = sp['L']; h = sp['H']; leg_h = h * (.42 if not sp.get("short") else .3); bz = leg_h + .1 * sp['body'] * h / .5
    # key positions (y forward = -Y)
    P = dict(rump=(0, .42 * s, bz), mid=(0, .08 * s, bz + .01), chest=(0, -.22 * s, bz + .02), neck0=(0, -.34 * s, bz + .08 * h / .5), head=(0, -.52 * s, bz + .17 * h / .5), nose=(0, -.52 * s - .14 * sp['snout'] * h / .5, bz + .12 * h / .5))
    rr = .1 * sp['body'] * h / .5
    pts = [(P['rump'][0], P['rump'][1], P['rump'][2], rr * .85, rr), (P['mid'][0], P['mid'][1], P['mid'][2], rr, rr * 1.05), (P['chest'][0], P['chest'][1], P['chest'][2], rr * 1.05, rr * 1.08),
           (P['neck0'][0], P['neck0'][1], P['neck0'][2], rr * .78, rr * .8), (P['head'][0], P['head'][1], P['head'][2], rr * .78, rr * .85), (P['nose'][0], P['nose'][1], P['nose'][2], rr * .4, rr * .38)]
    ed = [(0, 1), (1, 2), (2, 3), (3, 4), (4, 5)]
    # tail
    tl = {"long": .5, "mid": .32, "short": .15}[sp['tail']] * s * (1.0 if not sp['cat'] else 1.1)
    base = len(pts)
    pts += [(0, P['rump'][1] + .05 * s, bz + .02, rr * .3, rr * .3), (0, P['rump'][1] + .05 * s + tl * .5, bz + tl * .3, rr * .25, rr * .25), (0, P['rump'][1] + .05 * s + tl, bz + tl * .6, rr * .15, rr * .15)]
    ed += [(0, base), (base, base + 1), (base + 1, base + 2)]
    # legs
    legs = {}
    for sx, sd in ((-1, "r"), (1, "l")):
        fx = sx * rr * .8
        a = len(pts); pts += [(fx, P['chest'][1] + .03, bz - .02, rr * .5, rr * .5), (fx, P['chest'][1] + .03, leg_h * .6, rr * .36, rr * .36), (fx, P['chest'][1] + .02, leg_h * .08, rr * .3, rr * .32)]
        ed += [(2, a), (a, a + 1), (a + 1, a + 2)]; legs["f" + sd] = a
        a = len(pts); pts += [(fx, P['rump'][1] - .02, bz - .02, rr * .6, rr * .6), (fx, P['rump'][1] - .08 * s, leg_h * .62, rr * .42, rr * .42), (fx, P['rump'][1] + .04 * s, leg_h * .3, rr * .3, rr * .3), (fx, P['rump'][1] + .02 * s, leg_h * .08, rr * .3, rr * .32)]
        ed += [(0, a), (a, a + 1), (a + 1, a + 2), (a + 2, a + 3)]; legs["r" + sd] = a
    body = skin_obj(name, pts, ed, fur, 1)
    # belly patch, ears, eyes, nose, tongue
    parts = [body]
    hz, hy = P['head'][2], P['head'][1]
    for sx in (-1, 1):
        if sp['ear'] == "up":
            e = box((.04 * h / .5, .02, .09 * h / .5 * (1.2 if sp['cat'] else 1)), fur, loc=(sx * rr * .45, hy + .02, hz + rr * .78), bev=0, name="ear"); e.rotation_euler = (0, sx * .18, 0)
        else:
            e = box((.035 * h / .5, .09 * h / .5, .07 * h / .5), fur, loc=(sx * rr * .72, hy + .03, hz + rr * .5), bev=.004, name="ear"); e.rotation_euler = (0, sx * .5, 0)
        parts.append(e)
        parts.append(sphere(rr * .1, eye, loc=(sx * rr * .38, hy - rr * .55, hz + rr * .2), seg=8, rings=5, name="eye"))
    parts.append(sphere(rr * .13, black, loc=(0, P['nose'][1] - rr * .22, P['nose'][2] + rr * .08), seg=8, rings=5, name="nose"))
    parts.append(box((rr * .8, rr * 1.1, rr * .35), belly, loc=(0, P['mid'][1], P['mid'][2] - rr * .7), bev=.01, name="belly_patch"))
    for p in parts: p.vertex_groups.clear() if p is not body else None
    # bones
    B = [("root", None, (0, 0, 0), (0, 0, .1)), ("pelvis", "root", P['rump'], P['mid']), ("spine", "pelvis", P['mid'], P['chest']), ("chest", "spine", P['chest'], P['neck0']),
         ("neck", "chest", P['neck0'], P['head']), ("head", "neck", P['head'], P['nose']), ("jaw", "head", (0, hy - rr * .3, hz - rr * .3), (0, P['nose'][1], hz - rr * .35))]
    tb = base
    prev = "pelvis"
    for i in range(3):
        a = Vector(pts[tb + i][:3]); b = Vector(pts[tb + i + 1][:3]) if i < 2 else Vector(pts[tb + 2][:3]) + Vector((0, tl * .2, tl * .15))
        B.append((f"tail_{i + 1}", prev, tuple(a), tuple(b))); prev = f"tail_{i + 1}"
    for sd in ("l", "r"):
        a = legs["f" + sd]
        B += [(f"front_upper.{sd}", "chest", pts[a][:3], pts[a + 1][:3]), (f"front_lower.{sd}", f"front_upper.{sd}", pts[a + 1][:3], pts[a + 2][:3]), (f"front_paw.{sd}", f"front_lower.{sd}", pts[a + 2][:3], (pts[a + 2][0], pts[a + 2][1] - .05, .01))]
        a = legs["r" + sd]
        B += [(f"rear_thigh.{sd}", "pelvis", pts[a][:3], pts[a + 1][:3]), (f"rear_shin.{sd}", f"rear_thigh.{sd}", pts[a + 1][:3], pts[a + 2][:3]), (f"rear_hock.{sd}", f"rear_shin.{sd}", pts[a + 2][:3], pts[a + 3][:3]), (f"rear_paw.{sd}", f"rear_hock.{sd}", pts[a + 3][:3], (pts[a + 3][0], pts[a + 3][1] - .05, .01))]
    for ear in [p for p in parts if p.name.startswith("ear")]: pass
    objs = join_parts(parts, name)
    arm = make_rig(name + "_rig", B); weight([objs], arm, B)
    ps = Posing(arm)
    LEGS = [("front_upper", "front_lower", "front_paw", "l", 0.0), ("front_upper", "front_lower", "front_paw", "r", .5), ("rear_thigh", "rear_shin", "rear_hock", "l", .5), ("rear_thigh", "rear_shin", "rear_hock", "r", 0.0)]
    def gait(u, amp, bend, bob, flex, speed_sway):
        pose = {}
        for up, lo, pw, sd, off in LEGS:
            ph = u + off; sw = math.sin(2 * math.pi * ph); lift = max(0, math.cos(2 * math.pi * ph))
            front = up.startswith("front")
            pose[f"{up}.{sd}"] = (amp * sw, 0, 0)
            pose[f"{lo}.{sd}"] = ((-bend * lift) if front else (bend * .6 * lift), 0, 0)
            if not front: pose[f"{pw}.{sd}"] = (-bend * .5 * lift, 0, 0)
        pose["spine"] = (flex * math.sin(2 * math.pi * u), 0, speed_sway * math.sin(2 * math.pi * u)); pose["chest"] = (-flex * .6 * math.sin(2 * math.pi * u), 0, -speed_sway * math.sin(2 * math.pi * u))
        pose["neck"] = (-flex * .4 * math.sin(2 * math.pi * u + .6), 0, 0); pose["head"] = (flex * .4 * math.sin(2 * math.pi * u + .6), 0, 0)
        for i in range(3): pose[f"tail_{i + 1}"] = (3 * math.sin(2 * math.pi * u + i), 0, 10 * math.sin(2 * math.pi * u * 2 + i))
        return pose, {"root": (0, 0, bob * abs(math.sin(2 * math.pi * u)))}
    def idle(f):
        u = f / 96; s_ = math.sin(2 * math.pi * u)
        pose = {"chest": (1.2 * s_, 0, 0), "spine": (.6 * s_, 0, 0), "head": (2 * math.sin(2 * math.pi * u + 1), 0, 6 * math.sin(2 * math.pi * u)), "neck": (0, 0, 3 * math.sin(2 * math.pi * u))}
        for i in range(3): pose[f"tail_{i + 1}"] = (2 * s_, 0, 14 * math.sin(2 * math.pi * u * 3 + i * .8) * (1 if f % 96 < 60 else .3))
        for up, lo, pw, sd, off in LEGS: pose[f"{up}.{sd}"] = (0, 0, 0)
        return pose, {}
    ps.action("idle_loop", 96, idle, 8)
    ps.action("walk_loop", 24, lambda f: gait(f / 24, 22, 28, .012, 2, 3), 2)
    ps.action("run_loop", 16, lambda f: gait(f / 16, 42, 50, .05, 7, 2), 2)
    def sit_pose(k):
        pose = {"rear_thigh.l": (70 * k, 0, 0), "rear_thigh.r": (70 * k, 0, 0), "rear_shin.l": (-95 * k, 0, 0), "rear_shin.r": (-95 * k, 0, 0), "rear_hock.l": (25 * k, 0, 0), "rear_hock.r": (25 * k, 0, 0),
                "spine": (22 * k, 0, 0), "chest": (6 * k, 0, 0), "neck": (-14 * k, 0, 0), "head": (-6 * k, 0, 0)}
        for i in range(3): pose[f"tail_{i + 1}"] = (-15 * k, 0, 0)
        return pose, {"root": (0, .06 * k, -h * .22 * k)}
    ps.action("sit", 24, lambda f: sit_pose(cyc(f / 24, [(0, 0), (.6, 1), (1, 1)])), 3)
    def sit_idle(f):
        p, l = sit_pose(1); u = f / 96; p["head"] = (-6 + 3 * math.sin(2 * math.pi * u), 0, 14 * math.sin(2 * math.pi * u)); p["chest"] = (6 + math.sin(2 * math.pi * u), 0, 0)
        for i in range(3): p[f"tail_{i + 1}"] = (-15, 0, 8 * math.sin(2 * math.pi * u * 2 + i))
        return p, l
    ps.action("sit_idle_loop", 96, sit_idle, 8)
    if not sp['cat']:
        def bark(f):
            u = f / 20; k = cyc(u, [(0, 0), (.15, 1), (.4, .6), (.55, 1), (.85, .2), (1, 0)])
            jaw = 28 * max(0, math.sin(math.pi * u * 4)) * (1 if u < .8 else 0)
            pose = {"head": (-16 * k, 0, 0), "neck": (-10 * k, 0, 0), "jaw": (jaw, 0, 0), "chest": (-3 * k, 0, 0), "spine": (-2 * k, 0, 0)}
            for i in range(3): pose[f"tail_{i + 1}"] = (8 * k, 0, 0)
            return pose, {"root": (0, .03 * k, 0)}
        ps.action("bark", 20, bark, 2)
    else:
        def sleep(f):
            u = f / 120; s_ = math.sin(2 * math.pi * u)
            pose = {"head": (-30, 0, 50), "neck": (-20, 0, 30), "chest": (3 * s_, 0, 0), "spine": (-12, 0, 0)}
            for up, lo, pw, sd, off in LEGS:
                pose[f"{up}.{sd}"] = ((55 if up.startswith("front") else 55), 0, 0); pose[f"{lo}.{sd}"] = ((-100 if up.startswith("front") else -100), 0, 0)
            for i in range(3): pose[f"tail_{i + 1}"] = (0, 0, 55 + 5 * i)
            return pose, {"root": (0, 0, -leg_h * .82)}
        ps.action("sleep_loop", 120, sleep, 10)
        def lie(f):
            u = f / 96; s_ = math.sin(2 * math.pi * u)
            pose = {"head": (-8, 0, 12 * math.sin(2 * math.pi * u)), "chest": (2 * s_, 0, 0)}
            for up, lo, pw, sd, off in LEGS:
                pose[f"{up}.{sd}"] = ((55 if up.startswith("front") else 60), 0, 0); pose[f"{lo}.{sd}"] = ((-95 if up.startswith("front") else -100), 0, 0)
            for i in range(3): pose[f"tail_{i + 1}"] = (0, 0, 14 * math.sin(2 * math.pi * u * 2 + i))
            return pose, {"root": (0, 0, -leg_h * .8)}
        ps.action("lie_loop", 96, lie, 8)
    ps.finish()
    box((rr * 2.4, s * 1.4, h), None, loc=(0, 0, h / 2), bev=0, name=f"{name}-convcol")
    empty("ip_use", (0, -s, 0), size=.15); empty("ip_hit", (0, 0, h / 2), size=.1)
    smooth_angle([o for o in bpy.data.objects if o.type == 'MESH' and o.name == name], 60)
    for o in bpy.data.objects: o.select_set(True)
    bpy.ops.export_scene.gltf(filepath=f"{OUT}/{name}.glb", export_format='GLB', use_selection=True, export_animations=True, export_animation_mode='NLA_TRACKS', export_skins=True)
    print("RES", name, "tris", sum(len(p.vertices) - 2 for p in objs.data.polygons), "bones", len(arm.data.bones), "acts", len(ps.acts))

def join_parts(parts, name):
    for o in bpy.data.objects: o.select_set(False)
    for o in parts: o.select_set(True)
    bpy.context.view_layer.objects.active = parts[0]; bpy.ops.object.join()
    j = bpy.context.object; j.name = name; j.data.name = name; set_active(j); bpy.ops.object.transform_apply(location=True, rotation=True, scale=True); return j

# ============================================================================= birds
BSPEC = {"pigeon": dict(sc=1.0, body=(.25, .26, .3), wing=(.17, .18, .21), head=(.2, .22, .26), neck=(.3, .5, .4), beak=(.45, .32, .2), size=.32),
         "crow": dict(sc=1.45, body=(.012, .012, .015), wing=(.01, .01, .012), head=(.01, .01, .012), neck=(.01, .01, .012), beak=(.03, .03, .035), size=.5)}
def bird(name):
    sp = BSPEC[name]; fresh(); palette(); k = sp['sc']
    body_m = mat(name + "_body", sp['body'], .95); wing_m = mat(name + "_wing", sp['wing'], .95); head_m = mat(name + "_head", sp['head'], .95); beak_m = mat("beak", sp['beak'], .6); leg_m = mat("bird_leg", (.3, .1, .1) if name == "pigeon" else (.02, .02, .02), .7); eye_m = mat("bird_eye", (.4, .15, .02) if name == "pigeon" else (.02, .02, .02), .3)
    body = skin_obj(name, [(0, .08 * k, .17 * k, .07 * k, .075 * k), (0, -.03 * k, .18 * k, .08 * k, .08 * k), (0, -.1 * k, .22 * k, .05 * k, .05 * k), (0, -.13 * k, .27 * k, .04 * k, .042 * k)],
                    [(0, 1), (1, 2), (2, 3)], body_m, 1)
    parts = [body]
    parts.append(sphere(.04 * k, head_m, loc=(0, -.16 * k, .295 * k), seg=10, rings=6, name="head"))
    parts.append(cyl(.012 * k, .05 * k, beak_m, loc=(0, -.205 * k, .29 * k), seg=6, rot=(math.pi / 2, 0, 0), r2=.003 * k, name="beak"))
    for sx in (-1, 1): parts.append(sphere(.007 * k, eye_m, loc=(sx * .028 * k, -.18 * k, .305 * k), seg=6, rings=4, name="eye"))
    # tail fan
    t = box((.09 * k, .13 * k, .01), body_m, loc=(0, .2 * k, .17 * k), bev=.003, name="tail"); t.rotation_euler = (-.1, 0, 0); parts.append(t)
    # wings (two segments each), legs
    wings = []
    for sx, sd in ((-1, "r"), (1, "l")):
        w1 = box((.13 * k, .1 * k, .012), wing_m, loc=(sx * .1 * k, 0.03 * k, .2 * k), bev=.003, name="wing_in"); w2 = box((.16 * k, .08 * k, .008), wing_m, loc=(sx * .245 * k, .05 * k, .2 * k), bev=.003, name="wing_out")
        parts += [w1, w2]
        for lx in (sx * .03 * k,):
            parts.append(cyl(.006 * k, .12 * k, leg_m, loc=(lx, .05 * k, .09 * k), seg=5, name="leg")); parts.append(box((.03 * k, .06 * k, .006), leg_m, loc=(lx, .03 * k, .004), bev=0, name="foot"))
    j = join_parts(parts, name)
    B = [("root", None, (0, 0, 0), (0, 0, .05 * k)), ("body", "root", (0, .08 * k, .17 * k), (0, -.1 * k, .22 * k)), ("neck", "body", (0, -.1 * k, .22 * k), (0, -.15 * k, .28 * k)), ("head", "neck", (0, -.15 * k, .28 * k), (0, -.2 * k, .29 * k)),
         ("beak", "head", (0, -.19 * k, .29 * k), (0, -.23 * k, .29 * k)), ("tail", "body", (0, .12 * k, .17 * k), (0, .26 * k, .17 * k))]
    for sx, sd in ((-1, "r"), (1, "l")):
        B += [(f"wing_a.{sd}", "body", (sx * .04 * k, .03 * k, .2 * k), (sx * .17 * k, .04 * k, .2 * k)), (f"wing_b.{sd}", f"wing_a.{sd}", (sx * .17 * k, .04 * k, .2 * k), (sx * .33 * k, .06 * k, .2 * k)),
              (f"leg.{sd}", "body", (sx * .03 * k, .05 * k, .15 * k), (sx * .03 * k, .05 * k, .04 * k)), (f"foot.{sd}", f"leg.{sd}", (sx * .03 * k, .05 * k, .04 * k), (sx * .03 * k, .0, .005))]
    arm = make_rig(name + "_rig", B); weight([j], arm, B)
    ps = Posing(arm)
    def idle(f):
        u = f / 72; return {"head": (4 * math.sin(2 * math.pi * u * 2), 0, 12 * math.sin(2 * math.pi * u)), "neck": (0, 0, 8 * math.sin(2 * math.pi * u + 1)), "tail": (2 * math.sin(2 * math.pi * u), 0, 0)}, {}
    ps.action("idle_loop", 72, idle, 6)
    def peck(f):
        u = f / 36; d = cyc(u, [(0, 0), (.2, 1), (.3, .1), (.45, 1), (.6, 0), (1, 0)])
        return {"neck": (-45 * d, 0, 0), "head": (-25 * d, 0, 0), "body": (-18 * d, 0, 0), "tail": (14 * d, 0, 0)}, {"root": (0, 0, 0)}
    ps.action("peck", 36, peck, 2)
    def walk(f):
        u = f / 24; s_ = math.sin(2 * math.pi * u)
        pose = {"leg.l": (32 * s_, 0, 0), "leg.r": (-32 * s_, 0, 0), "foot.l": (-10 * max(0, s_), 0, 0), "foot.r": (-10 * max(0, -s_), 0, 0), "neck": (5 * math.sin(4 * math.pi * u), 0, 0), "head": (-5 * math.sin(4 * math.pi * u), 0, 0), "body": (0, 0, 5 * s_)}
        return pose, {"root": (0, 0, .01 * abs(s_))}
    ps.action("walk_loop", 24, walk, 2)
    def fly(f):
        u = f / 12; fl = math.sin(2 * math.pi * u)
        pose = {"wing_a.l": (0, 0, 0), "wing_a.r": (0, 0, 0)}
        for sd, sg in (("l", 1), ("r", -1)):
            pose[f"wing_a.{sd}"] = (0, 55 * fl, 0); pose[f"wing_b.{sd}"] = (0, 35 * fl + 10, 0)
        pose["body"] = (-8, 0, 0); pose["head"] = (4, 0, 0); pose["tail"] = (8, 0, 0)
        for sd in ("l", "r"): pose[f"leg.{sd}"] = (-55, 0, 0); pose[f"foot.{sd}"] = (50, 0, 0)
        return pose, {"root": (0, 0, .5 + .04 * fl)}
    ps.action("fly_loop", 12, fly, 1)
    def takeoff(f):
        u = f / 24; ramp = cyc(u, [(0, 0), (1, 1)]); fl = math.sin(2 * math.pi * f / 8)
        pose = {}
        for sd in ("l", "r"): pose[f"wing_a.{sd}"] = (0, 70 * fl, 0); pose[f"wing_b.{sd}"] = (0, 40 * fl, 0); pose[f"leg.{sd}"] = (-50 * ramp, 0, 0); pose[f"foot.{sd}"] = (40 * ramp, 0, 0)
        pose["body"] = (-25 * ramp, 0, 0); pose["tail"] = (12 * ramp, 0, 0)
        return pose, {"root": (0, -.4 * ramp, .6 * ramp * ramp)}
    ps.action("take_off", 24, takeoff, 1)
    def land(f):
        u = f / 24; ramp = cyc(u, [(0, 1), (1, 0)]); fl = math.sin(2 * math.pi * f / 8) * (1 - u * .7)
        pose = {}
        for sd in ("l", "r"): pose[f"wing_a.{sd}"] = (0, 65 * fl, 0); pose[f"wing_b.{sd}"] = (0, 40 * fl, 0); pose[f"leg.{sd}"] = (-40 * ramp + 25 * (1 - ramp) * 0, 0, 0)
        pose["body"] = (18 * ramp, 0, 0); pose["tail"] = (-18 * ramp, 0, 0)
        return pose, {"root": (0, .5 * ramp, .6 * ramp)}
    ps.action("land", 24, land, 1)
    ps.finish()
    box((.3 * k, .5 * k, .35 * k), None, loc=(0, 0, .17 * k), bev=0, name=f"{name}-convcol"); empty("ip_use", (0, -.6, 0), size=.1); empty("ip_hit", (0, 0, .17 * k), size=.08)
    for o in bpy.data.objects: o.select_set(True)
    bpy.ops.export_scene.gltf(filepath=f"{OUT}/{name}.glb", export_format='GLB', use_selection=True, export_animations=True, export_animation_mode='NLA_TRACKS', export_skins=True)
    print("RES", name, "tris", sum(len(p.vertices) - 2 for p in j.data.polygons), "bones", len(arm.data.bones), "acts", len(ps.acts))

which = os.environ.get("ANIMAL", "all")
for n in SPEC:
    if which in ("all", n): quadruped(n)
for n in BSPEC:
    if which in ("all", n): bird(n)
