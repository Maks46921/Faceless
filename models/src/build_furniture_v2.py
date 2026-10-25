"""Builds chair_noir_v2.glb, table_noir_v2.glb, lamp_noir_v2.glb (+ .blend in models/src).
Run: D:\\Cosmoteer\\blender.exe -b -P D:\\Faceless\\models\\src\\build_furniture_v2.py
Materials are taken from the original glb files so the palette is unchanged. Dimensions match the originals.
"""
import bpy, bmesh, math
from mathutils import Vector

ROOT = "D:/Faceless/models"
objs = []

def load_mats(name):
    objs.clear()
    bpy.ops.wm.read_factory_settings(use_empty=True)
    bpy.ops.import_scene.gltf(filepath=f"{ROOT}/{name}_noir.glb")
    ms = {m.name: m for m in bpy.data.materials}
    o = [o for o in bpy.data.objects if o.type == 'MESH'][0]
    back = sum(v.co.y for v in o.data.vertices if v.co.z > .6) / max(1, len([1 for v in o.data.vertices if v.co.z > .6]))
    for ob in list(bpy.data.objects): bpy.data.objects.remove(ob)
    return ms, back

def finish(name, out):
    for o in bpy.data.objects: o.select_set(o in objs)
    bpy.context.view_layer.objects.active = objs[0]; bpy.ops.object.join()
    j = bpy.context.object; j.name = name; j.data.name = name
    bpy.ops.object.shade_smooth_by_angle(angle=math.radians(35))
    [setattr(_o, 'name', _o.name + 'only') for _o in list(bpy.data.objects) if _o.name.endswith(('-col', '-convcol'))]  # Godot: -colonly = collider only, no visible mesh
    bpy.ops.export_scene.gltf(filepath=f"{ROOT}/{out}.glb", export_format='GLB', use_selection=True)
    bb = [j.matrix_world @ Vector(c) for c in j.bound_box]
    print("RES", out, "dims", [round(max(p[i] for p in bb) - min(p[i] for p in bb), 3) for i in range(3)], "verts", len(j.data.vertices),
          "tris", sum(len(p.vertices) - 2 for p in j.data.polygons))
    bpy.ops.wm.save_as_mainfile(filepath=f"{ROOT}/src/{out}.blend")

def put(bm, mat, name="part", loc=(0, 0, 0)):
    me = bpy.data.meshes.new(name); bm.to_mesh(me); bm.free(); me.materials.append(mat)
    o = bpy.data.objects.new(name, me); bpy.context.collection.objects.link(o); o.location = loc
    for p in me.polygons: p.use_smooth = True
    objs.append(o); return o

def box(c, s, mat, bev=.004, taper=1.0, seg=2, rot=None):
    """box centered c, size s; taper scales the bottom face in x/y"""
    bm = bmesh.new(); bmesh.ops.create_cube(bm, size=1)
    for v in bm.verts:
        v.co.x *= s[0]; v.co.y *= s[1]; v.co.z *= s[2]
        if v.co.z < 0: v.co.x *= taper; v.co.y *= taper
    if bev: bmesh.ops.bevel(bm, geom=bm.edges[:], offset=bev, segments=seg, affect='EDGES')
    o = put(bm, mat, "box", c)
    if rot: o.rotation_euler = rot
    return o

def lathe(prof, mat, loc, seg=24, name="lathe"):
    bm = bmesh.new(); vs = [bm.verts.new((r, 0, z)) for r, z in prof]
    es = [bm.edges.new((vs[i], vs[i + 1])) for i in range(len(vs) - 1)]
    bmesh.ops.spin(bm, geom=vs + es, cent=(0, 0, 0), axis=(0, 0, 1), angle=2 * math.pi, steps=seg)
    bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=1e-5); bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    return put(bm, mat, name, loc)

# ===================== CHAIR 0.46 x 0.46 x 1.0 =====================
ms, back = load_mats("chair")
W, D = ms['wood'], ms['wood_dark']
by = 1 if back > 0 else -1             # which side the backrest is on
lx, ly = .195, .195                    # leg centers
for sx in (-1, 1):
    for sy in (-1, 1):
        isback = (sy == by)
        h = .46 if not isback else .99
        # tapered, chamfered leg (rear legs run on up as back posts)
        box((sx * lx, sy * ly, h / 2), (.04, .04, h), D, .004, .72 if not isback else .82)
# seat: thick slab with rounded edges + slight crown
box((0, 0, .445), (.46, .46, .04), W, .008, 1.0, 3)
box((0, 0, .4175), (.40, .40, .015), D, .004)       # seat underside lip
# aprons under seat
for sx in (-1, 1): box((sx * lx, 0, .385), (.025, .33, .05), D, .004)
for sy in (-1, 1): box((0, sy * ly, .385), (.33, .025, .05), D, .004)
# stretchers (side + front/back + cross)
for sx in (-1, 1): box((sx * lx, 0, .17), (.02, .34, .025), D, .004)
box((0, -by * ly, .17), (.34, .02, .025), D, .004)
box((0, by * ly, .15), (.34, .02, .025), D, .004)
# back: top rail (curved), two slats, mid rail
box((0, by * ly, .945), (.40, .035, .09), W, .01, 1.0, 3)
box((0, by * ly, .745), (.34, .025, .04), D, .004)
for sx in (-.07, 0, .07): box((sx, by * ly, .85), (.03, .018, .2), D, .004, 1.0)
for sx in (-.07, 0, .07): box((sx, by * ly, .60), (.03, .018, .2), D, .004, 1.0)
finish("chair_noir", "chair_noir_v2")

# ===================== TABLE 1.30 x 0.75 x 0.76 =====================
ms, back = load_mats("table")
W, D = ms['wood'], ms['wood_dark']
T = .045
box((0, 0, .76 - T / 2), (1.3, .75, T), W, .012, 1.0, 3)                    # top
box((0, 0, .76 - T - .008), (1.22, .67, .016), D, .006)                       # under-lip band
lx, ly = .55, .30
for sx in (-1, 1):
    for sy in (-1, 1):
        box((sx * lx, sy * ly, .3375), (.065, .065, .675), D, .006, .65)       # tapered legs
        box((sx * lx, sy * ly, .62), (.075, .075, .06), D, .006)               # leg top block
for sy in (-1, 1): box((0, sy * ly, .64), (1.0, .03, .11), D, .005)            # long aprons
for sx in (-1, 1): box((sx * lx, 0, .64), (.03, .54, .11), D, .005)            # end aprons
for sx in (-1, 1): box((sx * lx, 0, .16), (.025, .54, .03), D, .004)          # lower side stretchers
box((0, 0, .16), (1.0, .025, .03), D, .004)                                   # center stretcher
# drawer in one long apron
box((0, -.30 + (-.0) - .012, .64), (.42, .012, .09), W, .004)
bm = bmesh.new(); bmesh.ops.create_uvsphere(bm, u_segments=12, v_segments=8, radius=.014)
put(bm, W, "knob", (0, -.325, .64))
finish("table_noir", "table_noir_v2")

# ===================== LAMP 0.40 x 0.42 x 1.72 =====================
ms, back = load_mats("lamp")
Mt, Sh = ms['metal'], ms['lamp_shade']
lathe([(0, 0), (.195, 0), (.2, .006), (.2, .016), (.18, .026), (.08, .034), (.045, .05), (.03, .075), (0, .075)], Mt, (0, 0, 0), 32, "base")
lathe([(.03, .07), (.02, .08), (.02, .5)], Mt, (0, 0, 0), 14, "stem_lower")
lathe([(.0, .5), (.034, .5), (.034, .515), (.02, .525), (.02, .53), (.034, .54), (.034, .555), (0, .555)], Mt, (0, 0, 0), 14, "stem_ring")
lathe([(.014, .55), (.014, 1.35)], Mt, (0, 0, 0), 12, "stem_upper")
lathe([(.0, 1.3), (.028, 1.3), (.028, 1.31), (.018, 1.32), (.018, 1.33), (.028, 1.34), (.028, 1.35), (0, 1.35)], Mt, (0, 0, 0), 14, "stem_ring2")
# socket / bulb holder
lathe([(0, 1.35), (.03, 1.35), (.03, 1.40), (.022, 1.42), (.022, 1.47), (0, 1.47)], Mt, (0, 0, 0), 14, "socket")
# shade: thin open cone, two-sided thickness
lathe([(.205, 1.40), (.208, 1.402), (.12, 1.718), (.117, 1.716)], Sh, (0, 0, 0), 32, "shade")
# frame rings (top and bottom) + spider arms
for z, r in ((1.402, .207), (1.717, .119)):
    lathe([(r - .004, z - .004), (r + .004, z - .004), (r + .004, z + .004), (r - .004, z + .004)], Mt, (0, 0, 0), 32, "ring")
for i in range(3):
    a = i * 2 * math.pi / 3
    bm = bmesh.new(); bmesh.ops.create_cube(bm, size=1)
    for v in bm.verts: v.co.x *= .12; v.co.y *= .006; v.co.z *= .006
    o = put(bm, Mt, "spider", (math.cos(a) * .075, math.sin(a) * .075, 1.55)); o.rotation_euler[2] = a; o.rotation_euler[1] = 0
# finial
lathe([(0, 1.7), (.012, 1.7), (.012, 1.715), (.02, 1.718), (.02, 1.726), (0, 1.73)], Mt, (0, 0, 0), 14, "finial")
finish("lamp_noir", "lamp_noir_v2")
