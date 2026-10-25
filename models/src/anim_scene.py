"""blender -b -P anim_scene.py -- glb out.png action scene(ladder|ledge|door|none) zc scale  : 8 frames side view with test geometry"""
import bpy, math, sys, numpy as np
from mathutils import Vector
a = sys.argv[sys.argv.index("--") + 1:]
glb, out, action, scene_kind = a[0], a[1], a[2], a[3]; zc = float(a[4]); scale = float(a[5]); ang = float(a[6]) if len(a) > 6 else 90
bpy.ops.wm.read_factory_settings(use_empty=True); bpy.ops.import_scene.gltf(filepath=glb)
arm = [o for o in bpy.data.objects if o.type == 'ARMATURE'][0]
sc = bpy.context.scene; sc.render.engine = 'BLENDER_EEVEE'; W, H = 420, 600
sc.render.resolution_x, sc.render.resolution_y = W, H
mat = bpy.data.materials.new("t"); mat.use_nodes = True; mat.node_tree.nodes["Principled BSDF"].inputs[0].default_value = (.55, .35, .15, 1)
def box(c, s):
    bpy.ops.mesh.primitive_cube_add(location=c); o = bpy.context.object; o.scale = (s[0] / 2, s[1] / 2, s[2] / 2); o.data.materials.append(mat)
if scene_kind == "ladder":
    for x in (-.22,): box((x, -.30, 1.6), (.04, .05, 3.4))
    for k in range(0, 12): box((0, -.30, .3 * k), (.44, .03, .03))
elif scene_kind == "ledge":
    box((0, -1.3, .6), (2.0, 2.0, 1.2))
elif scene_kind == "door":
    box((0, -.5, 1.0), (1.0, .05, 2.0)); box((.35, -.46, 1.0), (.05, .06, .05))
w = bpy.data.worlds.new("w2"); w.color = (.45, .46, .5); sc.world = w
for loc, e in (((2, -3, 3), 4), ((-3, -1, 2), 1.5), ((0, 3, 2), 2.5)):
    l = bpy.data.lights.new("l", "SUN"); l.energy = e; o = bpy.data.objects.new("l", l); sc.collection.objects.link(o); o.location = loc
    o.rotation_euler = (Vector((0, 0, .9)) - Vector(loc)).to_track_quat('-Z', 'Y').to_euler()
c = bpy.data.cameras.new("c"); c.type = 'ORTHO'; c.ortho_scale = scale; co = bpy.data.objects.new("c", c); sc.collection.objects.link(co); sc.camera = co
r = math.radians(ang); co.location = (math.sin(r) * 8, -math.cos(r) * 8 - .5 * (0 if ang == 0 else 1) * math.cos(r), zc); co.location.y = -math.cos(r) * 8
co.rotation_euler = (Vector((0, -.4 if ang == 90 else 0, zc)) - co.location).to_track_quat('-Z', 'Y').to_euler()
arm.animation_data_create(); act = [x for x in bpy.data.actions if x.name == action][0]
arm.animation_data.action = act
if hasattr(act, "slots") and act.slots: arm.animation_data.action_slot = act.slots[0]
f0, f1 = int(act.frame_range[0]), int(act.frame_range[1]); tiles = []
for k in range(8):
    f = int(round(f0 + (f1 - f0) * k / 7.0)) if scene_kind != "ladder" else int(round(f0 + (f1 - f0) * k / 8.0)); sc.frame_set(f); sc.render.filepath = "C:/tmp_t/_a.png"; bpy.ops.render.render(write_still=True)
    im = bpy.data.images.load("C:/tmp_t/_a.png", check_existing=False); tiles.append(np.array(im.pixels[:], np.float32).reshape(H, W, 4)); bpy.data.images.remove(im)
im = bpy.data.images.new("s", W * 8, H); im.pixels = np.concatenate(tiles, 1).ravel(); im.filepath_raw = out; im.file_format = 'PNG'; im.save()
