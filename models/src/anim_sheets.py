"""blender -b -P anim_sheets.py -- glb outdir [action1,action2,...] [angle]  -> outdir/anim_<action>.png (8 frames each)"""
import bpy, math, sys, numpy as np
from mathutils import Vector
a = sys.argv[sys.argv.index("--") + 1:]
glb, out = a[0], a[1]; only = a[2].split(",") if len(a) > 2 and a[2] != "all" else None; ang = float(a[3]) if len(a) > 3 else 90
bpy.ops.wm.read_factory_settings(use_empty=True); bpy.ops.import_scene.gltf(filepath=glb)
arm = [o for o in bpy.data.objects if o.type == 'ARMATURE'][0]
sc = bpy.context.scene; sc.render.engine = 'BLENDER_EEVEE'; W, H = 350, 500
sc.render.resolution_x, sc.render.resolution_y = W, H
w = bpy.data.worlds.new("w"); w.use_nodes = True; w.node_tree.nodes["Background"].inputs[0].default_value = (.4, .41, .44, 1); sc.world = w
for loc, e in (((2, -3, 3), 4), ((-3, -1, 2), 1.5), ((0, 3, 2), 2.5)):
    l = bpy.data.lights.new("l", "SUN"); l.energy = e; o = bpy.data.objects.new("l", l); sc.collection.objects.link(o); o.location = loc
    o.rotation_euler = (Vector((0, 0, .9)) - Vector(loc)).to_track_quat('-Z', 'Y').to_euler()
c = bpy.data.cameras.new("c"); c.type = 'ORTHO'; import os
ZC = float(os.environ.get('ZC', 1.0)); c.ortho_scale = float(os.environ.get('SC', 2.5)); co = bpy.data.objects.new("c", c); sc.collection.objects.link(co); sc.camera = co
r = math.radians(ang); co.location = (math.sin(r) * 6, -math.cos(r) * 6, ZC); co.rotation_euler = (Vector((0, 0, ZC)) - co.location).to_track_quat('-Z', 'Y').to_euler()
for o in bpy.data.objects:
    if o.name.endswith(('-col', '-convcol')): o.hide_render = True
arm.animation_data_create()
for act in sorted(bpy.data.actions, key=lambda x: x.name):
    if only and act.name not in only: continue
    arm.animation_data.action = act
    if hasattr(act, "slots") and act.slots: arm.animation_data.action_slot = act.slots[0]
    f0, f1 = int(act.frame_range[0]), int(act.frame_range[1]); tiles = []
    for k in range(8):
        f = int(round(f0 + (f1 - f0) * k / 8)); sc.frame_set(f); sc.render.filepath = "C:/tmp_t/_f.png"; bpy.ops.render.render(write_still=True)
        im = bpy.data.images.load("C:/tmp_t/_f.png", check_existing=False); px = np.array(im.pixels[:], np.float32).reshape(H, W, 4); tiles.append(px); bpy.data.images.remove(im)
    sheet = np.concatenate(tiles, axis=1); im = bpy.data.images.new("s", W * 8, H); im.pixels = sheet.ravel(); im.filepath_raw = f"{out}/anim_{act.name}.png"; im.file_format = 'PNG'; im.save(); bpy.data.images.remove(im)
    print("SHEET", act.name, f0, f1)
