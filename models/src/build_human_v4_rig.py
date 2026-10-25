"""Part 2 of build_human_v4.py (exec'd after build_human_v4_head.py): join, face shape keys, armature, weights, animations, export."""
import bpy, bmesh, math
from mathutils import Vector, Matrix

# ============ join, transform ============
if os.environ.get("TRISREPORT"):
    import collections
    c = collections.Counter()
    for o in objs: c[o.name.split('.')[0]] += sum(len(p.vertices) - 2 for p in o.data.polygons)
    print("TRISBY", dict(c.most_common()))
for o in bpy.data.objects: o.select_set(o in objs)
bpy.context.view_layer.objects.active = objs[0]; bpy.ops.object.join()
j = bpy.context.object; j.name = "human_noir"; j.data.name = "human_noir"
j.rotation_euler[2] = math.pi; bpy.ops.object.transform_apply(rotation=True, location=False)
mz = float(os.environ.get("REF_Z", 0)) or max(v.co.z for v in j.data.vertices); S = float(os.environ.get("TARGET_H", 1.78)) / mz
j.scale = (S, S, S); bpy.ops.object.transform_apply(scale=True)
bpy.ops.object.shade_smooth_by_angle(angle=math.radians(50))

def gidx(name):
    g = j.vertex_groups[name].index
    return [v.index for v in j.data.vertices if any(x.group == g for x in v.groups)]
FACE = {n: (gidx(n) if n in j.vertex_groups else []) for n in ("f_head", "f_eye", "f_pupil", "f_lid", "f_brow", "f_mouth", "f_lipu", "f_lipl")}
FACEKEYS = not os.environ.get("MANN")

# ============ face shape keys ============
HEADZ = 1.66 * S
if FACEKEYS:
    sk_basis = j.shape_key_add(name="Basis", from_mix=False)
    def smooth(x): x = max(0.0, min(1.0, x)); return x * x * (3 - 2 * x)
    def shape(name, fn):
        k = j.shape_key_add(name=name, from_mix=False); k.value = 0.0
        for i, v in enumerate(j.data.vertices): k.data[i].co = v.co.copy()
        fn(k.data)
        return k
    def sel_move(group, fn):
        def run(d):
            for i in FACE[group]:
                c = j.data.vertices[i].co; d[i].co = fn(c.copy())
        return run
    def combo(*fs):
        def run(d):
            for f in fs: f(d)
        return run
    def mv(group, dx=0, dy=0, dz=0): return sel_move(group, lambda c: c + Vector((dx, dy, dz)) * S)
    MZ = HEADZ - .067 * S
    def mouth_open(d):
        for i in FACE["f_head"]:
            c = j.data.vertices[i].co; zl = c.z - HEADZ
            if c.y < .015 * S and zl < -.06 * S:
                w = smooth((-.06 * S - zl) / (.04 * S)); d[i].co = c + Vector((0, 0, -.022 * S * w))
        for i in FACE["f_lipl"]: c = j.data.vertices[i].co; d[i].co = c + Vector((0, 0, -.016 * S))
        for i in FACE["f_lipu"]: c = j.data.vertices[i].co; d[i].co = c + Vector((0, 0, .002 * S))
        for i in FACE["f_mouth"]:
            c = j.data.vertices[i].co; d[i].co = Vector((c.x, c.y, MZ + (c.z - MZ) * 6 - .0065 * S))
    def blink_fn(d):
        for i in FACE["f_lid"]:
            c = j.data.vertices[i].co; zl = c.z / S - 1.672
            d[i].co = Vector((c.x, c.y - .0006 * S, S * (1.672 + (zl - .0087) / .04)))
    shape("blink", blink_fn)
    shape("mouth_open", mouth_open)
    def mouth_curve(sign):
        def run(d):
            for g in ("f_mouth", "f_lipu", "f_lipl"):
                for i in FACE[g]:
                    c = j.data.vertices[i].co; r = abs(c.x) / (.024 * S)
                    d[i].co = c + Vector((c.x * .1 * sign, 0, sign * .0095 * S * r * r))
            for i in FACE["f_head"]:
                c = j.data.vertices[i].co; zl = c.z - HEADZ
                if c.y < 0 and abs(zl + .066 * S) < .028 * S and .028 * S < abs(c.x) < .06 * S:
                    d[i].co = c + Vector((0, 0, sign * .0035 * S * (1 - abs(zl + .066 * S) / (.028 * S))))
        return run
    shape("smile", mouth_curve(1)); shape("frown", mouth_curve(-1))
    shape("brow_up", mv("f_brow", 0, 0, .010)); shape("brow_down", mv("f_brow", 0, 0, -.008))
    shape("look_l", mv("f_pupil", .0042)); shape("look_r", mv("f_pupil", -.0042))
    shape("look_up", mv("f_pupil", 0, 0, .003)); shape("look_down", mv("f_pupil", 0, 0, -.003))
    j.active_shape_key_index = 0

def smooth(x): x = max(0.0, min(1.0, x)); return x * x * (3 - 2 * x)
# ============ armature ============
def P(x, y, z): return Vector((-x * S, -y * S, z * S))      # pre-transform coords -> final
B = [("root", None, (0, 0, 0), (0, 0, .15)),
     ("pelvis", "root", P(0, 0, .93), P(0, 0, 1.02)), ("spine", "pelvis", P(0, 0, 1.02), P(0, 0, 1.15)),
     ("spine2", "spine", P(0, 0, 1.15), P(0, 0, 1.44)), ("neck", "spine2", P(0, 0, 1.44), P(0, 0, 1.58)),
     ("head", "neck", P(0, 0, 1.58), P(0, 0, 1.82)), ("jaw", "head", P(0, .0, 1.63), P(0, .075, 1.598))]
for sx, side in ((-1, "R"), (1, "L")):
    q = lambda x, y, z, sx=sx: P(-sx * x, y, z)
    B += [(f"shoulder.{side}", "spine2", q(.04, 0, 1.44), q(.2, 0, 1.44)),
          (f"upper_arm.{side}", f"shoulder.{side}", q(.2, 0, 1.44), q(.31, 0, 1.2)),
          (f"forearm.{side}", f"upper_arm.{side}", q(.31, 0, 1.2), q(.365, .04, .97)),
          (f"hand.{side}", f"forearm.{side}", q(.365, .04, .97), q(.372, .05, .86)),
          (f"index_1.{side}", f"hand.{side}", q(.372, .096, .855), q(.372, .1, .818)),
          (f"index_2.{side}", f"index_1.{side}", q(.372, .1, .818), q(.372, .104, .782)),
          (f"fingers_1.{side}", f"hand.{side}", q(.372, .05, .855), q(.372, .056, .812)),
          (f"fingers_2.{side}", f"fingers_1.{side}", q(.372, .056, .812), q(.372, .062, .772)),
          (f"thumb_1.{side}", f"hand.{side}", q(.38, .09, .93), q(.385, .105, .89)),
          (f"thumb_2.{side}", f"thumb_1.{side}", q(.385, .105, .89), q(.387, .113, .855)),
          (f"prop.{side}", f"hand.{side}", q(.372, .1, .88), q(.372, .13, .88)),
          (f"thigh.{side}", "pelvis", q(.095, 0, .9), q(.095, 0, .5)),
          (f"shin.{side}", f"thigh.{side}", q(.095, 0, .5), q(.1, 0, .09)),
          (f"foot.{side}", f"shin.{side}", q(.1, 0, .09), q(.1, .105, .04)),
          (f"toe.{side}", f"foot.{side}", q(.1, .105, .04), q(.1, .17, .035))]
B.append(("phone", "prop.R", P(-.372, .1, .93), P(-.372, .11, 1.0)))
B.append(("ember", "prop.R", P(-.372, .14, .88), P(-.372, .15, .88)))
B.append(("lids", "head", P(0, .09, 1.672), P(0, .1, 1.672)))
bpy.ops.object.armature_add(enter_editmode=True, location=(0, 0, 0))
arm = bpy.context.object; arm.name = "human_rig"; arm.data.name = "human_rig"
eb = arm.data.edit_bones
for e in list(eb): eb.remove(e)
for name, parent, h, t in B:
    e = eb.new(name); e.head = Vector(h); e.tail = Vector(t)
    if parent: e.parent = eb[parent]
for e in eb:
    if e.parent and (e.parent.tail - e.head).length < 1e-4 * S: e.use_connect = True
bpy.ops.object.mode_set(mode='OBJECT')

# ---- weights
def seg_dist(p, a, b):
    ab = b - a; t = max(0, min(1, (p - a).dot(ab) / ab.length_squared)); return (p - (a + ab * t)).length
segs = {n: (Vector(h), Vector(t)) for n, par, h, t in B if n not in ("root", "phone", "ember", "lids") and not n.startswith("prop")}
mats = [m.name for m in j.data.materials]
vm = {}
for poly in j.data.polygons:
    for vi in poly.vertices: vm.setdefault(vi, mats[poly.material_index])
for n in [b[0] for b in B if b[0] != "root"]: j.vertex_groups.new(name=n)
S_EYE = set(FACE["f_eye"]) | set(FACE["f_pupil"]) | set(FACE["f_lid"]) | set(FACE["f_brow"])
S_LIPU, S_LIPL, S_MOUTH = set(FACE["f_lipu"]), set(FACE["f_lipl"]), set(FACE["f_mouth"])
facev = set(FACE["f_head"]) | S_EYE | S_LIPU | S_LIPL | S_MOUTH
leg = lambda n: n.startswith(("thigh", "shin", "foot", "toe"))
def setw(vi, ws):
    for n, w in ws:
        if w > 1e-4: j.vertex_groups[n].add([vi], w, 'REPLACE')
for v in j.data.vertices:
    p = v.co; mname = vm.get(v.index, "coat")
    if v.index in facev:
        zl = p.z - HEADZ; lower = (p.y < .02 * S) and zl < -.055 * S
        wj = smooth((-.055 * S - zl) / (.035 * S)) if lower else 0.0
        if v.index in S_MOUTH: wj = .55
        if v.index in S_LIPL: wj = .9
        if v.index in S_LIPU: wj = .12
        if v.index in S_EYE: wj = 0.0
        setw(v.index, (("jaw", wj), ("head", 1 - wj))); continue
    if mname in ("hair",) or p.z > 1.62 * S:
        setw(v.index, (("head", 1.0),)); continue
    skirt = mname == "coat" and p.z < .98 * S and abs(p.x) < .27 * S
    if skirt:
        t = max(0.0, min(1.0, (.93 * S - p.z) / (.4 * S))) * .38
        wl = max(0.0, min(1.0, .5 + p.x / (.12 * S)))
        setw(v.index, (("pelvis", 1 - t), ("thigh.L", t * wl), ("thigh.R", t * (1 - wl)))); continue
    cand = []
    for n, (h, t) in segs.items():
        if mname in ("shoes", "pants") and not (leg(n) or n in ("pelvis", "spine")): continue
        if mname == "coat" and n.startswith(("shin", "foot", "toe", "head", "neck", "jaw", "thigh")): continue
        cand.append((seg_dist(p, h, t), n))
    cand.sort(); cand = cand[:3]
    ws = [(1.0 / (d + .012) ** 3, n) for d, n in cand]; tot = sum(w for w, _ in ws)
    setw(v.index, [(n, w / tot) for w, n in ws])
mod = j.modifiers.new("Armature", 'ARMATURE'); mod.object = arm
j.parent = arm

# ============ pose calibration ============
bpy.context.view_layer.objects.active = arm
bpy.ops.object.mode_set(mode='POSE')
pb = arm.pose.bones
for b in pb: b.rotation_mode = 'XYZ'
def upd(): bpy.context.view_layer.update()
def reset():
    for b in pb: b.rotation_euler = (0, 0, 0); b.location = (0, 0, 0)
    upd()
CAL = {}
Z = Vector((0, 0, 1))
for n, b in pb.items():
    if n == "root": CAL[n] = (1, 1, 1); continue
    reset(); t0 = b.tail.copy(); a0 = b.matrix.to_3x3() @ Vector((1, 0, 0)); dirv = (b.tail - b.head).normalized()
    vertical = abs(dirv.z) > .5
    b.rotation_euler = (math.radians(10), 0, 0); upd(); d = b.tail - t0
    if n == "jaw": sf = 1 if d.z < 0 else -1
    elif vertical: sf = 1 if d.y < 0 else -1
    else: sf = 1 if d.z > 0 else -1
    reset(); b.rotation_euler = (0, 0, math.radians(10)); upd(); d = b.tail - t0; ss = 1 if d.x > 0 else -1
    reset(); b.rotation_euler = (0, math.radians(10), 0); upd(); a1 = b.matrix.to_3x3() @ Vector((1, 0, 0))
    st = 1 if (a1 - a0).dot(Z.cross(a0)) > 0 else -1
    CAL[n] = (sf, ss, st)
reset()
LOCM = {}
for n in ("pelvis", "root"):
    b = pb[n]; reset(); h0 = b.head.copy(); cols = []
    for k in range(3):
        v = [0, 0, 0]; v[k] = .1; b.location = v; upd(); cols.append((b.head - h0) / .1); b.location = (0, 0, 0)
    LOCM[n] = Matrix((cols[0], cols[1], cols[2])).transposed().inverted()
reset()

# ============ animation engine ============
R = math.radians
LIMB = ("shoulder", "upper_arm", "forearm", "hand", "thigh", "shin", "foot", "toe", "index_1", "index_2", "fingers_1", "fingers_2", "thumb_1", "thumb_2")
def side_of(n): return 1 if n.endswith(".L") else (-1 if n.endswith(".R") else 1)
REST = {"upper_arm.L": (0, 5, 0), "upper_arm.R": (0, 5, 0), "forearm.L": (10, 0, 0), "forearm.R": (10, 0, 0),
        "grip.L": (.25, 0, .15), "grip.R": (.25, 0, .15)}
def grip_pose(side, amt, point=0.0, thumb=None):
    th = amt * .55 if thumb is None else thumb
    ix = amt * (1 - point)
    return {f"index_1.{side}": (0, -75 * ix, 0), f"index_2.{side}": (0, -85 * ix, 0),
            f"fingers_1.{side}": (0, -78 * amt, 0), f"fingers_2.{side}": (0, -88 * amt, 0),
            f"thumb_1.{side}": (-10 * th, -35 * th, 0), f"thumb_2.{side}": (0, -55 * th, 0)}
def expand_grip(pose):
    out = dict(pose)
    for side in "LR":
        g = out.pop(f"grip.{side}", None)
        # legacy keys from older action definitions
        old = out.pop(f"fingers.{side}", None); out.pop(f"thumb.{side}", None)
        if g is None and old is not None: g = (-old[1] / 80.0, 0, None)
        if g is None: g = REST[f"grip.{side}"]
        for k, v in grip_pose(side, g[0], g[1], g[2]).items(): out.setdefault(k, v)
    return out
def apply_pose(pose, loc=None):
    pose = expand_grip(pose)
    for n, b in pb.items():
        if n in ("root", "phone", "ember", "lids") or n.startswith("prop"): continue
        f, s, t = pose.get(n, REST.get(n, (0, 0, 0)))
        sf, ss, st = CAL[n]
        sgn = side_of(n) if n.split(".")[0] in LIMB else 1
        b.rotation_euler = (sf * R(f), st * R(t), ss * R(s * sgn))
    for n in ("pelvis", "root"):
        d = (loc or {}).get(n, (0, 0, 0))
        pb[n].location = LOCM[n] @ Vector(d)
    rr = (loc or {}).get("root_rot", (0, 0, 0))
    pb["root"].rotation_euler = (R(rr[0]), 0, 0)
    upd()

# ---- planar IK (sagittal Y-Z plane) for hands/feet on real geometry
def ik(upper, lower, target, init=(30, 30), sign_lower=1, iters=14):
    bu, bl = pb[upper], pb[lower]; sfu, sfl = CAL[upper][0], CAL[lower][0]
    a = list(init)
    def setang(a1, a2):
        e = bu.rotation_euler; bu.rotation_euler = (sfu * R(a1), e[1], e[2])
        e = bl.rotation_euler; bl.rotation_euler = (sfl * R(a2), e[1], e[2]); upd()
    def resid(a1, a2):
        setang(a1, a2); t = bl.tail; return Vector((t.y - target.y, t.z - target.z))
    for _ in range(iters):
        r0 = resid(*a)
        if r0.length < .002: break
        h = 1.5
        r1 = resid(a[0] + h, a[1]); r2 = resid(a[0], a[1] + h)
        J = Matrix(((((r1.x - r0.x) / h), ((r2.x - r0.x) / h)), (((r1.y - r0.y) / h), ((r2.y - r0.y) / h))))
        try: da = J.inverted() @ r0
        except ValueError: break
        a[0] -= max(-25, min(25, da.x * .8)); a[1] -= max(-25, min(25, da.y * .8))
        if sign_lower > 0: a[1] = max(2, a[1])
        else: a[1] = min(-2, a[1])
    setang(*a); return a
def level_foot(side, slope=0.0):
    b = pb[f"foot.{side}"]; sf = CAL[f"foot.{side}"][0]; e = b.rotation_euler; ang = 0.0
    for _ in range(8):
        b.rotation_euler = (sf * R(ang), e[1], e[2]); upd()
        d = (b.tail - b.head).normalized(); err = d.z - slope
        ang -= math.degrees(math.asin(max(-1, min(1, err)))) * .9 * sf * (1 if sf else 1) * 0 + math.degrees(err) * .0
        # direct: want dz = slope; rotating by dA changes dz by roughly cos(a)*dA
        ang += (-math.degrees(math.asin(max(-1, min(1, d.z))))) * sf * 0
        ang += 0
        break
    # solve by bisection on ang in [-90, 90]
    lo, hi = -90.0, 90.0
    def dz(a):
        b.rotation_euler = (sf * R(a), e[1], e[2]); upd(); return (b.tail - b.head).normalized().z
    for _ in range(18):
        mid = (lo + hi) / 2
        if (dz(mid) - slope) * (dz(lo) - slope) <= 0: hi = mid
        else: lo = mid
    b.rotation_euler = (sf * R((lo + hi) / 2), e[1], e[2]); upd()

IKT = {"hand.L": ("upper_arm.L", "forearm.L", (30, 50), 1), "hand.R": ("upper_arm.R", "forearm.R", (30, 50), 1),
       "foot.L": ("thigh.L", "shin.L", (30, -30), -1), "foot.R": ("thigh.R", "shin.R", (30, -30), -1)}
def key_frame(frame, pose, loc=None, iks=None):
    apply_pose(pose, loc)
    for tgt_name, tgt in (iks or {}).items():
        up, lo, init, sg = IKT[tgt_name]
        ik(up, lo, Vector(tgt), init, sg)
        if tgt_name.startswith("foot"): level_foot(tgt_name[-1], 0.0)
    for n, b in pb.items():
        if n in ("phone", "ember", "lids") or n.startswith("prop"): continue
        b.keyframe_insert("rotation_euler", frame=frame)
        if n in ("pelvis", "root"): b.keyframe_insert("location", frame=frame)

ACTS = {}
LOOPS = set()
def make(name, n, keys_or_fn, step=None, loop=False):
    act = bpy.data.actions.new(name); arm.animation_data_create(); arm.animation_data.action = act
    reset()
    if callable(keys_or_fn):
        for f in range(0, n + 1, step or 2):
            r = keys_or_fn(f); p, l = r[0], r[1]; key_frame(f + 1, p, l, r[2] if len(r) > 2 else None)
    else:
        for k in keys_or_fn: key_frame(k[0] + 1, k[1], k[2], k[3] if len(k) > 3 else None)
    act.use_fake_user = True; ACTS[name] = act; arm.animation_data.action = None; reset()
    if loop: LOOPS.add(name)
    return act
def keyed(name, n, kfs): return make(name, n, kfs)

def cyc(u, pts):
    u %= 1.0
    for (a, va), (b, vb) in zip(pts, pts[1:]):
        if a <= u <= b:
            x = (u - a) / (b - a) if b > a else 0; x = x * x * (3 - 2 * x); return va + (vb - va) * x
    return pts[0][1]
def lerp(a, b, t): return a + (b - a) * t
def sstep(x): x = max(0.0, min(1.0, x)); return x * x * (3 - 2 * x)
def mixp(A, Bp, t=1.0):
    out = {}
    for k in set(A) | set(Bp):
        a = A.get(k, REST.get(k, (0, 0, 0))); b = Bp.get(k, REST.get(k, (0, 0, 0)))
        out[k] = tuple(lerp(x, y, t) if (x is not None and y is not None) else (y if x is None else x) for x, y in zip(a, b))
    return out
def L(side, thigh, bend, foot=0, toe=0, abd=0):
    return {f"thigh.{side}": (thigh, abd, 0), f"shin.{side}": (-bend, 0, 0), f"foot.{side}": (foot, 0, 0), f"toe.{side}": (toe, 0, 0)}
def A_(side, up, abd, elbow, twist=0, wrist=0):
    return {f"upper_arm.{side}": (up, abd, twist), f"forearm.{side}": (elbow, 0, 0), f"hand.{side}": (wrist, 0, 0)}
def G(side, amt, point=0.0, thumb=None): return {f"grip.{side}": (amt, point, thumb)}

# ---------------- gait ----------------
def gait(u, amp, old=False):
    run = amp > 1.4
    pose = {}
    for side, ph in (("L", u), ("R", u + .5)):
        th = cyc(ph, [(0, 25 * amp), (.5, -20 * amp), (1, 25 * amp)]) if not run else 20 + 22 * math.cos(2 * math.pi * ph) - 6 * math.sin(4 * math.pi * ph)
        if run:
            bend = 30 + 75 * max(0, math.sin(2 * math.pi * (ph - .45))) ** 1.3
            foot = cyc(ph, [(0, 10), (.15, 0), (.5, -25), (.7, 10), (1, 10)])
        else:
            x = (ph % 1 - .5) / .5
            bend = 4 + (62 * math.sin(math.pi * x) ** 1.4 if 0 <= x <= 1 else 0) + 10 * max(0, math.sin(math.pi * (ph % 1) / .25)) * (ph % 1 < .25)
            if old: bend = 8 + .55 * (bend - 4)
            foot = cyc(ph, [(0, 12), (.1, 0), (.45, -8), (.55, -28), (.7, 2), (1, 12)])
            if old: foot *= .4
        pose.update(L(side, th, bend, foot, max(0, -foot - 8) * .8))
        ua = -th * (.85 if not run else 1.1)
        if old: ua *= .35
        pose.update(A_(side, ua, 4 + (3 if run else 0), (12 + .5 * max(0, ua)) if not run else 80 + .6 * ua, 0, 0))
        if run: pose.update(G(side, .8, 0, .5))
    twist = 5 * amp * math.sin(2 * math.pi * u) if not run else 9 * math.sin(2 * math.pi * u)
    pose["pelvis"] = (0, 2.5 * math.sin(2 * math.pi * u), twist)
    pose["spine"] = (2 if not run else 8, -1.5 * math.sin(2 * math.pi * u), -twist * .7)
    pose["spine2"] = (1 if not run else 4, 0, -twist * .5)
    pose["neck"] = (0, 0, twist * .3); pose["head"] = (-2 if not run else -8, 0, twist * .2)
    if old:
        pose["spine"] = (14, 0, -twist * .7); pose["spine2"] = (10, 0, -twist * .5); pose["head"] = (-16, 0, twist * .2)
    bob = .018 * amp if not run else .05
    z = -bob * (1 + math.cos(4 * math.pi * (u - .1))) / 2
    if old: z -= .02
    loc = {"pelvis": (.012 * math.sin(2 * math.pi * u) * (1 if not run else .5), 0, z)}
    return pose, loc
make("walk_loop", 24, lambda f: gait(f / 24, 1.0), 2, True)
make("run_loop", 16, lambda f: gait(f / 16, 1.9), 2, True)
make("walk_old_loop", 36, lambda f: gait(f / 36, .6, True), 3, True)

# ---------------- idles ----------------
def idle_pose(u, look=0):
    s = math.sin(2 * math.pi * u)
    p = {"spine2": (1.4 * s, 0, 0), "spine": (.6 * s, 0, 1.0 * math.sin(2 * math.pi * u + 1)),
         "head": (-1.0 * s, 0, 2.0 * math.sin(2 * math.pi * u + .5) + look), "neck": (0, 0, 0),
         "pelvis": (0, 1.3 * math.sin(2 * math.pi * u), 0)}
    p.update(A_("L", 0, 5 + .8 * s, 10 + 2 * s)); p.update(A_("R", 0, 5 + .8 * s, 10 + 2 * s))
    p.update(L("L", 1.5 * math.sin(2 * math.pi * u), 2)); p.update(L("R", -1.5 * math.sin(2 * math.pi * u), 2))
    return p, {"pelvis": (.008 * math.sin(2 * math.pi * u), 0, .003 * s)}
make("idle_loop", 96, lambda f: idle_pose(f / 96), 8, True)
def idle_look(f):
    u = f / 120
    look = cyc(u, [(0, 0), (.2, 42), (.4, 42), (.55, -38), (.75, -38), (.92, 0), (1, 0)])
    p, l = idle_pose(u, 0)
    p["head"] = (-1 + 2 * math.sin(2 * math.pi * u), 0, look * .7); p["neck"] = (0, 0, look * .3)
    p["spine2"] = (1.2 * math.sin(2 * math.pi * u), 0, look * .15)
    return p, l
make("idle_look_loop", 120, idle_look, 6, True)
def idle_cold(f):
    u = f / 48; s = math.sin(2 * math.pi * u * 8)
    p, l = idle_pose(f / 96 % 1)
    p.update(A_("L", 38, -18, 128, 0, 0)); p.update(A_("R", 42, -22, 132, 0, 0))
    p.update(G("L", .7, 0, .3)); p.update(G("R", .7, 0, .3))
    p["shoulder.L"] = (10 + 1.5 * s, 0, 0); p["shoulder.R"] = (10 - 1.5 * s, 0, 0)
    p["spine"] = (8 + .7 * s, 0, 0); p["spine2"] = (10, 0, 0); p["head"] = (-8 + 1.2 * s, 0, 0)
    p.update(L("L", 3, 8)); p.update(L("R", 3, 8)); p["pelvis"] = (0, 0, 0)
    return p, {"pelvis": (0, 0, -.012 + .002 * s)}
make("idle_cold_loop", 48, idle_cold, 2, True)

# ---------------- talk / phone / smoke ----------------
def jaw_env(f, n, amp=9):
    env = .55 + .45 * math.sin(2 * math.pi * f / (n / 2) + .7)
    return amp * env * abs(math.sin(math.pi * f / 6.0))
def talk(f):
    n = 96; u = f / n; p, l = idle_pose(u)
    g = math.sin(2 * math.pi * u * 2)
    p.update(A_("R", 28 + 14 * g, 14, 70 + 22 * math.sin(2 * math.pi * u * 2 + 1), 0, 8 * g)); p.update(G("R", .3 + .3 * max(0, g), 0, .2))
    p.update(A_("L", 12 + 6 * math.sin(2 * math.pi * u * 2 + 2.2), 10, 50 + 14 * math.sin(2 * math.pi * u * 2 + 1.4), 0, 5))
    p["head"] = (-2 + 4 * max(0, math.sin(2 * math.pi * u * 4)), 0, 6 * math.sin(2 * math.pi * u * 2))
    p["jaw"] = (jaw_env(f, n), 0, 0); p["spine2"] = (2 + 1.5 * g, 0, 3 * math.sin(2 * math.pi * u * 2 + .5))
    return p, l
make("talk_loop", 96, talk, 2, True)
def phone(f):
    n = 96; u = f / n; p, l = idle_pose(u)
    p.update(A_("R", 38 + 2 * math.sin(2 * math.pi * u), 22, 128 + 3 * math.sin(2 * math.pi * u * 2), 0, -10))
    p["hand.R"] = (-15, -12, 0); p.update(G("R", .75, 0, .35))
    p.update(A_("L", 18, 6, 78, 0, 0)); p.update(G("L", .5, 0, .3))
    p["head"] = (0, -9 + 1.5 * math.sin(2 * math.pi * u * 2), 4 * math.sin(2 * math.pi * u * 2))
    p["jaw"] = (jaw_env(f, n, 5) * (1 if f % 48 < 30 else 0.2), 0, 0)
    p["pelvis"] = (0, 3 * math.sin(2 * math.pi * u), 0)
    return p, l
make("phone_loop", 96, phone, 2, True)
def smoke(f):
    n = 144; u = f / n; p, l = idle_pose(u)
    arm_up = cyc(u, [(0, 0), (.14, 1), (.3, 1), (.42, 0), (1, 0)])
    exhale = cyc(u, [(0, 0), (.4, 0), (.5, 1), (.68, 1), (.8, 0), (1, 0)])
    p.update(A_("R", lerp(14, 46, arm_up), 12, lerp(82, 132, arm_up), 0, lerp(0, -12, arm_up)))
    p.update(G("R", .55, .9, .6))     # index and thumb clamp the cigarette, rest curled
    p.update(A_("L", 8, 10, 62)); p.update(G("L", .5)); p["head"] = (-1 - 14 * exhale + 3 * arm_up, 0, 3 * math.sin(2 * math.pi * u * 2))
    p["jaw"] = (7 * exhale + 2 * arm_up, 0, 0); p["spine2"] = (1.4 * math.sin(2 * math.pi * u * 3) + 3 * arm_up - 3 * exhale, 0, 0)
    p["shoulder.R"] = (-3 * arm_up, 0, 0)
    return p, l
make("smoke_loop", 144, smoke, 4, True)

# ---------------- one-shot reactions ----------------
def S0():
    p = {k: v for k, v in idle_pose(0)[0].items() if k not in ("spine2", "spine", "head", "pelvis")}
    return p
confused = []
for f, hd, tilt, shr, arms in ((0, 0, 0, 0, 0), (12, 28, 6, 0, .4), (26, 28, 8, 8, 1), (40, -26, -6, 8, 1), (56, -10, -2, 0, .5), (72, 0, 0, 0, 0)):
    p = S0(); p["head"] = (-2, tilt, hd); p["neck"] = (0, 0, hd * .3); p["spine2"] = (0, 0, hd * .15)
    p["shoulder.L"] = (shr, 0, 0); p["shoulder.R"] = (shr, 0, 0)
    for sd in "LR":
        p.update(A_(sd, 10 * arms, 5 + 25 * arms, 10 + 60 * arms, 0, 0)); p[f"hand.{sd}"] = (-20 * arms, 0, 0); p.update(G(sd, .25 + .1 * arms, 0, .1))
    confused.append((f, p, {"pelvis": (0, 0, -.01 * arms)}))
make("confused_loop", 72, confused, loop=True)
sty = []
for f, k in ((0, 0), (3, .7), (7, 1), (14, .85), (26, .3), (36, 0)):
    p = mixp(S0(), {"spine": (-9, 0, 0), "spine2": (-10, 0, 0), "head": (-10, 0, 0), "neck": (-4, 0, 0),
                    **A_("L", 52, 32, 78, 0, -10), **A_("R", 52, 32, 78, 0, -10),
                    **L("L", 12, 18), **L("R", -10, 14), "shoulder.L": (6, 0, 0), "shoulder.R": (6, 0, 0),
                    "jaw": (10, 0, 0), **G("L", 0, 0, 0), **G("R", 0, 0, 0)}, k)
    sty.append((f, p, {"pelvis": (0, .05 * k, -.035 * k)}))
keyed("startled", 36, sty)
shv = []
for f, pr in ((0, 0), (6, .5), (12, 1), (20, 1.0), (30, 0)):
    if f == 6:
        p = mixp(S0(), {**A_("L", 30, 10, 110), **A_("R", 30, 10, 110), "spine": (-4, 0, 0), "spine2": (-3, 0, 0), **L("L", -4, 6), **L("R", 4, 6), **G("L", .5), **G("R", .5)})
    else:
        p = mixp(S0(), {**A_("L", 88, 6, 6, 0, 20), **A_("R", 88, 6, 6, 0, 20), "spine": (10, 0, 0), "spine2": (6, 0, 0), "head": (-6, 0, 0),
                        **L("L", 28, 14, 8), **L("R", -18, 24, -20, 20), **G("L", 0, 0, .3), **G("R", 0, 0, .3)}, pr)
    shv.append((f, p, {"pelvis": (0, -.07 * pr if f != 6 else .02, -.03 * pr)}))
keyed("shove", 30, shv)

def lying(br=0):
    p = {"spine": (-3, 0, 0), "spine2": (-4 + br * 1.2, 0, 0), "head": (-26, 0, 38), "neck": (-8, 0, 12),
         **A_("L", 168, 22, 14, 0, 0), **A_("R", 150, 30, 40, 0, 0), **L("L", 4, 4, -15), **L("R", -5, 12, -20, 0, 6),
         **G("L", .2), **G("R", .3)}
    return p
LY_LOC = {"root": (0, -.02, .12), "root_rot": (86, 0, 0)}
fall = []
for f, pr in ((0, "stand"), (6, "stag"), (14, "tip"), (22, "tip2"), (30, "lie"), (36, "bounce"), (48, "lie")):
    if pr == "stand": fall.append((0, S0(), {}))
    elif pr == "stag":
        fall.append((f, mixp(S0(), {"spine": (6, 0, 0), "spine2": (-6, 0, 0), "head": (-6, 0, 0), **A_("L", 38, 30, 20), **A_("R", 30, 36, 24), **L("L", 14, 22), **L("R", -6, 10)}), {"pelvis": (0, 0, -.02)}))
    elif pr == "tip":
        fall.append((f, mixp(S0(), {"spine": (14, 0, 0), "spine2": (10, 0, 0), "head": (-12, 0, 0), **A_("L", 90, 24, 22), **A_("R", 100, 28, 24), **L("L", 20, 30), **L("R", 10, 40)}), {"root_rot": (24, 0, 0), "pelvis": (0, 0, -.05)}))
    elif pr == "tip2":
        fall.append((f, mixp(S0(), {"spine": (10, 0, 0), "spine2": (6, 0, 0), "head": (-22, 0, 0), **A_("L", 140, 20, 18), **A_("R", 150, 24, 20), **L("L", 28, 50), **L("R", 18, 70)}), {"root_rot": (62, 0, 0), "root": (0, 0, .03), "pelvis": (0, 0, -.06)}))
    elif pr == "bounce":
        p = mixp(S0(), lying()); p["spine2"] = (-9, 0, 0); fall.append((f, p, {**LY_LOC, "root": (0, -.02, .15)}))
    else: fall.append((f, mixp(S0(), lying()), LY_LOC))
keyed("fall", 48, fall)
def down(f):
    u = f / 96; s = math.sin(2 * math.pi * u)
    return mixp(S0(), lying(br=s)), {**LY_LOC, "pelvis": (0, 0, .003 * s)}
make("down_loop", 96, down, 8, True)
def carried(f):
    u = f / 60; s = math.sin(2 * math.pi * u); c = math.cos(2 * math.pi * u)
    p = mixp(S0(), {"head": (-34 + 5 * c, 6 * s, 14 * s), "neck": (-10, 0, 5 * s), "spine": (-3, 0, 0), "spine2": (-6, 0, 0),
                    **A_("L", -78 + 8 * s, 12 + 4 * c, 6, 0, 10), **A_("R", -70 - 8 * s, 18 - 4 * c, 10, 0, 10),
                    **L("L", -22 + 5 * s, 16, -12), **L("R", -26 - 5 * s, 20, -14), **G("L", .2 + .05 * s), **G("R", .2 - .05 * s)})
    return p, {"root_rot": (-88 + 2 * s, 0, 0), "root": (0, .08 * s * .2, 1.12 + .02 * c), "pelvis": (0, 0, 0)}
make("carried_loop", 60, carried, 4, True)

# ---------------- ladder / ledge (geometry constants shared with the test scene) ----------------
LADDER_Y, RUNG_PITCH = -.30, .30          # rungs at y=-0.30 (in front of the character), z = k * 0.30
LEDGE_Z, LEDGE_Y = 1.2, -.30              # ledge top z=1.2, front edge at y=-0.30, top runs towards -Y
def climb(f):
    u = (f / 32) % 1.0
    zr = .6 * u
    sw = lambda x: sstep(x)
    hz_R = 1.8 if u < .5 else 1.8 + .6 * sw((u - .5) / .5)
    hz_L = (1.5 + .6 * sw(u / .5)) if u < .5 else 2.1
    fz_R = .3 if u < .5 else .3 + .6 * sw((u - .5) / .5)
    fz_L = (0.0 + .6 * sw(u / .5)) if u < .5 else .6
    p = mixp(S0(), {"spine": (8, 0, 0), "spine2": (6, 0, 2.5 * math.sin(2 * math.pi * u)), "head": (-16, 0, 0), "pelvis": (4, 0, 4 * math.sin(2 * math.pi * u)),
                    **G("L", .85, 0, .6), **G("R", .85, 0, .6)})
    loc = {"root": (0, 0, zr), "pelvis": (0, -.12, -.03)}
    iks = {"hand.R": (LADDER_Y + .02, hz_R), "hand.L": (LADDER_Y + .02, hz_L),
           "foot.R": (LADDER_Y + .13, fz_R + .09), "foot.L": (LADDER_Y + .13, fz_L + .09)}
    # ik targets are world positions: add the root rise because key_frame solves in armature space
    iks = {k: (0, v[0], v[1]) for k, v in iks.items()}
    return p, loc, iks
make("climb_ladder_loop", 32, climb, 2, True)

def jpose(kind):
    if kind == 0: return S0(), {}
    if kind == 1: return mixp(S0(), {"spine": (22, 0, 0), "spine2": (12, 0, 0), "head": (-12, 0, 0), **A_("L", -38, 12, 12), **A_("R", -38, 12, 12), **L("L", 62, 74, 5), **L("R", 58, 72, 5)}), {"pelvis": (0, .06, -.19)}
    if kind == 2: return mixp(S0(), {"spine": (-4, 0, 0), "spine2": (-4, 0, 0), "head": (-6, 0, 0), **A_("L", 158, 14, 14), **A_("R", 158, 14, 14), **L("L", -4, 6, -38, 30), **L("R", 0, 8, -36, 30)}), {"root": (0, 0, .1), "pelvis": (0, 0, 0)}
    if kind == 3: return mixp(S0(), {"spine": (6, 0, 0), "head": (-8, 0, 0), **A_("L", 118, 28, 24), **A_("R", 118, 28, 24), **L("L", 36, 66, 10), **L("R", 26, 54, 10)}), {"root": (0, 0, .42)}
    if kind == 4: return mixp(S0(), {"spine": (4, 0, 0), "head": (-6, 0, 0), **A_("L", 70, 40, 20), **A_("R", 70, 40, 20), **L("L", 14, 22, 18), **L("R", 8, 18, 18)}), {"root": (0, 0, .12)}
    return mixp(S0(), {"spine": (24, 0, 0), "spine2": (12, 0, 0), "head": (-14, 0, 0), **A_("L", 36, 24, 28), **A_("R", 36, 24, 28), **L("L", 66, 86, 4), **L("R", 62, 84, 4)}), {"pelvis": (0, .06, -.21)}
keyed("jump", 36, [(f, *jpose(k)) for f, k in ((0, 0), (7, 1), (11, 2), (15, 3), (21, 4), (28, 5), (36, 0))])

HAND_TOP = LEDGE_Z + .03
vault = []
def VK(f, spine, spine2, head, loc, iks, hands=.7):
    p = mixp(S0(), {"spine": (spine, 0, 0), "spine2": (spine2, 0, 0), "head": (head, 0, 0), **G("L", hands, 0, .5), **G("R", hands, 0, .5)})
    vault.append((f, p, loc, {k: (0, v[0], v[1]) for k, v in iks.items()}))
VK(0, 0, 0, 0, {}, {})
VK(10, 16, 10, -16, {"pelvis": (0, -.1, -.04)}, {"hand.L": (LEDGE_Y - .05, HAND_TOP + .1), "hand.R": (LEDGE_Y - .05, HAND_TOP + .1)})
VK(20, 26, 16, -26, {"root": (0, -.12, .5), "pelvis": (0, -.12, -.05)}, {"hand.L": (LEDGE_Y - .12, HAND_TOP + .08), "hand.R": (LEDGE_Y - .12, HAND_TOP + .08), "foot.R": (LEDGE_Y - .1, LEDGE_Z + .2), "foot.L": (LEDGE_Y + .12, .62)})
VK(30, 34, 20, -26, {"root": (0, -.32, 1.0), "pelvis": (0, -.1, -.08)}, {"hand.L": (LEDGE_Y - .2, HAND_TOP + .06), "hand.R": (LEDGE_Y - .2, HAND_TOP + .06), "foot.R": (LEDGE_Y - .3, LEDGE_Z + .22), "foot.L": (LEDGE_Y - .12, LEDGE_Z + .26)})
VK(40, 20, 12, -14, {"root": (0, -.55, 1.2), "pelvis": (0, 0, -.1)}, {"hand.L": (LEDGE_Y - .45, HAND_TOP + .1), "hand.R": (LEDGE_Y - .45, HAND_TOP + .1), "foot.R": (LEDGE_Y - .5, LEDGE_Z + .09), "foot.L": (LEDGE_Y - .42, LEDGE_Z + .09)}, .3)
VK(48, 0, 0, 0, {"root": (0, -.6, 1.2)}, {})
make("vault", 48, vault)

# ---------------- sitting ----------------
def seated(br=0, lean=0):
    return {"spine": (lean * .5 + br * .5, 0, 0), "spine2": (lean + br, 0, 0), "head": (-lean * .6, 0, 0),
            **L("L", 88, 88, 0), **L("R", 88, 88, 0), **A_("L", 18, 8, 74, 0, 0), **A_("R", 18, 8, 74, 0, 0)}
SIT_LOC = {"pelvis": (0, .1, -.46)}
keyed("sit_down", 36, [(0, S0(), {}),
    (12, mixp(S0(), {"spine": (16, 0, 0), "spine2": (14, 0, 0), "head": (-10, 0, 0), **L("L", 18, 30), **L("R", 14, 28), **A_("L", 24, 8, 40), **A_("R", 24, 8, 40)}), {"pelvis": (0, .02, -.1)}),
    (24, mixp(S0(), seated(0, 10)), {"pelvis": (0, .08, -.38)}),
    (36, mixp(S0(), seated(0, 0)), SIT_LOC)])
keyed("stand_up", 36, [(0, mixp(S0(), seated(0, 0)), SIT_LOC),
    (10, mixp(S0(), seated(0, 20)), {"pelvis": (0, .05, -.4)}),
    (22, mixp(S0(), {"spine": (24, 0, 0), "spine2": (18, 0, 0), "head": (-14, 0, 0), **L("L", 40, 50), **L("R", 36, 48), **A_("L", 30, 8, 40), **A_("R", 30, 8, 40)}), {"pelvis": (0, .02, -.17)}),
    (36, S0(), {})])
def sit_idle(f):
    u = f / 96; s = math.sin(2 * math.pi * u)
    p = mixp(S0(), seated(s, 0)); p["head"] = (-1 * s, 0, 8 * math.sin(2 * math.pi * u * 1 + .4) * (1 if 20 < f < 70 else 0.4))
    p["foot.R"] = (6 * max(0, math.sin(2 * math.pi * u * 4)), 0, 0)
    return p, {"pelvis": (0, .1, -.46)}
make("sit_idle_loop", 96, sit_idle, 8, True)

# ---------------- gestures ----------------
def point_pose(k):
    p = mixp(S0(), {**A_("R", 84, 4, 8, 0, 6), **G("R", .9, 1.0, .8), "spine": (3, 0, 4), "spine2": (2, 0, 5), "head": (-3, 0, 6)}, k)
    return p
keyed("point", 36, [(0, S0(), {}), (8, mixp(S0(), {**A_("R", 50, 8, 90), **G("R", .9, 1, .8)}), {}), (14, point_pose(1), {"pelvis": (0, -.02, 0)}),
                    (26, point_pose(1), {"pelvis": (0, -.02, 0)}), (36, S0(), {})])
def knock(f):
    k = sstep(f / 8) * (1 - sstep((f - 40) / 8)); tap = (math.sin(2 * math.pi * (f - 8) / 10) if 8 <= f <= 38 else 0)
    p = mixp(S0(), {**A_("R", 68 * k, 6, 100 * k + 12 * tap * k, 0, 0), **G("R", .95 * k + .25 * (1 - k), 0, .6), "spine": (5 * k, 0, 0), "head": (-3 * k, 0, 0)})
    return p, {"pelvis": (0, -.03 * k, 0)}
make("knock", 48, knock, 2)
def pickup(f):
    u = f / 48; dn = cyc(u, [(0, 0), (.3, 1), (.5, 1), (.8, 0), (1, 0)]); hold = cyc(u, [(0, 0), (.5, 0), (.62, 1), (1, 1)])
    p = mixp(S0(), {"spine": (34 * dn, 0, 0), "spine2": (20 * dn, 0, 0), "head": (-18 * dn, 0, 0), **L("L", 36 * dn, 62 * dn, 0), **L("R", 20 * dn, 54 * dn, 0),
                    **G("R", lerp(.15, .9, hold))})
    loc = {"pelvis": (0, .08 * dn, -.2 * dn)}
    # right hand: ground object at (y=-0.32, z=0.1) then carried up to (y=-0.28, z=0.95) (offset z keeps wrist above the object)
    tz = lerp(.12, .95, sstep((u - .5) / .4)) if u > .5 else .12
    ty = -.32 if u <= .5 else lerp(-.32, -.26, sstep((u - .5) / .4))
    if u < .12: tz, ty = lerp(.95, .12, 0) , -.32
    iks = {"hand.R": (0, ty, tz)} if .1 <= u else {}
    if u < .1: iks = {}
    return p, loc, iks
make("pick_up", 48, pickup, 2)
def opendoor(f):
    u = f / 48; reach = cyc(u, [(0, 0), (.2, 1), (.4, 1), (.7, 1), (1, 0)]); pull = cyc(u, [(0, 0), (.35, 0), (.65, 1), (1, 0)])
    p = mixp(S0(), {"spine": (6 * reach, 0, -6 * reach), "spine2": (4 * reach, 0, -6 * reach), "head": (-4, 0, 8 * reach), **G("R", lerp(.2, .8, reach), 0, .5)})
    loc = {"pelvis": (0, lerp(0, .1, pull) - .03 * reach, -.02 * pull)}
    iks = {"hand.R": (0, lerp(-.42, -.2, pull), 1.0 - .03 * pull)} if reach > .3 else {}
    return p, loc, iks
make("open_door", 48, opendoor, 2)

exec(compile(open("D:/Faceless/models/src/build_human_v4_moves.py", encoding="utf-8").read(), "v4_moves", "exec"), globals())
# ============ NLA + export ============
bpy.ops.object.mode_set(mode='OBJECT')
arm.animation_data.action = None
order = ["idle_loop", "idle_look_loop", "idle_cold_loop", "walk_loop", "walk_old_loop", "run_loop", "talk_loop", "phone_loop", "smoke_loop",
         "confused_loop", "startled", "shove", "point", "knock", "pick_up", "open_door", "fall", "down_loop", "carried_loop",
         "climb_ladder_loop", "jump", "vault", "sit_down", "sit_idle_loop", "stand_up"] + MOVES
for name in order:
    act = ACTS[name]; tr = arm.animation_data.nla_tracks.new(); tr.name = name
    tr.strips.new(name, int(act.frame_range[0]), act)
for o in bpy.data.objects: o.select_set(o in (arm, j))
bpy.context.view_layer.objects.active = arm
OUT = os.environ.get("OUTGLB", "D:/Faceless/models/human_noir_v4.glb")
bpy.ops.export_scene.gltf(filepath=OUT, export_format='GLB', use_selection=True, export_animations=True,
                          export_animation_mode='NLA_TRACKS', export_skins=True, export_morph=True, export_apply=False)
print("TRIS", sum(len(p.vertices) - 2 for p in j.data.polygons), "VERTS", len(j.data.vertices), "BONES", len(arm.data.bones), "S", round(S, 3),
      "ACTIONS", len(ACTS), "KEYS", (len(j.data.shape_keys.key_blocks) - 1) if j.data.shape_keys else 0, "LOOPS", sorted(LOOPS))
bpy.ops.wm.save_as_mainfile(filepath=os.environ.get("OUTBLEND", "D:/Faceless/models/src/human_noir_v4.blend"))
