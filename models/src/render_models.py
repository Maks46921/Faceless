"""Renders glb models. Usage: blender -b -P render_models.py -- <outdir> <name> <glb> [<glb2>]
Views: front/side/back/threequarter/head/hands/top (+ noir variants). With two glbs side by side -> compare_*."""
import bpy, math, sys
from mathutils import Vector
argv = sys.argv[sys.argv.index("--") + 1:]
out, name, files = argv[0], argv[1], argv[2:]

def setup(style, res):
    bpy.ops.wm.read_factory_settings(use_empty=True)
    sc = bpy.context.scene; sc.render.engine = 'BLENDER_EEVEE'
    sc.render.resolution_x, sc.render.resolution_y = res
    w = bpy.data.worlds.new("w"); w.use_nodes = True; bg = w.node_tree.nodes["Background"]; sc.world = w
    if style == "neutral":
        bg.inputs[0].default_value = (.4, .41, .44, 1); bg.inputs[1].default_value = 1.0
        L = (((2, -3, 3), 4), ((-3, -1, 2), 1.5), ((0, 3, 2), 2.5))
    else:
        bg.inputs[0].default_value = (.01, .012, .018, 1); bg.inputs[1].default_value = 1.0
        L = (((3, -2.5, 3.5), 9), ((-3, 2, 1.5), 1.5))
    for loc, e in L:
        l = bpy.data.lights.new("l", "SUN"); l.energy = e
        if style == "noir": l.angle = math.radians(2)
        o = bpy.data.objects.new("l", l); sc.collection.objects.link(o); o.location = loc
        o.rotation_euler = (Vector((0, 0, .9)) - Vector(loc)).to_track_quat('-Z', 'Y').to_euler()
    return sc

def run(style, label, ang, zc, scale, elev=0, xc=0):
    n = len(files)
    sc = setup(style, (1400 * n, 1400))
    for i, f in enumerate(files):
        bpy.ops.import_scene.gltf(filepath=f)
        for o in bpy.context.selected_objects:
            if o.parent is None: o.location.x += (i - (n - 1) / 2) * 1.1
    c = bpy.data.cameras.new("c"); c.type = 'ORTHO'; c.ortho_scale = scale * n
    o = bpy.data.objects.new("c", c); sc.collection.objects.link(o); sc.camera = o
    a = math.radians(ang); e = math.radians(elev); d = 6
    o.location = (xc + math.sin(a) * math.cos(e) * d, -math.cos(a) * math.cos(e) * d, zc + math.sin(e) * d)
    o.rotation_euler = (Vector((xc, 0, zc)) - o.location).to_track_quat('-Z', 'Y').to_euler()
    sc.render.filepath = f"{out}/{label}.png"; bpy.ops.render.render(write_still=True)

pre = f"compare_{name}" if len(files) > 1 else name
import os
ZC = float(os.environ.get("ZC", .9)); SC = float(os.environ.get("SC", 2.1))
views = [("front", 0, ZC, SC, 0), ("side", 90, ZC, SC, 0), ("back", 180, ZC, SC, 0), ("threequarter", 35, ZC, SC, 0)]
if len(files) == 1:
    views += [("top", 0, ZC, SC, 55)]
    if not os.environ.get("NOCLOSE"): views += [("head", 25, 1.58, .55, 0), ("hands", 25, .9, .5, 0)]
for n, a, z, s, e in views:
    xc = .37 if n == "hands" else 0
    run("neutral", f"{pre}_{n}", a, z, s, e, xc)
    if len(files) == 1 and n in ("front", "threequarter", "head"):
        run("noir", f"{pre}_{n}_noir", a, z, s, e)
