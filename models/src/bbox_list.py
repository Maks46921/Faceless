"""blender -b -P bbox_list.py -- out.json : bbox (blender coords, -col/ip hidden) of every glb"""
import bpy, sys, os, json
from mathutils import Vector
out = sys.argv[sys.argv.index("--") + 1]
R = "D:/Faceless/models"
res = {}
for sub in ("city/buildings", "city/vehicles", "city/props", "city/animals", "city/people"):
    for f in sorted(os.listdir(f"{R}/{sub}")):
        if not f.endswith(".glb") or f.endswith("_far.glb"): continue
        bpy.ops.wm.read_factory_settings(use_empty=True)
        bpy.ops.import_scene.gltf(filepath=f"{R}/{sub}/{f}")
        mn = Vector((1e9,) * 3); mx = Vector((-1e9,) * 3)
        for o in bpy.data.objects:
            if o.type != 'MESH' or "col" in o.name: continue
            for v in o.bound_box:
                w = o.matrix_world @ Vector(v)
                mn = Vector(map(min, mn, w)); mx = Vector(map(max, mx, w))
        res[f"{sub}/{f}"] = [round(x, 2) for x in (*mn, *mx)]
json.dump(res, open(out, "w"), indent=0)
