"""blender -b -P face_sheet.py -- glb out.png : 10 expression morph targets at 1.0, head close-up, grid 5x2.
Reads the morph targets straight from the glb (the Blender glTF importer mixes up per-material targets), so what you see is what Godot gets."""
import bpy, math, sys, json, struct, numpy as np
from mathutils import Vector
glb, out = sys.argv[sys.argv.index("--") + 1:][:2]
d = open(glb, 'rb').read(); jl = struct.unpack('<I', d[12:16])[0]; J = json.loads(d[20:20 + jl]); bin0 = 20 + jl + 8
def raw(bvi, off, ct, count):
    bv = J['bufferViews'][bvi]; return np.frombuffer(d, dtype=ct, count=count, offset=bin0 + bv.get('byteOffset', 0) + off)
def acc(i):
    a = J['accessors'][i]; n = {'SCALAR': 1, 'VEC3': 3, 'VEC2': 2, 'VEC4': 4}[a['type']]
    ct = {5126: 'f4', 5123: 'u2', 5125: 'u4', 5121: 'u1'}[a['componentType']]
    if 'bufferView' in a: arr = raw(a['bufferView'], a.get('byteOffset', 0), ct, a['count'] * n).reshape(a['count'], n).copy()
    else: arr = np.zeros((a['count'], n), np.float32)
    if 'sparse' in a:
        sp = a['sparse']; k = sp['count']; ix = sp['indices']; vl = sp['values']
        ict = {5123: 'u2', 5125: 'u4', 5121: 'u1'}[ix['componentType']]
        idx = raw(ix['bufferView'], ix.get('byteOffset', 0), ict, k).astype(int); val = raw(vl['bufferView'], vl.get('byteOffset', 0), ct, k * n).reshape(k, n)
        arr[idx] = val
    return arr
mesh = [m for m in J['meshes'] if 'targetNames' in m.get('extras', {})][0]; names = mesh['extras']['targetNames']
mats = [mm['name'] for mm in J['materials']]
sc = bpy.context.scene
bpy.ops.wm.read_factory_settings(use_empty=True); sc = bpy.context.scene; sc.render.engine = 'BLENDER_EEVEE'; W = 400; sc.render.resolution_x = sc.render.resolution_y = W
w = bpy.data.worlds.new("w2"); w.color = (.4, .41, .44); sc.world = w
bm_ = {}
for n, col in (("skin", (.32, .27, .23)), ("hair", (.01, .01, .01)), ("coat_dark", (.02, .02, .025)), ("shirt", (.55, .53, .5)), ("iris", (.07, .11, .13)), ("lips", (.2, .11, .1))):
    m = bpy.data.materials.new(n); m.diffuse_color = (*col, 1); m.use_nodes = True; m.node_tree.nodes["Principled BSDF"].inputs[0].default_value = (*col, 1); bm_[n] = m
for loc, e in (((0, -3, 3), 5), ((-3, -1, 2), 1.5)):
    l = bpy.data.lights.new("l", "SUN"); l.energy = e; l.use_shadow = False; o = bpy.data.objects.new("l", l); sc.collection.objects.link(o); o.location = loc
    o.rotation_euler = (Vector((0, 0, 1.6)) - Vector(loc)).to_track_quat('-Z', 'Y').to_euler()
c = bpy.data.cameras.new("c"); c.type = 'ORTHO'; c.ortho_scale = .30; co = bpy.data.objects.new("c", c); sc.camera = co; sc.collection.objects.link(co)
co.location = (0, -3, 1.605); co.rotation_euler = (math.pi / 2, 0, 0)
prims = []
for p in mesh['primitives']:
    pos = acc(p['attributes']['POSITION']).astype(np.float64); idx = acc(p['indices']).reshape(-1, 3).astype(int)
    tg = [acc(t['POSITION']).astype(np.float64) for t in p['targets']]
    prims.append((mats[p['material']], pos, idx, tg))
def conv(a): return [(x, -z, y) for x, y, z in a]     # glTF Y-up -> Blender Z-up
tiles = []
for ti, n in enumerate(names):
    objs = []
    for mname, pos, idx, tg in prims:
        v = pos + tg[ti]; me = bpy.data.meshes.new("t"); vv = conv(v)
        keep = [tuple(f) for f in idx if min(vv[i][2] for i in f) < 1.665]       # drop the hat
        me.from_pydata(vv, [], keep)
        me.materials.append(bm_.get(mname) or bm_["skin"]) if mname in bm_ else me.materials.append(bpy.data.materials.new(mname))
        for pl in me.polygons: pl.use_smooth = True
        o = bpy.data.objects.new("t", me); sc.collection.objects.link(o); objs.append(o)
    sc.render.filepath = "C:/tmp_t/_s.png"; bpy.ops.render.render(write_still=True)
    im = bpy.data.images.load("C:/tmp_t/_s.png", check_existing=False); tiles.append(np.array(im.pixels[:], np.float32).reshape(W, W, 4)); bpy.data.images.remove(im)
    for o in objs: bpy.data.objects.remove(o)
sheet = np.concatenate([np.concatenate(tiles[5:10], 1), np.concatenate(tiles[:5], 1)], 0)   # image origin is bottom-left: first 5 tiles end up on the top row
im = bpy.data.images.new("s", W * 5, W * 2); im.pixels = sheet.ravel(); im.filepath_raw = out; im.file_format = 'PNG'; im.save()
print("SHEET", names)
