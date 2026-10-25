"""Test cutscene (Blender only): sky, clouds, a passer-by in a coat and the golden spirit. 6 key frames -> renders/city/mechanics/spirit_cutscene_*.png + sheet.
blender -b -P cutscene_spirit.py"""
import bpy, math, bmesh, random, numpy as np
from mathutils import Vector
M = "D:/Faceless/models"; OUT = "D:/Faceless/renders/city/mechanics"
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=f"{M}/spirit_gold.glb")
sp_objs = list(bpy.data.objects); sp_arm = [o for o in sp_objs if o.type == 'ARMATURE'][0]
spirit_actions = {a.name: a for a in bpy.data.actions}
bpy.ops.import_scene.gltf(filepath=f"{M}/human_noir_v4.glb")
pe_arm = [o for o in bpy.data.objects if o.type == 'ARMATURE' and o is not sp_arm][0]
SP = {n: a for n, a in spirit_actions.items()}
PE = {a.name: a for a in bpy.data.actions if a not in spirit_actions.values()}
for o in bpy.data.objects:
    if o.parent is None and o not in sp_objs:
        o.location = (0, -1.2, 0); o.rotation_euler = (0, 0, math.pi)
sc = bpy.context.scene; sc.render.engine = 'BLENDER_EEVEE'; sc.render.resolution_x = 760; sc.render.resolution_y = 500; sc.render.fps = 24; sc.view_settings.view_transform = "Standard"
w = bpy.data.worlds.new("sky"); w.color = (.05, .06, .12); sc.world = w
# sky dome with a vertical gradient (warm horizon, deep blue zenith)
dome = bpy.data.objects.new("dome", bpy.data.meshes.new("dome"))
bm = bmesh.new(); bmesh.ops.create_uvsphere(bm, u_segments=32, v_segments=24, radius=160); bmesh.ops.reverse_faces(bm, faces=bm.faces)
bm.to_mesh(dome.data); bm.free(); sc.collection.objects.link(dome)
dm = bpy.data.materials.new("domemat"); dm.use_nodes = True; dn = dm.node_tree; dn.nodes.clear()
tcn = dn.nodes.new("ShaderNodeTexCoord"); sep = dn.nodes.new("ShaderNodeSeparateXYZ"); mr = dn.nodes.new("ShaderNodeMapRange")
cr2 = dn.nodes.new("ShaderNodeValToRGB"); em = dn.nodes.new("ShaderNodeEmission"); out = dn.nodes.new("ShaderNodeOutputMaterial")
dn.links.new(tcn.outputs['Object'], sep.inputs[0]); dn.links.new(sep.outputs['Z'], mr.inputs[0])
mr.inputs[1].default_value = -30; mr.inputs[2].default_value = 150
dn.links.new(mr.outputs[0], cr2.inputs[0])
cr2.color_ramp.elements[0].position = .0; cr2.color_ramp.elements[0].color = (.8, .45, .18, 1)
cr2.color_ramp.elements[1].position = .6; cr2.color_ramp.elements[1].color = (.02, .035, .11, 1)
cr2.color_ramp.elements.new(.3).color = (.28, .16, .26, 1)
dn.links.new(cr2.outputs[0], em.inputs[0]); em.inputs[1].default_value = 1.2; dn.links.new(em.outputs[0], out.inputs[0]); dome.data.materials.append(dm)
# ground
bpy.ops.mesh.primitive_plane_add(size=300, location=(0, 0, 0)); gp = bpy.context.object
gm = bpy.data.materials.new("ground"); gm.use_nodes = True
gm.node_tree.nodes["Principled BSDF"].inputs[0].default_value = (.04, .04, .05, 1); gm.node_tree.nodes["Principled BSDF"].inputs['Roughness'].default_value = .6
gp.data.materials.append(gm)
# clouds
rnd = random.Random(3); cm = bpy.data.materials.new("cloud"); cm.use_nodes = True
cm.node_tree.nodes["Principled BSDF"].inputs[0].default_value = (.75, .6, .6, 1); cm.node_tree.nodes["Principled BSDF"].inputs['Roughness'].default_value = 1; cm.node_tree.nodes["Principled BSDF"].inputs['Emission Color'].default_value = (.9, .55, .45, 1); cm.node_tree.nodes["Principled BSDF"].inputs['Emission Strength'].default_value = .6
for i in range(26):
    cx, cy, cz = rnd.uniform(-60, 60), rnd.uniform(15, 90), rnd.uniform(9, 40)
    for k in range(rnd.randint(4, 7)):
        bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=2, radius=rnd.uniform(2.5, 6), location=(cx + rnd.uniform(-5, 5), cy + rnd.uniform(-3, 3), cz + rnd.uniform(-1, 1)))
        o = bpy.context.object; o.scale.z = .45; o.data.materials.append(cm)
l = bpy.data.lights.new("rim", "SUN"); l.energy = 1.2; l.color = (.7, .75, 1.0); o = bpy.data.objects.new("rim", l); sc.collection.objects.link(o); o.rotation_euler = (1.0, .2, .6)
pl = bpy.data.lights.new("glow", "POINT"); pl.energy = 4000; pl.color = (1.0, .7, .3); pl.shadow_soft_size = .5
plo = bpy.data.objects.new("glow", pl); sc.collection.objects.link(plo)
cam = bpy.data.cameras.new("cam"); cam.lens = 28; co = bpy.data.objects.new("cam", cam); sc.collection.objects.link(co); sc.camera = co

def set_action(arm, act, frame):
    if not arm.animation_data: arm.animation_data_create()
    arm.animation_data.action = act
    if hasattr(act, "slots") and act.slots: arm.animation_data.action_slot = act.slots[0]
def look(cam_pos, target, lens):
    co.location = cam_pos; cam.lens = lens
    co.rotation_euler = (Vector(target) - Vector(cam_pos)).to_track_quat('-Z', 'Y').to_euler()
def spirit_pos():
    p = sp_arm.matrix_world @ sp_arm.pose.bones["root"].head; return Vector((p.x, p.y, p.z + 1.2))
shots = []
def shot(name, spirit_act, sf, person_act, pf, cam_pos, target_fn, lens=28):
    set_action(sp_arm, SP[spirit_act], sf); set_action(pe_arm, PE[person_act], pf)
    gone = spirit_act == "enter" and sf >= 36
    for o in sp_objs: o.hide_render = gone
    sc.frame_set(pf if gone else sf)
    sp = spirit_pos(); plo.location = sp + Vector((0, -.4, .3)); look(cam_pos, target_fn(sp), lens)
    sc.render.filepath = f"{OUT}/spirit_cutscene_{name}.png"; bpy.ops.render.render(write_still=True); shots.append(sc.render.filepath)
print("PERSON ACTIONS", sorted(PE)[:30])
idle_p = "idle_loop"; start_p = [n for n in PE if n.startswith("startled")][0]
shot("1_up", "descend", 14, idle_p, 1, (3.5, -3.5, 1.0), lambda sp: sp + Vector((0, 0, 3)), 24)
shot("2_descend", "descend", 82, idle_p, 1, (6.5, -8.0, 2.2), lambda sp: sp, 30)
shot("3_near", "descend", 132, idle_p, 1, (5.4, -6.4, 1.4), lambda sp: Vector((0, -.5, 1.3)), 30)
shot("4_touch", "idle", 30, idle_p, 1, (3.2, -.6, 1.4), lambda sp: Vector((0, -.6, 1.3)), 30)
shot("5_enter", "enter", 22, idle_p, 1, (2.2, -2.5, 1.6), lambda sp: Vector((0, -1.2, 1.5)), 34)
shot("6_alive", "enter", 37, start_p, 12, (1.8, -.2, 1.6), lambda sp: Vector((0, -1.2, 1.5)), 34)
tiles = []
for f in shots:
    im = bpy.data.images.load(f); tiles.append(np.array(im.pixels[:], np.float32).reshape(500, 760, 4))
rows = [np.concatenate(tiles[0:3], 1), np.concatenate(tiles[3:6], 1)][::-1]
im = bpy.data.images.new("sheet", 760 * 3, 1000); im.pixels = np.concatenate(rows, 0).ravel(); im.filepath_raw = f"{OUT}/spirit_cutscene_sheet.png"; im.file_format = 'PNG'; im.save()
print("OK")
