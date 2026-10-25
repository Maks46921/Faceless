"""Part 1 of build_human_v4.py: reuses the v3 builder text up to the join step (patched), with a sculpted face
(nose, brows, lips, eyes with iris, lids), hat raised for the brim, hidden geometry trimmed."""
import re, math, os
src = open("D:/Faceless/models/src/build_human_v3.py", encoding="utf-8").read()
pre = src[:src.index("# ---- join, scale, export")]

a = pre.index("def head_bm"); b = pre.index("for sx in (-1, 1):\n    bm = bmesh.new(); bmesh.ops.create_uvsphere(bm, u_segments=12")
face_code = '''
M['iris'] = mat("iris", (.07, .11, .13, 1), .4)
M['lips'] = mat("lips", (.2, .11, .10, 1), .6)
def g2(x, z, sx, sz): return math.exp(-((x / sx) ** 2 + (z / sz) ** 2))
def head_bm(k=1.0, face=False):
    hb = bmesh.new(); bmesh.ops.create_uvsphere(hb, u_segments=40 if face else 32, v_segments=28 if face else 22, radius=.1 * k)
    for v in hb.verts:
        v.co.x *= .85; v.co.y *= .95; v.co.z *= 1.15
        if v.co.z < 0:
            s = 1 + v.co.z * 1.3; v.co.x *= s; v.co.y *= (1 + v.co.z * .7)
    if face:
        ed = [e for e in hb.edges if (lambda m: m.y > .035 and abs(m.x) < .075 and -.108 < m.z < .075)((e.verts[0].co + e.verts[1].co) / 2)]
        bmesh.ops.subdivide_edges(hb, edges=ed, cuts=1, use_grid_fill=True)
        for v in hb.verts:
            if v.co.y > -.02:
                fw = min(1.0, (v.co.y + .02) / .03); x, z = abs(v.co.x), v.co.z; dy = 0
                dy += .027 * g2(x, z + .004, .0085, .026)                 # nose bridge ridge
                dy += .022 * g2(x, z + .042, .0125, .013)                 # nose body/tip
                dy += .010 * g2(x - .0175, z + .047, .009, .009)          # alar wings
                dy -= .005 * g2(x - .0085, z + .058, .005, .0045)         # nostrils
                dy -= .0035 * g2(x, z - .008, .011, .008)                 # nasion dip between eyes
                dy += .008 * math.exp(-((z - .03) / .009) ** 2) * (1 if x < .05 else math.exp(-((x - .05) / .015) ** 2))  # brow ridge
                dy -= .0075 * g2(x - .034, z - .012, .016, .011)          # eye sockets
                dy += .006 * g2(x - .052, z + .014, .014, .018)           # cheekbones
                dy -= .0045 * g2(x - .046, z + .058, .012, .022)          # cheek hollow
                dy -= .0035 * g2(x, z + .069, .032, .0028)                # mouth groove
                dy += .0035 * g2(x, z + .088, .028, .007)                 # below-lip curve
                dy += .013 * g2(x, z + .098, .018, .011)                  # chin
                dy -= .002 * g2(x, z + .062, .0035, .006)                 # philtrum
                v.co.y += dy * fw
    return hb
def tag(o, name):
    o.vertex_groups.new(name=name).add(list(range(len(o.data.vertices))), 1.0, 'REPLACE'); return o
head_o = tag(bm_obj("head", head_bm(face=True), M['skin'], (0, .005, 1.66)), 'f_head')
hb = head_bm(1.045)
bmesh.ops.bisect_plane(hb, geom=hb.verts[:] + hb.edges[:] + hb.faces[:], plane_co=(0, 0, .055), plane_no=(0, -.669, .743), clear_inner=True)
bm_obj("hair", hb, M['hair'], (0, .005, 1.66))
def hy(x, z):
    h = head_o.ray_cast(Vector((x, 1.0, z)), Vector((0, -1, 0)))
    return h[1].y if h[0] else .09
for sx in (-1, 1):
    ey = hy(sx * .034, .012)
    bm = bmesh.new(); bmesh.ops.create_uvsphere(bm, u_segments=14, v_segments=8, radius=.0088)
    for v in bm.verts: v.co.x *= 1.15; v.co.z *= .8
    tag(bm_obj("eye", bm, M['shirt'], (sx * .034, ey - .001, 1.66 + .012)), 'f_eye')
    bm = bmesh.new(); bmesh.ops.create_uvsphere(bm, u_segments=12, v_segments=6, radius=.0058)
    for v in bm.verts: v.co.y *= .5
    tag(bm_obj("iris", bm, M['iris'], (sx * .034, ey + .0058, 1.66 + .012)), 'f_pupil')
    bm = bmesh.new(); bmesh.ops.create_uvsphere(bm, u_segments=8, v_segments=5, radius=.003)
    for v in bm.verts: v.co.y *= .5
    tag(bm_obj("pupil", bm, M['hair'], (sx * .034, ey + .0078, 1.66 + .012)), 'f_pupil')
    bm = bmesh.new(); bmesh.ops.create_uvsphere(bm, u_segments=14, v_segments=8, radius=.0106)
    for v in bm.verts:
        v.co.x *= 1.2; v.co.y *= .9; v.co.z = .0087 + v.co.z * .04      # open eye: lid collapsed to a thin fin on the upper rim; blink shape key restores the full shell
    tag(bm_obj("lid", bm, M['skin'], (sx * .034, ey - .0005, 1.66 + .012)), 'f_lid')
    bm = box(.034, .009, .0085, .002)
    o = tag(bm_obj("brow", bm, M['hair'], (sx * .034, hy(sx * .034, .037) + .004, 1.66 + .039)), 'f_brow'); o.rotation_euler[1] = -sx * .22
# nose is part of the head surface; mouth: dark line + upper/lower lips
my = hy(0, -.067)
bm = box(.044, .004, .0022, .0006); tag(bm_obj("mouth", bm, M['coat_dark'], (0, my + .0005, 1.66 - .067)), 'f_mouth')
for nm, zc, sx_, sy_, sz_ in (("lip_upper", -.0625, .0245, .0062, .0048), ("lip_lower", -.0728, .021, .0068, .006)):
    bm = bmesh.new(); bmesh.ops.create_uvsphere(bm, u_segments=14, v_segments=8, radius=1)
    for v in bm.verts: v.co.x *= sx_; v.co.y *= sy_; v.co.z *= sz_
    tag(bm_obj(nm, bm, M['lips'], (0, hy(0, zc) - .0008, 1.66 + zc)), 'f_lipu' if nm == "lip_upper" else 'f_lipl')
'''
pre = pre[:a] + face_code + pre[b:]
pre = pre.replace("H = (0, .005, 1.705)", "H = (0, .005, 1.74)")
# trim polygons: buttons, ears, hat
pre = pre.replace("bmesh.ops.create_uvsphere(bm, u_segments=14, v_segments=8, radius=.014)", "bmesh.ops.create_uvsphere(bm, u_segments=8, v_segments=5, radius=.014)")
pre = pre.replace("u_segments=12, v_segments=8, radius=.03)", "u_segments=8, v_segments=5, radius=.03)")
# narrower coat skirt
pre = pre.replace("(0, 0, .69, .225, .145), (0, 0, .58, .235, .15), (0, 0, .5, .235, .15)", "(0, 0, .69, .212, .14), (0, 0, .58, .22, .145), (0, 0, .5, .22, .145)")
exec(compile(pre, "v3_prefix", "exec"))

# remove pants geometry hidden under the coat (open top is inside the coat, invisible)
for o in objs:
    if o.name.startswith("pants"):
        bm = bmesh.new(); bm.from_mesh(o.data)
        bmesh.ops.delete(bm, geom=[f for f in bm.faces if f.calc_center_median().z > .66], context='FACES')
        bm.to_mesh(o.data); bm.free()
