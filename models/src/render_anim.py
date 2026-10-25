"""blender -b -P render_anim.py -- glb outdir action f1,f2,... [view_angle] [zc] [scale]  renders posed frames (neutral light)."""
import bpy, math, sys
from mathutils import Vector
a = sys.argv[sys.argv.index("--") + 1:]
glb, out, action = a[0], a[1], a[2]; frames = [int(x) for x in a[3].split(",")]
ang = float(a[4]) if len(a) > 4 else 90; zc = float(a[5]) if len(a) > 5 else .9; sc_ = float(a[6]) if len(a) > 6 else 2.1
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=glb)
arm = [o for o in bpy.data.objects if o.type == 'ARMATURE'][0]
print("ACTIONS", [x.name for x in bpy.data.actions])
act = [x for x in bpy.data.actions if action in x.name][0]
arm.animation_data_create(); arm.animation_data.action = act
if hasattr(act, "slots") and act.slots: arm.animation_data.action_slot = act.slots[0]
sc = bpy.context.scene; sc.render.engine = 'BLENDER_EEVEE'; sc.render.resolution_x = 700; sc.render.resolution_y = 1000 if sc_ > 1 else 700
w = bpy.data.worlds.new("w"); w.use_nodes = True; w.node_tree.nodes["Background"].inputs[0].default_value = (.4, .41, .44, 1); sc.world = w
for loc, e in (((2, -3, 3), 4), ((-3, -1, 2), 1.5), ((0, 3, 2), 2.5)):
    l = bpy.data.lights.new("l", "SUN"); l.energy = e; o = bpy.data.objects.new("l", l); sc.collection.objects.link(o); o.location = loc
    o.rotation_euler = (Vector((0, 0, .9)) - Vector(loc)).to_track_quat('-Z', 'Y').to_euler()
c = bpy.data.cameras.new("c"); c.type = 'ORTHO'; c.ortho_scale = sc_; o = bpy.data.objects.new("c", c); sc.collection.objects.link(o); sc.camera = o
r = math.radians(ang); o.location = (math.sin(r) * 6, -math.cos(r) * 6, zc); o.rotation_euler = (Vector((0, 0, zc)) - o.location).to_track_quat('-Z', 'Y').to_euler()
for f in frames:
    sc.frame_set(f); sc.render.filepath = f"{out}/{action}_f{f:03d}.png"; bpy.ops.render.render(write_still=True)
