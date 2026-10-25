"""blender -b -P render_items.py -- out.png cell file1.glb file2.glb ... : each glb as one tile, 3 views (front 3/4, side, top), neutral light, auto-framed."""
import bpy, math, sys, numpy as np
from mathutils import Vector
a = sys.argv[sys.argv.index("--") + 1:]; out = a[0]; cell = int(a[1]); files = a[2:]
tiles = []
for f in files:
    for ang, elev in ((35, 25), (90, 0), (0, 80)):
        bpy.ops.wm.read_factory_settings(use_empty=True); bpy.ops.import_scene.gltf(filepath=f)
        import os
        hide = [h for h in os.environ.get('HIDE', '').split(',') if h]
        def hid(o):
            while o:
                if o.name in hide: return True
                o = o.parent
            return False
        for o in bpy.data.objects:
            if hid(o) or o.name.endswith(('-col', '-convcol')): o.hide_render = True; o.hide_viewport = True
        sc = bpy.context.scene; sc.render.engine = 'BLENDER_EEVEE'; sc.render.resolution_x = sc.render.resolution_y = cell
        w = bpy.data.worlds.new("w"); w.color = (.4, .41, .44); sc.world = w
        pts = [o.matrix_world @ Vector(c) for o in bpy.data.objects if o.type == 'MESH' and not o.hide_render and not o.name.endswith(("-col", "-convcol")) for c in o.bound_box]
        mn = Vector((min(p.x for p in pts), min(p.y for p in pts), min(p.z for p in pts))); mx = Vector((max(p.x for p in pts), max(p.y for p in pts), max(p.z for p in pts)))
        ctr = (mn + mx) / 2; size = max((mx - mn).length, .05)
        for loc, e in (((2, -3, 3), 4), ((-3, -1, 2), 1.5), ((0, 3, 2), 2.5)):
            l = bpy.data.lights.new("l", "SUN"); l.energy = e; l.use_shadow = size < 8; o = bpy.data.objects.new("l", l); sc.collection.objects.link(o); o.location = loc
            o.rotation_euler = (Vector((0, 0, 0)) - Vector(loc)).to_track_quat('-Z', 'Y').to_euler()
        c = bpy.data.cameras.new("c"); c.type = 'ORTHO'; c.ortho_scale = size * 1.15; co = bpy.data.objects.new("c", c); sc.collection.objects.link(co); sc.camera = co
        r, e = math.radians(ang), math.radians(elev); d = 10
        co.location = ctr + Vector((math.sin(r) * math.cos(e) * d, -math.cos(r) * math.cos(e) * d, math.sin(e) * d))
        co.rotation_euler = (ctr - co.location).to_track_quat('-Z', 'Y').to_euler()
        sc.render.filepath = "C:/tmp_t/_i.png"; bpy.ops.render.render(write_still=True)
        im = bpy.data.images.load("C:/tmp_t/_i.png", check_existing=False); tiles.append(np.array(im.pixels[:], np.float32).reshape(cell, cell, 4)); bpy.data.images.remove(im)
rows = [np.concatenate(tiles[i:i + 3], 1) for i in range(0, len(tiles), 3)][::-1]
im = bpy.data.images.new("s", cell * 3, cell * len(rows)); im.pixels = np.concatenate(rows, 0).ravel(); im.filepath_raw = out; im.file_format = 'PNG'; im.save()
print("OK", out)
