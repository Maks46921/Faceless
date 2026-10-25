"""blender -b -P presets_sheets.py -- outdir : full-body and head tiles for every preset glb in models/city/people"""
import bpy, math, sys, glob, os, numpy as np
from mathutils import Vector
out = sys.argv[sys.argv.index("--") + 1]
files = sorted(f for f in glob.glob("D:/Faceless/models/city/people/*.glb") if not f.endswith("_far.glb"))
def tile(f, zc, scale, ang=0, res=(420, 640)):
    bpy.ops.wm.read_factory_settings(use_empty=True); bpy.ops.import_scene.gltf(filepath=f)
    sc = bpy.context.scene; sc.render.engine = 'BLENDER_EEVEE'; sc.render.resolution_x, sc.render.resolution_y = res
    w = bpy.data.worlds.new("w"); w.color = (.4, .41, .44); sc.world = w
    for loc, e in (((2, -3, 3), 4), ((-3, -1, 2), 1.5), ((0, 3, 2), 2.5)):
        l = bpy.data.lights.new("l", "SUN"); l.energy = e; o = bpy.data.objects.new("l", l); sc.collection.objects.link(o); o.location = loc
        o.rotation_euler = (Vector((0, 0, .9)) - Vector(loc)).to_track_quat('-Z', 'Y').to_euler()
    c = bpy.data.cameras.new("c"); c.type = 'ORTHO'; c.ortho_scale = scale; co = bpy.data.objects.new("c", c); sc.collection.objects.link(co); sc.camera = co
    r = math.radians(ang); co.location = (math.sin(r) * 6, -math.cos(r) * 6, zc); co.rotation_euler = (Vector((0, 0, zc)) - co.location).to_track_quat('-Z', 'Y').to_euler()
    sc.render.filepath = "C:/tmp_t/_p.png"; bpy.ops.render.render(write_still=True)
    im = bpy.data.images.load("C:/tmp_t/_p.png", check_existing=False); a = np.array(im.pixels[:], np.float32).reshape(res[1], res[0], 4); bpy.data.images.remove(im); return a
def head_z(f):
    return 1.0
full = []; heads = []
for f in files:
    full.append(tile(f, .98, 2.2))
    # head height from the file's rig: use 0.93 * height; read it from the name table
    hz = {"schoolchild": 1.12, "resident_old_f": 1.45, "resident_old_m": 1.57, "cleaner_f": 1.5, "barista_f": 1.53, "kiosk_seller_f": 1.5, "medic_f": 1.55, "resident_young_f": 1.55}.get(os.path.basename(f)[:-4], 1.66)
    heads.append(tile(f, hz, .5, 20, (420, 420)))
def sheet(tiles, cols, path, h):
    rows = [np.concatenate(tiles[i:i + cols] + [np.zeros_like(tiles[0])] * (cols - len(tiles[i:i + cols])), 1) for i in range(0, len(tiles), cols)][::-1]
    a = np.concatenate(rows, 0); im = bpy.data.images.new("s", a.shape[1], a.shape[0]); im.pixels = a.ravel(); im.filepath_raw = path; im.file_format = 'PNG'; im.save()
sheet(full, 6, f"{out}/presets_lineup.png", 640); sheet(heads, 6, f"{out}/presets_faces.png", 420)
print("OK", [os.path.basename(f) for f in files])
