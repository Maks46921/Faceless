"""Part 1 of build_human_v4.py: reuses the v3 builder text up to the join step (patched), with a sculpted face
(nose, brows, lips, eyes with iris, lids), hat raised for the brim, hidden geometry trimmed."""
import re, math, os
src = open("D:/Faceless/models/src/build_human_v3.py", encoding="utf-8").read()
pre = src[:src.index("# ---- join, scale, export")]

a = pre.index("def head_bm"); b = pre.index("for sx in (-1, 1):\n    bm = bmesh.new(); bmesh.ops.create_uvsphere(bm, u_segments=12")
face_code = '''
M['iris'] = mat("iris", (.07, .11, .13, 1), .4)
M['lips'] = mat("lips", (.2, .11, .10, 1), .6)
FP = globals().get('FP', {})
def fp(k, d=1.0): return FP.get(k, d)
def g2(x, z, sx, sz): return math.exp(-((x / sx) ** 2 + (z / sz) ** 2))
def head_bm(k=1.0, face=False):
    hb = bmesh.new(); bmesh.ops.create_uvsphere(hb, u_segments=36 if face else 32, v_segments=26 if face else 22, radius=.1 * k)
    jaw = fp('jaw'); wid = fp('head_w')
    for v in hb.verts:
        v.co.x *= .85 * wid; v.co.y *= .95; v.co.z *= 1.15
        if v.co.z < 0:
            s = 1 + v.co.z * 1.3; v.co.x *= s; v.co.y *= (1 + v.co.z * .7)
            if v.co.z < -.04: v.co.x *= 1 + (jaw - 1) * min(1.0, (-v.co.z - .04) / .05)
    if face:
        ed = [e for e in hb.edges if (lambda m: m.y > .035 and abs(m.x) < .075 and -.108 < m.z < .075)((e.verts[0].co + e.verts[1].co) / 2)]
        bmesh.ops.subdivide_edges(hb, edges=ed, cuts=1, use_grid_fill=True)
        age = fp('age', 0.0)
        nl, nw, nz = fp('nose'), fp('nose_w'), fp('nose_z', 0.0)
        cb, hol, ch, cw = fp('cheek'), fp('hollow'), fp('chin'), fp('chin_w')
        br, ey_s, ey_z = fp('brow_r'), fp('eye_s'), fp('eye_z', 0.0)
        for v in hb.verts:
            if v.co.y > -.02:
                fw = min(1.0, (v.co.y + .02) / .03); x, z = abs(v.co.x), v.co.z; dy = 0
                dy += nl * .027 * g2(x, z + .004, .0085 * nw, .026)                 # nose bridge ridge
                dy += nl * .022 * g2(x, z + .042 - nz, .0125 * nw, .013)            # nose body/tip
                dy += nl * .010 * g2(x - .0175 * nw, z + .047 - nz, .009 * nw, .009)  # alar wings
                dy -= .005 * g2(x - .0085 * nw, z + .058 - nz, .005, .0045)         # nostrils
                dy -= .0035 * g2(x, z - .008, .011, .008)                           # nasion dip between eyes
                dy += br * .008 * math.exp(-((z - .03) / .009) ** 2) * (1 if x < .05 else math.exp(-((x - .05) / .015) ** 2))  # brow ridge
                dy -= .0075 * g2(x - .034 * fp('eye_sep'), z - .012 - ey_z, .016 * ey_s, .011 * ey_s)  # eye sockets
                dy += cb * .006 * g2(x - .052, z + .014, .014, .018)                # cheekbones
                dy -= hol * .0045 * g2(x - .046, z + .058, .012, .022)              # cheek hollow
                dy -= .0012 * g2(x, z + .069, .03, .0028)                          # mouth groove
                dy += .0035 * g2(x, z + .088, .028, .007)                           # below-lip curve
                dy += ch * .013 * g2(x, z + .098, .018 * cw, .011)                  # chin
                dy -= .002 * g2(x, z + .062, .0035, .006)                           # philtrum
                if age > 0:
                    dy -= age * .0028 * g2(x - .03, z + .045, .007, .03)            # nasolabial fold
                    dy -= age * .0020 * g2(x - .034, z - .002 - ey_z, .02, .005)    # under-eye line
                    dy += age * .0022 * g2(x - .034, z + .001 - ey_z, .02, .006)    # eye bag
                    dy -= age * .0016 * (math.exp(-((z - .062) / .004) ** 2) + math.exp(-((z - .075) / .004) ** 2)) * math.exp(-(x / .05) ** 2)  # forehead lines
                    dy -= age * .0016 * g2(x - .062, z - .008, .006, .012)           # crow's feet
                    dy -= age * .0018 * g2(x - .02, z + .082, .02, .004)             # chin crease
                v.co.y += dy * fw
    return hb
def tag(o, name):
    o.vertex_groups.new(name=name).add(list(range(len(o.data.vertices))), 1.0, 'REPLACE'); return o
M['iris'] = mat("iris", (.07, .11, .13, 1), .4)
M['eyewhite'] = mat("eyewhite", (.66, .64, .6, 1), .35)
_sk = M['skin'].node_tree.nodes["Principled BSDF"].inputs[0].default_value
_lc = FP.get('lip_c') or (min(1, _sk[0] * 1.22 + .02), _sk[1] * .8, _sk[2] * .78)
M['lips'] = mat("lips", (*_lc, 1), .5); M['lips_dark'] = mat("lips_dark", (_lc[0] * .45, _lc[1] * .4, _lc[2] * .4, 1), .6)
head_o = tag(bm_obj("head", head_bm(face=True), M['skin'], (0, .005, 1.66)), 'f_head')
hb = head_bm(1.045)
bmesh.ops.bisect_plane(hb, geom=hb.verts[:] + hb.edges[:] + hb.faces[:], plane_co=(0, 0, .055), plane_no=(0, -.669, .743), clear_inner=True)
bm_obj("hair", hb, M['hair'], (0, .005, 1.66))
def hy(x, z):
    h = head_o.ray_cast(Vector((x, 1.0, z)), Vector((0, -1, 0)))
    return h[1].y if h[0] else .09
EX, EZ, ES = .034 * fp('eye_sep'), .012 + fp('eye_z', 0.0), fp('eye_s')
for sx in (-1, 1):
    ey = hy(sx * EX, EZ)
    bm = bmesh.new(); bmesh.ops.create_uvsphere(bm, u_segments=10, v_segments=6, radius=.0088 * ES)
    for v in bm.verts: v.co.x *= 1.15; v.co.z *= .8
    tag(bm_obj("eye", bm, M['eyewhite'], (sx * EX, ey - .001, 1.66 + EZ)), 'f_eye')
    bm = bmesh.new(); bmesh.ops.create_uvsphere(bm, u_segments=8, v_segments=5, radius=.0058 * ES)
    for v in bm.verts: v.co.y *= .5
    tag(bm_obj("iris", bm, M['iris'], (sx * EX, ey + .0058 * ES, 1.66 + EZ)), 'f_pupil')
    bm = bmesh.new(); bmesh.ops.create_uvsphere(bm, u_segments=8, v_segments=5, radius=.003 * ES)
    for v in bm.verts: v.co.y *= .5
    tag(bm_obj("pupil", bm, M['hair'], (sx * EX, ey + .0078 * ES, 1.66 + EZ)), 'f_pupil')
    bm = bmesh.new(); bmesh.ops.create_uvsphere(bm, u_segments=10, v_segments=6, radius=.0106 * ES)
    for v in bm.verts:
        v.co.x *= 1.2; v.co.y *= .9; v.co.z = (.0087 + fp('lid_heavy', 0.0)) * ES + v.co.z * .04      # open eye: lid collapsed to a thin fin on the upper rim; blink shape key restores the full shell
    tag(bm_obj("lid", bm, M['skin'], (sx * EX, ey - .0005, 1.66 + EZ)), 'f_lid')
    bm = box(.034 * fp('brow_w'), .009, .0085 * fp('brow_t'), .002)
    o = tag(bm_obj("brow", bm, M['hair'], (sx * EX, hy(sx * EX, .037 + fp('brow_z', 0.0)) + .004, 1.66 + .039 + fp('brow_z', 0.0))), 'f_brow'); o.rotation_euler[1] = -sx * (.22 + fp('brow_tilt', 0.0))
# nose is part of the head surface; mouth: thin dark seam between full, skin-tinted lips (no dark band under the nose)
LF, LW = fp('lip_f'), fp('lip_w')
my = hy(0, -.0685)
bm = box(.028 * LW, .002, .0012, .0004); tag(bm_obj("mouth", bm, M['lips_dark'], (0, my - .0004, 1.66 - .0685)), 'f_mouth')
for nm, zc, sx_, sy_, sz_ in (("lip_upper", -.0635, .0225 * LW, .0075 * LF, .0052 * LF), ("lip_lower", -.0735, .02 * LW, .0088 * LF, .0068 * LF)):
    bm = bmesh.new(); bmesh.ops.create_uvsphere(bm, u_segments=10, v_segments=6, radius=1)
    for v in bm.verts: v.co.x *= sx_; v.co.y *= sy_; v.co.z *= sz_
    tag(bm_obj(nm, bm, M['lips'], (0, hy(0, zc) + .0018, 1.66 + zc)), 'f_lipu' if nm == "lip_upper" else 'f_lipl')
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
