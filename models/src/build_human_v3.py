"""Builds models/human_noir_v3.glb (+ models/src/human_noir_v3.blend).
Run: D:\\Cosmoteer\\blender.exe -b -P D:\\Faceless\\models\\src\\build_human_v3.py
Body = skin modifier + subdivision (shared mesh); accessories (lapels, hat, belt...) are separate shells joined at export.
"""
import bpy, bmesh, math
from mathutils import Vector

bpy.ops.wm.read_factory_settings(use_empty=True)

def mat(n, c, r=.8, m=0):
    x = bpy.data.materials.new(n); x.use_nodes = True; b = x.node_tree.nodes["Principled BSDF"]
    b.inputs[0].default_value = c; b.inputs['Roughness'].default_value = r; b.inputs['Metallic'].default_value = m
    return x

M = dict(coat=mat("coat", (.03, .03, .035, 1), .85), coat_dark=mat("coat_dark", (.012, .012, .016, 1), .9),
         gold=mat("gold_accent", (.69, .47, .05, 1), .45, .3), hair=mat("hair", (.01, .01, .01, 1), .85),
         pants=mat("pants", (.02, .02, .025, 1), .85), shoes=mat("shoes", (.005, .005, .008, 1), .4),
         skin=mat("skin", (.32, .27, .23, 1), .9), shirt=mat("shirt", (.55, .53, .5, 1), .9))
objs = []

def link(me, name, m, loc=(0, 0, 0)):
    o = bpy.data.objects.new(name, me); bpy.context.collection.objects.link(o); o.location = loc
    me.materials.append(m)
    for p in me.polygons: p.use_smooth = True
    objs.append(o); return o

def sel(o):
    for ob in bpy.context.selected_objects: ob.select_set(False)
    o.select_set(True); bpy.context.view_layer.objects.active = o

def chain(name, pts, edges, material, sub=2, clip_z=None):
    me = bpy.data.meshes.new(name); me.from_pydata([p[:3] for p in pts], edges, [])
    o = link(me, name, material); sel(o)
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
    if clip_z is not None:
        bm = bmesh.new(); bm.from_mesh(o.data)
        r = bmesh.ops.bisect_plane(bm, geom=bm.verts[:] + bm.edges[:] + bm.faces[:], plane_co=(0, 0, clip_z), plane_no=(0, 0, 1), clear_outer=False, clear_inner=True)
        bmesh.ops.holes_fill(bm, edges=[e for e in bm.edges if e.is_boundary], sides=64)
        bm.to_mesh(o.data); bm.free()
    for p in o.data.polygons: p.use_smooth = True
    return o

def shell(name, verts, faces, material, thick=.008, sub=1):
    me = bpy.data.meshes.new(name); me.from_pydata(verts, [], faces); me.update()
    o = link(me, name, material); sel(o)
    o.modifiers.new("sol", "SOLIDIFY").thickness = thick
    if sub: o.modifiers.new("sub", "SUBSURF").levels = sub
    for m in list(o.modifiers): bpy.ops.object.modifier_apply(modifier=m.name)
    for p in o.data.polygons: p.use_smooth = True
    return o

def bm_obj(name, bm, material, loc=(0, 0, 0)):
    me = bpy.data.meshes.new(name); bm.to_mesh(me); bm.free(); return link(me, name, material, loc)

def lathe(prof, seg=40):
    bm = bmesh.new(); vs = [bm.verts.new((r, 0, z)) for r, z in prof]
    es = [bm.edges.new((vs[i], vs[i + 1])) for i in range(len(vs) - 1)]
    bmesh.ops.spin(bm, geom=vs + es, cent=(0, 0, 0), axis=(0, 0, 1), angle=2 * math.pi, steps=seg)
    bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=1e-5)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    return bm

def box(sx, sy, sz, bev=.004):
    bm = bmesh.new(); bmesh.ops.create_cube(bm, size=1)
    for v in bm.verts: v.co.x *= sx; v.co.y *= sy; v.co.z *= sz
    bmesh.ops.bevel(bm, geom=bm.edges[:], offset=bev, segments=2)
    return bm

# ---- legs / shoes
if not __import__('os').environ.get('NOPANTS'): chain("pants", [(0, 0, .86, .1, .08), (-.09, 0, .82, .085, .08), (-.095, 0, .5, .075, .07), (-.1, 0, .025, .058, .055),
                (.09, 0, .82, .085, .08), (.095, 0, .5, .075, .07), (.1, 0, .025, .058, .055)],
      [(0, 1), (1, 2), (2, 3), (0, 4), (4, 5), (5, 6)], M['pants'])
chain("shoes", [(-.1, -.02, .07, .05, .055), (-.1, .06, .05, .052, .045), (-.1, .15, .038, .046, .034), (.1, -.02, .07, .05, .055), (.1, .06, .05, .052, .045), (.1, .15, .038, .046, .034)],
      [(0, 1), (1, 2), (3, 4), (4, 5)], M['shoes'], 2)
for sx in (-1, 1):
    bm_obj("sole", box(.11, .26, .02, .006), M['coat_dark'], (sx * .1, .045, .012))
    bm_obj("heel", box(.07, .06, .03, .006), M['coat_dark'], (sx * .1, -.055, .03))
    bm_obj("trouser_cuff", lathe([(.066, -.016), (.07, -.014), (.07, .014), (.066, .016)], 14), M['pants'], (sx * .1, 0, .08))

# ---- coat
chain("coat", [(0, 0, 1.18, .2, .135), (0, 0, 1.0, .19, .13), (0, 0, .9, .2, .135), (0, 0, .8, .21, .14), (0, 0, .69, .225, .145), (0, 0, .58, .235, .15), (0, 0, .5, .235, .15),
               (0, 0, 1.38, .2, .12), (0, 0, 1.5, .09, .09), (-.2, 0, 1.44, .07, .07), (-.31, 0, 1.2, .06, .06), (-.365, .04, .95, .052, .052),
               (.2, 0, 1.44, .07, .07), (.31, 0, 1.2, .06, .06), (.365, .04, .95, .052, .052)],
      [(0, 1), (1, 2), (2, 3), (3, 4), (4, 5), (5, 6), (0, 7), (7, 8), (7, 9), (9, 10), (10, 11), (7, 12), (12, 13), (13, 14)], M['coat'], 2, .6)
coat_o = objs[-1]
def fy(x, z, off=.008):
    h = coat_o.ray_cast(Vector((x, 1.0, z)), Vector((0, -1, 0)))
    return (h[1].y if h[0] else .1) + off
for sx in (-1, 1):
    P = [(.02, 1.47), (.1, 1.46), (.135, 1.37), (.1, 1.33), (.075, 1.18), (.022, 1.2)]
    vs = [(sx * x, fy(sx * x * .4, z, .022), z) for x, z in P]
    shell("lapel", vs, [(0, 1, 2, 3, 4, 5)] if sx > 0 else [(5, 4, 3, 2, 1, 0)], M['coat_dark'], .012, 1)
bm = lathe([(.072, 1.465), (.08, 1.5), (.07, 1.53), (.062, 1.52), (.066, 1.5), (.06, 1.47)], 20)
for v in bm.verts: v.co.y += .004
bm_obj("collar", bm, M['coat_dark'])
bm_obj("shirt_collar", lathe([(.054, 1.47), (.066, 1.515), (.064, 1.545), (.056, 1.54), (.054, 1.5)], 20), M['shirt'])
bm = bmesh.new(); bmesh.ops.create_cone(bm, cap_ends=False, segments=30, radius1=1, radius2=1, depth=.045)
for v in bm.verts: v.co.x *= .186; v.co.y *= .128
bo = bm_obj("belt", bm, M['coat_dark'], (0, 0, .99)); sel(bo)
bo.modifiers.new("s", "SOLIDIFY").thickness = .012; bpy.ops.object.modifier_apply(modifier="s")
bm_obj("buckle", box(.035, .01, .035, .003), M['gold'], (0, fy(0, .99, .02), .99))
for sx in (-1, 1):
    o = bm_obj("pocket", box(.075, .012, .03, .004), M['coat_dark'], (sx * .115, fy(sx * .115, .8, .01), .8)); o.rotation_euler[1] = sx * .12
    o = bm_obj("sleeve_cuff", lathe([(.06, -.014), (.064, -.012), (.064, .014), (.06, .016)], 14), M['coat_dark'], (sx * .357, .043, .965)); o.rotation_euler[1] = sx * .2
    o = bm_obj("sleeve_cuff_gold", lathe([(.0635, -.003), (.066, -.003), (.066, .003), (.0635, .003)], 14), M['gold'], (sx * .356, .043, .982)); o.rotation_euler[1] = sx * .2

if __import__('os').environ.get('BANDS'):
    co = [o for o in objs if o.name.startswith('coat')][0]
    for z in (1.47, 1.4, 1.33, 1.2, 1.1, .99, .85, .8):
        vs = [v.co for v in co.data.vertices if abs(v.co.z - z) < .015 and abs(v.co.x) < .3]
        print('BAND', z, round(min(v.x for v in vs), 3), round(max(v.x for v in vs), 3), round(min(v.y for v in vs), 3), round(max(v.y for v in vs), 3))
# ---- hands (palm, 4 fingers, thumb) + neck
pts = []; ed = []
def add(p): pts.append(p); return len(pts) - 1
for sx in (-1, 1):
    hx = sx * .372
    a = add((hx, .048, .975, .036, .026)); b = add((hx, .058, .865, .038, .024)); ed.append((a, b))
    for i, yy in enumerate((.026, .05, .074, .096)):
        L = (.075, .082, .078, .064)[i]
        f0 = add((hx, yy, .855, .0105, .0105)); f1 = add((hx, yy + .006, .855 - L * .5, .0098, .0098)); f2 = add((hx, yy + .012, .855 - L, .0085, .0085))
        ed += [(b, f0), (f0, f1), (f1, f2)]
    t0 = add((hx + sx * .01, .095, .9, .012, .012)); t1 = add((hx + sx * .012, .112, .855, .0105, .0105)); ed += [(a, t0), (t0, t1)]
n0 = add((0, 0, 1.44, .05, .05)); n1 = add((0, 0, 1.6, .046, .05)); ed.append((n0, n1))
chain("skin", pts, ed, M['skin'], 1)

# ---- head, hair, ears
def head_bm(k=1.0):
    hb = bmesh.new(); bmesh.ops.create_uvsphere(hb, u_segments=24, v_segments=14, radius=.1 * k)
    for v in hb.verts:
        v.co.x *= .85; v.co.y *= .95; v.co.z *= 1.15
        if v.co.z < 0:
            s = 1 + v.co.z * 1.3; v.co.x *= s; v.co.y *= (1 + v.co.z * .7)
    return hb
bm_obj("head", head_bm(), M['skin'], (0, .005, 1.66))
hb = head_bm(1.045)
bmesh.ops.delete(hb, geom=[f for f in hb.faces if not (f.calc_center_median().z > .045 or (f.calc_center_median().y < -.045 and f.calc_center_median().z > -.06))], context='FACES')
bm_obj("hair", hb, M['hair'], (0, .005, 1.66))
for sx in (-1, 1):
    bm = bmesh.new(); bmesh.ops.create_uvsphere(bm, u_segments=12, v_segments=8, radius=.03)
    for v in bm.verts: v.co.x *= .3; v.co.y *= .7
    bm_obj("ear", bm, M['skin'], (sx * .083, 0, 1.655))

# ---- tie, shirt front, buttons
chain("shirt", [(0, fy(0, 1.46, -.012), 1.46, .07, .014), (0, fy(0, 1.3, -.01), 1.3, .045, .012)], [(0, 1)], M['shirt'], 1)
chain("tie", [(0, fy(0, 1.42, .014), 1.42, .016, .01), (0, fy(0, 1.2, .022), 1.2, .026, .012)], [(0, 1)], M['gold'], 1)
bm = bmesh.new(); bmesh.ops.create_uvsphere(bm, u_segments=14, v_segments=8, radius=.02)
for v in bm.verts: v.co.z *= .8
bm_obj("knot", bm, M['gold'], (0, fy(0, 1.445, .012), 1.445))
for z in (1.1, .97, .85):
    bm = bmesh.new(); bmesh.ops.create_uvsphere(bm, u_segments=14, v_segments=8, radius=.014)
    bm_obj("button", bm, M['gold'], (.03, fy(.03, z, .008), z))

# ---- hat
H = (0, .005, 1.705)
prof = [(0, .118), (.03, .117), (.055, .113), (.075, .104), (.089, .09), (.097, .07), (.101, .045), (.103, .02), (.105, -.005), (.12, -.012), (.17, -.008), (.215, .004), (.228, .018), (.226, .012), (.2, -.006), (.15, -.022), (.106, -.022)]
bm = lathe(prof, 28)
for v in bm.verts:
    r = math.hypot(v.co.x, v.co.y)
    if r < .085 and v.co.z > .085: v.co.z -= .02 * math.exp(-(v.co.x / .03) ** 2)
    if r > .11: v.co.z -= .03 * (v.co.y / .23) + .012 * abs(v.co.x / .23)
bm_obj("hat", bm, M['coat_dark'], H)
bm_obj("hat_band", lathe([(.1, .008), (.1085, .012), (.1085, .036), (.1, .04)], 20), M['gold'], H)

# ---- join, scale, export
for o in bpy.data.objects: o.select_set(o in objs)
bpy.context.view_layer.objects.active = objs[0]; bpy.ops.object.join()
j = bpy.context.object; j.name = "human_noir"; j.data.name = "human_noir"
j.rotation_euler[2] = math.pi; bpy.ops.object.transform_apply(rotation=True, location=False)
mz = max((j.matrix_world @ v.co).z for v in j.data.vertices); s = 1.78 / mz
j.scale = (s, s, s); bpy.ops.object.transform_apply(scale=True)
bpy.ops.object.shade_smooth_by_angle(angle=math.radians(50))
[setattr(_o, 'name', _o.name + 'only') for _o in list(bpy.data.objects) if _o.name.endswith(('-col', '-convcol'))]  # Godot: -colonly = collider only, no visible mesh
bpy.ops.export_scene.gltf(filepath="D:/Faceless/models/human_noir_v3.glb", export_format='GLB', use_selection=True)
xs = [j.matrix_world @ Vector(c) for c in j.bound_box]
print("BBOX", [round(max(p[i] for p in xs) - min(p[i] for p in xs), 2) for i in range(3)], "minz", round(min(p.z for p in xs), 3))
print("TRIS", sum(len(p.vertices) - 2 for p in j.data.polygons), "VERTS", len(j.data.vertices), "scale", round(s, 3))
bpy.ops.wm.save_as_mainfile(filepath="D:/Faceless/models/src/human_noir_v3.blend")
