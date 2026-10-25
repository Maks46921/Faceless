"""Shared helpers for prop/asset builders. Blender conventions: Z up, model front = -Y (becomes +Z in glTF), origin at floor centre.
Naming for the game (Godot 4): '-col' / '-convcol' suffix = collision meshes, empties 'ip_use','ip_hit','ip_hand','ip_spark', top-level 'state_ok'/'state_loose'/'state_broken'.
"""
import bpy, bmesh, math, os, random
from mathutils import Vector, Matrix, Euler

ROOT = "D:/Faceless/models"
MATS = {}

def fresh():
    bpy.ops.wm.read_factory_settings(use_empty=True); MATS.clear()

def mat(name, color, rough=.8, metal=0.0, emit=None, emit_strength=0.0, alpha=None):
    if name in MATS: return MATS[name]
    m = bpy.data.materials.new(name); m.use_nodes = True; b = m.node_tree.nodes["Principled BSDF"]
    b.inputs[0].default_value = (*color, 1); b.inputs['Roughness'].default_value = rough; b.inputs['Metallic'].default_value = metal
    if emit is not None:
        b.inputs['Emission Color'].default_value = (*emit, 1); b.inputs['Emission Strength'].default_value = emit_strength
    if alpha is not None:
        b.inputs['Alpha'].default_value = alpha; m.blend_method = 'BLEND' if hasattr(m, 'blend_method') else None
    MATS[name] = m; return m

def palette():
    mat("concrete", (.40, .40, .38), .95); mat("concrete_dark", (.24, .24, .23), .95)
    mat("rebar_rust", (.20, .11, .07), .7, .5); mat("steel", (.42, .44, .47), .35, .9); mat("steel_dark", (.09, .10, .12), .5, .7)
    mat("rubber", (.02, .02, .02), .9); mat("wood", (.14, .09, .05), .85); mat("leather", (.10, .06, .04), .6)
    mat("paint_gray", (.20, .22, .23), .7, .2); mat("paint_green", (.10, .17, .13), .7, .2); mat("paint_yellow", (.55, .42, .06), .7)
    mat("glass", (.55, .62, .62), .1, 0.0); mat("gun_metal", (.04, .045, .06), .4, .8); mat("grip_brown", (.12, .06, .03), .6)
    mat("stone", (.22, .22, .21), .95); mat("plastic_black", (.03, .03, .035), .5); mat("liquid_amber", (.5, .3, .05), .2)
    mat("gold_glow", (1.0, .72, .18), .3, 0.0, emit=(1.0, .55, .08), emit_strength=2.6)
    mat("gold_glow_pale", (1.0, .85, .5), .3, 0.0, emit=(1.0, .75, .35), emit_strength=1.3)
    mat("mannequin_gray", (.5, .5, .5), .6); mat("cast_iron", (.07, .065, .06), .7, .6); mat("asphalt", (.07, .07, .075), .95)
    mat("soot", (.01, .01, .01), .95); mat("copper", (.55, .28, .12), .35, .9); mat("wire_red", (.35, .03, .03), .6); mat("wire_black", (.02, .02, .02), .6)
    mat("sign_yellow", (.65, .5, .05), .6); mat("brick", (.22, .1, .08), .95)
    return MATS

def collection(): return bpy.context.scene.collection

def finish_obj(o, parent=None, smooth=True):
    if parent: o.parent = parent
    if smooth and o.type == 'MESH':
        for p in o.data.polygons: p.use_smooth = True
    return o

def mesh_obj(name, bm, material, loc=(0, 0, 0), rot=(0, 0, 0), scale=(1, 1, 1), parent=None, smooth=True):
    me = bpy.data.meshes.new(name); bm.to_mesh(me); bm.free()
    if material is not None: me.materials.append(material)
    o = bpy.data.objects.new(name, me); collection().objects.link(o)
    o.location = loc; o.rotation_euler = rot; o.scale = scale
    return finish_obj(o, parent, smooth)

def empty(name, loc=(0, 0, 0), parent=None, display='PLAIN_AXES', size=.1, rot=(0, 0, 0)):
    o = bpy.data.objects.new(name, None); o.empty_display_type = display; o.empty_display_size = size
    collection().objects.link(o); o.location = loc; o.rotation_euler = rot
    if parent: o.parent = parent
    return o

def bevel(bm, off=.004, seg=2):
    bmesh.ops.bevel(bm, geom=bm.edges[:], offset=off, segments=seg, affect='EDGES')

def box(size, material, loc=(0, 0, 0), bev=.004, rot=(0, 0, 0), parent=None, name="box", taper=None, seg=2):
    bm = bmesh.new(); bmesh.ops.create_cube(bm, size=1)
    for v in bm.verts:
        v.co.x *= size[0]; v.co.y *= size[1]; v.co.z *= size[2]
        if taper and v.co.z < 0: v.co.x *= taper; v.co.y *= taper
    if bev: bevel(bm, bev, seg)
    return mesh_obj(name, bm, material, loc, rot, parent=parent)

def cyl(r, h, material, loc=(0, 0, 0), seg=16, bev=0, rot=(0, 0, 0), parent=None, name="cyl", r2=None, caps=True):
    bm = bmesh.new()
    bmesh.ops.create_cone(bm, cap_ends=caps, segments=seg, radius1=r, radius2=(r if r2 is None else r2), depth=h)
    if bev: bevel(bm, bev, 1)
    return mesh_obj(name, bm, material, loc, rot, parent=parent)

def sphere(r, material, loc=(0, 0, 0), seg=14, rings=8, scale=(1, 1, 1), parent=None, name="sph"):
    bm = bmesh.new(); bmesh.ops.create_uvsphere(bm, u_segments=seg, v_segments=rings, radius=r)
    return mesh_obj(name, bm, material, loc, scale=scale, parent=parent)

def lathe(prof, material, loc=(0, 0, 0), seg=24, parent=None, name="lathe", rot=(0, 0, 0)):
    bm = bmesh.new(); vs = [bm.verts.new((r, 0, z)) for r, z in prof]
    es = [bm.edges.new((vs[i], vs[i + 1])) for i in range(len(vs) - 1)]
    bmesh.ops.spin(bm, geom=vs + es, cent=(0, 0, 0), axis=(0, 0, 1), angle=2 * math.pi, steps=seg)
    bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=1e-5); bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    return mesh_obj(name, bm, material, loc, rot, parent=parent)

def extrude_profile(pts, depth, material, loc=(0, 0, 0), rot=(0, 0, 0), parent=None, name="prof", bev=.0015, axis='Y'):
    """closed polygon in the XZ plane extruded along Y (centered)."""
    bm = bmesh.new(); vs = [bm.verts.new((x, -depth / 2, z)) for x, z in pts]
    f = bm.faces.new(vs); r = bmesh.ops.extrude_face_region(bm, geom=[f])
    vv = [e for e in r['geom'] if isinstance(e, bmesh.types.BMVert)]
    bmesh.ops.translate(bm, verts=vv, vec=(0, depth, 0)); bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    if bev: bevel(bm, bev, 1)
    return mesh_obj(name, bm, material, loc, rot, parent=parent)

def poly_prism(pts2d, h, material, loc=(0, 0, 0), parent=None, name="prism", bev=0):
    bm = bmesh.new(); vs = [bm.verts.new((x, y, 0)) for x, y in pts2d]
    f = bm.faces.new(vs); r = bmesh.ops.extrude_face_region(bm, geom=[f])
    vv = [e for e in r['geom'] if isinstance(e, bmesh.types.BMVert)]
    bmesh.ops.translate(bm, verts=vv, vec=(0, 0, h)); bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    if bev: bevel(bm, bev, 1)
    return mesh_obj(name, bm, material, loc, parent=parent)

def rock_blob(r, material, seed=1, loc=(0, 0, 0), flat=.7, subdiv=2, rough=.25, parent=None, name="rock"):
    rnd = random.Random(seed)
    bm = bmesh.new(); bmesh.ops.create_icosphere(bm, subdivisions=subdiv, radius=r)
    for v in bm.verts:
        k = 1 + rnd.uniform(-rough, rough); v.co *= k; v.co.z *= flat
    return mesh_obj(name, bm, material, loc, parent=parent, smooth=True)

def join(objs, name):
    for o in bpy.data.objects: o.select_set(False)
    for o in objs: o.select_set(True)
    bpy.context.view_layer.objects.active = objs[0]; bpy.ops.object.join()
    j = bpy.context.object; j.name = name; j.data.name = name
    set_active(j); bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
    return j

def set_active(o):
    for x in bpy.data.objects: x.select_set(False)
    o.select_set(True); bpy.context.view_layer.objects.active = o

def apply_all_transforms(objs):
    for o in objs:
        if o.type == 'MESH':
            set_active(o); bpy.ops.object.transform_apply(location=False, rotation=True, scale=True)

def smooth_angle(objs, deg=40):
    for o in objs:
        if o.type == 'MESH':
            set_active(o); bpy.ops.object.shade_smooth_by_angle(angle=math.radians(deg))

# ---------------- animation: per-object keyframes -> NLA track named after the animation ----------------
def animate(obj, anim_name, keys, fps=24):
    """keys: [(frame, {'loc':(x,y,z), 'rot':(rx,ry,rz) radians, 'scale':(sx,sy,sz)})] in the object's local (parent) space."""
    obj.animation_data_create()
    act = bpy.data.actions.new(f"{anim_name}_{obj.name}"); obj.animation_data.action = act
    for f, d in keys:
        if 'loc' in d: obj.location = d['loc']; obj.keyframe_insert("location", frame=f)
        if 'rot' in d: obj.rotation_euler = d['rot']; obj.keyframe_insert("rotation_euler", frame=f)
        if 'scale' in d: obj.scale = d['scale']; obj.keyframe_insert("scale", frame=f)
    obj.animation_data.action = None
    tr = obj.animation_data.nla_tracks.new(); tr.name = anim_name; tr.strips.new(anim_name, int(keys[0][0]), act)
    bpy.context.scene.render.fps = fps
    return act

def export(name, objs=None, anims=False, out_dir=None):
    path = f"{out_dir or ROOT}/{name}.glb"
    for o in bpy.data.objects: o.select_set(True if objs is None else o in objs)
    kw = dict(filepath=path, export_format='GLB', use_selection=True, export_apply=True)
    if anims: kw.update(export_animations=True, export_animation_mode='NLA_TRACKS')
    else: kw.update(export_animations=False)
    [setattr(_o, 'name', _o.name + 'only') for _o in list(bpy.data.objects) if _o.name.endswith(('-col', '-convcol'))]  # Godot: -colonly = collider only, no visible mesh
    bpy.ops.export_scene.gltf(**kw)
    tris = 0; names = []
    for o in bpy.data.objects:
        if o.type == 'MESH':
            o.data.calc_loop_triangles(); tris += len(o.data.loop_triangles)
        names.append(o.name)
    bb = [o.matrix_world @ Vector(c) for o in bpy.data.objects if o.type == 'MESH' for c in o.bound_box]
    dims = [round(max(p[i] for p in bb) - min(p[i] for p in bb), 3) for i in range(3)] if bb else [0, 0, 0]
    print("RES", name, "tris", tris, "dims(xyz blender)", dims, "nodes", len(names))
    return tris, dims

def beam(p0, p1, sx, sy, material, parent=None, name="beam", bev=.003):
    p0, p1 = Vector(p0), Vector(p1); d = p1 - p0; mid = (p0 + p1) / 2
    o = box((sx, sy, d.length), material, loc=tuple(mid), bev=bev, parent=parent, name=name)
    o.rotation_mode = 'QUATERNION'; o.rotation_quaternion = Vector((0, 0, 1)).rotation_difference(d.normalized()); o.rotation_mode = 'XYZ'
    return o
def tube(p0, p1, r, material, parent=None, name="tube", seg=8):
    p0, p1 = Vector(p0), Vector(p1); d = p1 - p0; mid = (p0 + p1) / 2
    o = cyl(r, d.length, material, loc=tuple(mid), seg=seg, parent=parent, name=name)
    o.rotation_mode = 'QUATERNION'; o.rotation_quaternion = Vector((0, 0, 1)).rotation_difference(d.normalized()); o.rotation_mode = 'XYZ'
    return o
