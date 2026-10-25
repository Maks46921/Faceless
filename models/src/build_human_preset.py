"""Parametric human presets on the shared 40-bone rig (same skeleton and 25 animations as human_noir_v4).
Run: PRESET=<name> LOD=near|far D:\\Cosmoteer\\blender.exe -b -P build_human_preset.py   -> models/city/people/<name>[_far].glb
Presets are defined in PRESETS below (colour, outfit, headwear, hair, build, height, accessories)."""
import os, json, math, re
_v3 = open("D:/Faceless/models/src/build_human_v3.py", encoding="utf-8").read()
exec(compile(_v3[:_v3.index("# ---- legs / shoes")], "v3_helpers", "exec"))
_head = open("D:/Faceless/models/src/build_human_v4_head.py", encoding="utf-8").read()
FACE_CODE = _head[_head.index("face_code = '''") + len("face_code = '''"):_head.index("'''\npre = pre[:a]")]

def col(m, rgb, rough=None, metal=None):
    b = m.node_tree.nodes["Principled BSDF"]; b.inputs[0].default_value = (*rgb, 1)
    if rough is not None: b.inputs['Roughness'].default_value = rough
    if metal is not None: b.inputs['Metallic'].default_value = metal

OUTFITS = {
 'coat':       dict(hem=.58, thick=1.0, lapels=1, collar=1, tie=1, belt=1, buttons=2, pockets=1, cuffs=1, shirt=1),
 'jacket':     dict(hem=.72, thick=1.0, collar=1, pockets=1, zip=1, cuffs=1),
 'hoodie':     dict(hem=.74, thick=1.06, hood=1, pocket_front=1, drawstring=1),
 'leather':    dict(hem=.76, thick=1.04, lapels=1, collar=1, belt=1, zip=1, shine=1, cuffs=1),
 'puffer':     dict(hem=.72, thick=1.32, quilt=1, collar_high=1, zip=1),
 'track':      dict(hem=.74, thick=1.0, stripes=1, zip=1, collar=1),
 'sweater':    dict(hem=.74, thick=1.05, roll_neck=1, hem_band=1),
 'long_cardigan': dict(hem=.58, thick=1.05, roll_neck=0, collar=1, buttons=3, hem_band=1, pockets=1),
 'work':       dict(hem=.70, thick=1.06, pockets_chest=1, belt=1, buttons=3, collar=1, cuffs=1),
 'uniform':    dict(hem=.70, thick=1.0, epaulets=1, buttons=4, belt=1, strap=1, collar=1, pockets_chest=1, tie=1, cuffs=1),
 'suit':       dict(hem=.66, thick=1.0, lapels=1, tie=1, shirt=1, buttons=2, pockets=1, cuffs=1),
 'white_coat': dict(hem=.52, thick=1.03, collar=1, buttons=4, pockets_chest=1, shirt=1),
}
# colour tuples are linear-ish RGB (muted noir palette, as the rest of the game)
PRESETS = {
 "militia_patrol": dict(outfit='uniform', hat='peaked', hair='short', height=1.84, build=1.06, skin=(.33, .26, .21), hair_c=(.03, .025, .02), top=(.09, .13, .17), trim=(.03, .04, .06), pants=(.05, .07, .1), shoes=(.01, .01, .012), hat_c=(.07, .1, .14), iris=(.1, .15, .2), acc=['radio_pouch']),
 "militia_inspector": dict(outfit='coat', hat='flat_cap', hair='short', height=1.78, build=1.0, skin=(.32, .26, .22), hair_c=(.2, .19, .18), top=(.1, .08, .06), trim=(.04, .03, .025), pants=(.05, .045, .04), shoes=(.015, .01, .008), hat_c=(.08, .07, .06), shirt=(.45, .44, .4), iris=(.12, .1, .06), acc=['briefcase_hint']),
 "guard_black": dict(outfit='jacket', hat='flat_cap', hair='short', height=1.86, build=1.14, skin=(.3, .24, .2), hair_c=(.02, .02, .02), top=(.02, .02, .025), trim=(.01, .01, .012), pants=(.015, .015, .02), shoes=(.005, .005, .006), hat_c=(.015, .015, .018), iris=(.05, .06, .07), acc=['radio_pouch', 'sunglasses']),
 "electrician": dict(outfit='work', hat='hardhat', hair='short', height=1.76, build=1.04, skin=(.31, .25, .2), hair_c=(.08, .05, .03), top=(.08, .12, .16), trim=(.04, .06, .08), pants=(.07, .1, .13), shoes=(.025, .02, .015), hat_c=(.62, .42, .03), iris=(.14, .1, .06), acc=['tool_belt']),
 "courier": dict(outfit='hoodie', hat='beanie', hair='short', height=1.74, build=.96, skin=(.34, .27, .22), hair_c=(.1, .06, .03), top=(.14, .15, .08), trim=(.08, .09, .05), pants=(.03, .03, .04), shoes=(.1, .1, .1), hat_c=(.03, .03, .035), iris=(.08, .12, .1), acc=['backpack']),
 "barista_f": dict(outfit='sweater', hat='none', hair='bun', gender='f', height=1.66, build=.9, skin=(.36, .29, .24), hair_c=(.07, .04, .025), top=(.2, .12, .09), trim=(.12, .07, .05), pants=(.02, .02, .025), shoes=(.02, .015, .012), hat_c=(.05, .05, .05), iris=(.1, .08, .05), acc=['apron']),
 "medic_f": dict(outfit='white_coat', hat='beret', hair='bun', gender='f', height=1.68, build=.92, skin=(.35, .28, .23), hair_c=(.18, .1, .05), top=(.62, .62, .6), trim=(.5, .5, .48), pants=(.55, .55, .53), shoes=(.55, .55, .53), hat_c=(.55, .55, .53), shirt=(.35, .45, .5), iris=(.08, .14, .16), acc=['stethoscope', 'red_cross']),
 "medic_m": dict(outfit='white_coat', hat='none', hair='short', height=1.82, build=1.04, skin=(.33, .26, .21), hair_c=(.03, .025, .02), top=(.62, .62, .6), trim=(.5, .5, .48), pants=(.3, .4, .5), shoes=(.4, .4, .4), hat_c=(.55, .55, .53), shirt=(.3, .4, .45), iris=(.1, .08, .06), acc=['stethoscope', 'red_cross']),
 "resident_old_m": dict(outfit='jacket', hat='flat_cap', hair='short', height=1.7, build=1.0, skin=(.38, .3, .25), hair_c=(.4, .4, .4), top=(.12, .09, .06), trim=(.06, .045, .03), pants=(.06, .055, .05), shoes=(.02, .015, .01), hat_c=(.1, .09, .08), iris=(.1, .12, .14), acc=[]),
 "resident_old_f": dict(outfit='long_cardigan', hat='headscarf', hair='short', gender='f', height=1.58, build=1.05, skin=(.4, .32, .27), hair_c=(.45, .45, .45), top=(.12, .1, .12), trim=(.07, .06, .07), pants=(.04, .035, .04), shoes=(.02, .015, .012), hat_c=(.14, .05, .05), iris=(.1, .13, .15), acc=[]),
 "resident_young_f": dict(outfit='puffer', hat='beret', hair='long', gender='f', height=1.68, build=.92, skin=(.36, .29, .24), hair_c=(.1, .06, .03), top=(.05, .1, .14), trim=(.03, .06, .09), pants=(.03, .03, .04), shoes=(.06, .06, .06), hat_c=(.3, .08, .08), iris=(.08, .11, .09), acc=[]),
 "resident_man": dict(outfit='leather', hat='none', hair='short', height=1.79, build=1.02, skin=(.33, .27, .22), hair_c=(.06, .04, .03), top=(.035, .03, .03), trim=(.015, .012, .012), pants=(.04, .05, .07), shoes=(.015, .012, .01), hat_c=(.05, .05, .05), iris=(.1, .08, .05), acc=[]),
 "bodyguard": dict(outfit='suit', hat='none', hair='short', height=1.92, build=1.2, skin=(.3, .24, .2), hair_c=(.015, .015, .015), top=(.012, .012, .015), trim=(.006, .006, .008), pants=(.012, .012, .015), shoes=(.004, .004, .005), hat_c=(.01, .01, .01), shirt=(.5, .5, .5), iris=(.04, .05, .06), acc=['sunglasses']),
 "janitor": dict(outfit='puffer', hat='beanie', hair='short', height=1.72, build=1.1, skin=(.34, .27, .22), hair_c=(.2, .2, .2), top=(.1, .13, .08), trim=(.05, .07, .04), pants=(.05, .06, .09), shoes=(.025, .02, .015), hat_c=(.15, .06, .03), iris=(.1, .11, .07), acc=[]),
 "cleaner_f": dict(outfit='work', hat='headscarf', hair='short', gender='f', height=1.62, build=1.05, skin=(.37, .3, .25), hair_c=(.2, .15, .1), top=(.1, .17, .22), trim=(.05, .09, .12), pants=(.08, .13, .17), shoes=(.04, .04, .04), hat_c=(.12, .2, .26), iris=(.08, .1, .1), acc=['apron']),
 "kiosk_seller_f": dict(outfit='puffer', hat='beanie', hair='long', gender='f', height=1.64, build=1.0, skin=(.37, .3, .25), hair_c=(.12, .07, .04), top=(.2, .1, .08), trim=(.1, .05, .04), pants=(.02, .02, .03), shoes=(.02, .02, .02), hat_c=(.2, .2, .22), iris=(.1, .09, .06), acc=[]),
 "schoolchild": dict(outfit='hoodie', hat='none', hair='short', height=1.3, build=.8, head_scale=1.22, skin=(.36, .29, .24), hair_c=(.12, .08, .05), top=(.12, .06, .06), trim=(.07, .035, .035), pants=(.04, .05, .08), shoes=(.1, .1, .1), hat_c=(.05, .05, .05), iris=(.08, .1, .12), acc=['backpack']),
}

def dec(o, ratio):
    sel(o); m_ = o.modifiers.new('d', 'DECIMATE'); m_.ratio = ratio; bpy.ops.object.modifier_apply(modifier='d'); return o
PN = os.environ.get("PRESET", "militia_patrol"); PR = PRESETS[PN]; LOD = os.environ.get("LOD", "near"); FAR = LOD == "far"
OF = dict(hem=.8, thick=1.0); OF.update(OUTFITS[PR['outfit']])
FEM = PR.get('gender') == 'f'; BUILD = PR.get('build', 1.0) * (.92 if FEM else 1.0); HEADS = PR.get('head_scale', 1.0)
SUB = 1 if FAR else 2

# ---- materials
col(M['coat'], PR['top'], .9 if not OF.get('shine') else .35); col(M['coat_dark'], PR['trim']); col(M['pants'], PR['pants']); col(M['shoes'], PR['shoes'])
col(M['skin'], PR['skin']); col(M['hair'], PR['hair_c']); col(M['shirt'], PR.get('shirt', (.5, .5, .48)))
HAT = mat("headwear", (*PR['hat_c'], 1), .85); col(HAT, PR['hat_c'])
STRIPE = mat("stripe_white", (.5, .5, .5, 1), .8)

# ---- legs
cuffs = not FAR
chain("pants", [(0, 0, .9, .105 * BUILD, .085), (-.082, 0, .8, .088 * BUILD, .083), (-.095, 0, .5, .075, .07), (-.1, 0, .025, .058, .055),
                (.082, 0, .8, .088 * BUILD, .083), (.095, 0, .5, .075, .07), (.1, 0, .025, .058, .055)],
      [(0, 1), (1, 2), (2, 3), (0, 4), (4, 5), (5, 6)], M['pants'], SUB)
dec(objs[-1], .55 if not FAR else .8)
chain("shoes", [(-.1, -.02, .07, .05, .055), (-.1, .06, .05, .052, .045), (-.1, .15, .038, .046, .034), (.1, -.02, .07, .05, .055), (.1, .06, .05, .052, .045), (.1, .15, .038, .046, .034)],
      [(0, 1), (1, 2), (3, 4), (4, 5)], M['shoes'], 1 if FAR else 2)
dec(objs[-1], .6 if not FAR else .9)
for sx in (-1, 1):
    bm_obj("sole", box(.11, .26, .02, .006), M['coat_dark'], (sx * .1, .045, .012))
    if not FAR: bm_obj("heel", box(.07, .06, .03, .006), M['coat_dark'], (sx * .1, -.055, .03))
    if cuffs and PR['outfit'] in ('coat', 'suit', 'uniform', 'work'): bm_obj("trouser_cuff", lathe([(.066, -.016), (.07, -.014), (.07, .014), (.066, .016)], 14), M['pants'], (sx * .1, 0, .08))
if OF.get('stripes') and not FAR:
    for sx in (-1, 1): bm_obj("pants_stripe", box(.012, .09, .78, .002), STRIPE, (sx * .185, 0, .5))

# ---- upper garment (truncated skin chain, clipped at the hem)
T_ = OF['thick']; hem = OF['hem']
lower = [(1.18, .2, .135), (1.0, .19, .13), (.9, .2, .135), (.8, .21, .14), (.69, .212, .14), (.58, .22, .145), (.5, .22, .145)]
lp = [p for p in lower if p[0] > hem + .05]
lp.append((hem + .02, lp[-1][1] if lp else .2, lp[-1][2] if lp else .135))
pts = [(0, 0, z, rx * T_ * BUILD, ry * T_) for z, rx, ry in lp]
n = len(pts)
sl_r = (.06 * T_, .052 * T_)
sh = .0 if not FEM else -.02
pts += [(0, 0, 1.38, .2 * T_ * BUILD, .12 * T_), (0, 0, 1.5, .09 * (1.2 if OF.get('collar_high') else 1.0), .09), (-.2 * (1 - .03 * (BUILD < 1)), 0, 1.44, .07 * T_, .07 * T_), (-.31, 0, 1.2, sl_r[0], sl_r[0]), (-.365, .04, .95, sl_r[1], sl_r[1]),
        (.2 * (1 - .03 * (BUILD < 1)), 0, 1.44, .07 * T_, .07 * T_), (.31, 0, 1.2, sl_r[0], sl_r[0]), (.365, .04, .95, sl_r[1], sl_r[1])]
ed = [(i, i + 1) for i in range(n - 1)]
ed += [(0, n), (n, n + 1), (n, n + 2), (n + 2, n + 3), (n + 3, n + 4), (n, n + 5), (n + 5, n + 6), (n + 6, n + 7)]
chain("coat", pts, ed, M['coat'], SUB, hem)
coat_o = objs[-1]
dec(coat_o, .72 if not FAR else .9)
def fy(x, z, off=.008):
    h = coat_o.ray_cast(Vector((x, 1.0, z)), Vector((0, -1, 0)))
    return (h[1].y if h[0] else .1) + off

if not FAR:
    if OF.get('lapels'):
        for sx in (-1, 1):
            Pp = [(.02, 1.47), (.1, 1.46), (.135, 1.37), (.1, 1.33), (.075, 1.18), (.022, 1.2)]
            vs = [(sx * x, fy(sx * x * .4, z, .022), z) for x, z in Pp]
            shell("lapel", vs, [(0, 1, 2, 3, 4, 5)] if sx > 0 else [(5, 4, 3, 2, 1, 0)], M['coat_dark'], .012, 1)
    if OF.get('collar') or OF.get('roll_neck') or OF.get('collar_high'):
        h_ = 1.56 if (OF.get('roll_neck') or OF.get('collar_high')) else 1.53
        w_ = .082 if OF.get('roll_neck') else .072
        bm = lathe([(w_, 1.465), (w_ + .01, 1.5), (w_ - .002, h_), (w_ - .012, h_ - .01), (w_ - .006, 1.5), (w_ - .012, 1.47)], 20)
        for v in bm.verts: v.co.y += .004
        bm_obj("collar", bm, M['coat'] if (OF.get('roll_neck') or OF.get('collar_high')) else M['coat_dark'])
    if OF.get('shirt') or PR['outfit'] in ('coat', 'suit', 'uniform', 'work', 'white_coat'):
        bm_obj("shirt_collar", lathe([(.054, 1.47), (.066, 1.515), (.064, 1.545), (.056, 1.54), (.054, 1.5)], 20), M['shirt'])
        if OF.get('shirt'): chain("shirt", [(0, fy(0, 1.46, -.012), 1.46, .07, .014), (0, fy(0, 1.3, -.01), 1.3, .045, .012)], [(0, 1)], M['shirt'], 1)
    if OF.get('tie'):
        chain("tie", [(0, fy(0, 1.42, .014), 1.42, .016, .01), (0, fy(0, 1.2, .022), 1.2, .026, .012)], [(0, 1)], M['gold'] if PR['outfit'] == 'coat' else M['coat_dark'], 1)
        bm = bmesh.new(); bmesh.ops.create_uvsphere(bm, u_segments=10, v_segments=6, radius=.02)
        for v in bm.verts: v.co.z *= .8
        bm_obj("knot", bm, M['gold'] if PR['outfit'] == 'coat' else M['coat_dark'], (0, fy(0, 1.445, .012), 1.445))
    if OF.get('belt') and hem < .95:
        bm = bmesh.new(); bmesh.ops.create_cone(bm, cap_ends=False, segments=26, radius1=1, radius2=1, depth=.045)
        for v in bm.verts: v.co.x *= .186 * BUILD * T_; v.co.y *= .128 * T_
        bo = bm_obj("belt", bm, M['coat_dark'], (0, 0, .99)); sel(bo); bo.modifiers.new("s", "SOLIDIFY").thickness = .012; bpy.ops.object.modifier_apply(modifier="s")
        bm_obj("buckle", box(.035, .01, .035, .003), M['gold'], (0, fy(0, .99, .02), .99))
    for k in range(OF.get('buttons', 0)):
        z = 1.1 - k * .14
        if z < hem + .05: continue
        bm = bmesh.new(); bmesh.ops.create_uvsphere(bm, u_segments=8, v_segments=5, radius=.013)
        bm_obj("button", bm, M['gold'] if PR['outfit'] in ('coat', 'uniform', 'suit') else M['coat_dark'], (.03, fy(.03, z, .008), z))
    if OF.get('pockets'):
        for sx in (-1, 1):
            o = bm_obj("pocket", box(.075, .012, .03, .004), M['coat_dark'], (sx * .115, fy(sx * .115, max(hem + .06, .78), .01), max(hem + .06, .78))); o.rotation_euler[1] = sx * .12
    if OF.get('pockets_chest'):
        for sx in (-1, 1): bm_obj("chest_pocket", box(.055, .01, .05, .003), M['coat_dark'], (sx * .085, fy(sx * .085, 1.22, .01), 1.22))
    if OF.get('zip'):
        bm_obj("zip", box(.01, .008, .6, .0015), M['coat_dark'], (0, fy(0, 1.0, .006), 1.04))
    if OF.get('stripes'):
        for sx in (-1, 1):
            o = bm_obj("sleeve_stripe", box(.01, .09, .38, .002), STRIPE, (sx * .34, .0, 1.2)); o.rotation_euler[1] = sx * .22
    if OF.get('pocket_front'):
        bm_obj("kangaroo_pocket", box(.22, .018, .1, .006), M['coat_dark'], (0, fy(0, .98, .008), .98))
    if OF.get('drawstring'):
        for sx in (-1, 1): bm_obj("drawstring", box(.006, .006, .09, .001), M['shirt'], (sx * .03, fy(sx * .03, 1.38, .02), 1.38))
    if OF.get('hood'):
        bm = bmesh.new(); bmesh.ops.create_uvsphere(bm, u_segments=14, v_segments=8, radius=.12)
        for v in bm.verts: v.co.x *= 1.05; v.co.y *= .85; v.co.z *= .75
        bm_obj("hood", bm, M['coat'], (0, -.07, 1.5))
    if OF.get('quilt'):
        for z in (1.28, 1.14, 1.0, .88): bm_obj("quilt", lathe([(.0, z - .01), (.2 * BUILD * T_ * .8, z - .01), (.208 * BUILD * T_ * .8, z), (.2 * BUILD * T_ * .8, z + .01)], 20), M['coat_dark'], (0, 0, 0)).scale = (1, .66, 1)
    if OF.get('hem_band') or OF.get('puffer'):
        bm_obj("hem_band", lathe([(.1, -.012), (.1, .012)], 4), M['coat_dark'], (0, 0, hem)) if False else None
    if OF.get('epaulets'):
        for sx in (-1, 1): o = bm_obj("epaulet", box(.1, .04, .01, .002), M['gold'], (sx * .17, 0, 1.5)); o.rotation_euler[1] = sx * .22
    if OF.get('strap'):
        o = bm_obj("cross_strap", box(.04, .01, .5, .002), M['coat_dark'], (0, fy(0, 1.2, .012), 1.2)); o.rotation_euler[1] = .5
    if OF.get('cuffs'):
        for sx in (-1, 1):
            o = bm_obj("sleeve_cuff", lathe([(.06 * T_, -.014), (.064 * T_, -.012), (.064 * T_, .014), (.06 * T_, .016)], 14), M['coat_dark'], (sx * .357, .043, .965)); o.rotation_euler[1] = sx * .2

# ---- hands + neck (mitten in the far LOD)
pts2 = []; ed2 = []
def add(p): pts2.append(p); return len(pts2) - 1
for sx in (-1, 1):
    hx = sx * .372
    a = add((hx, .048, .975, .036, .026)); b = add((hx, .058, .865, .038, .024)); ed2.append((a, b))
    if FAR:
        c_ = add((hx, .06, .79, .028, .02)); ed2.append((b, c_)); t0 = add((hx + sx * .01, .095, .9, .014, .014)); ed2.append((a, t0))
    else:
        for i, yy in enumerate((.026, .05, .074, .096)):
            L_ = (.075, .082, .078, .064)[i]
            f0 = add((hx, yy, .855, .0105, .0105)); f1 = add((hx, yy + .006, .855 - L_ * .5, .0098, .0098)); f2 = add((hx, yy + .012, .855 - L_, .0085, .0085))
            ed2 += [(b, f0), (f0, f1), (f1, f2)]
        t0 = add((hx + sx * .01, .095, .9, .012, .012)); t1 = add((hx + sx * .012, .112, .855, .0105, .0105)); ed2 += [(a, t0), (t0, t1)]
n0 = add((0, 0, 1.44, .05, .05)); n1 = add((0, 0, 1.6, .046, .05)); ed2.append((n0, n1))
chain("skin", pts2, ed2, M['skin'], 1)
dec(objs[-1], .72 if not FAR else .9)

# ---- face (shared sculpt) / far head
head_start = len(objs)
if not FAR:
    exec(FACE_CODE)
    col(M['iris'], PR['iris'], .4)
else:
    hb = bmesh.new(); bmesh.ops.create_uvsphere(hb, u_segments=16, v_segments=10, radius=.1)
    for v in hb.verts:
        v.co.x *= .85; v.co.y *= .95; v.co.z *= 1.15
        if v.co.z < 0: s_ = 1 + v.co.z * 1.3; v.co.x *= s_; v.co.y *= (1 + v.co.z * .7)
        if v.co.y > .03 and abs(v.co.x) < .018 and -.06 < v.co.z < .02: v.co.y += .014         # nose ridge
    head_far = bm_obj("head", hb, M['skin'], (0, .005, 1.66))
    head_far.vertex_groups.new(name="f_head").add(list(range(len(head_far.data.vertices))), 1.0, 'REPLACE')
    M['iris'] = mat("iris", (*PR['iris'], 1), .4)
    for sx in (-1, 1):
        bm = bmesh.new(); bmesh.ops.create_uvsphere(bm, u_segments=6, v_segments=4, radius=.0065)
        for v in bm.verts: v.co.y *= .5
        bm_obj("eye_dot", bm, M['iris'], (sx * .034, .0925, 1.672))
    hb2 = bmesh.new(); bmesh.ops.create_uvsphere(hb2, u_segments=16, v_segments=10, radius=.1045)
    for v in hb2.verts:
        v.co.x *= .85; v.co.y *= .95; v.co.z *= 1.15
        if v.co.z < 0: s_ = 1 + v.co.z * 1.3; v.co.x *= s_; v.co.y *= (1 + v.co.z * .7)
    bmesh.ops.bisect_plane(hb2, geom=hb2.verts[:] + hb2.edges[:] + hb2.faces[:], plane_co=(0, 0, .055), plane_no=(0, -.669, .743), clear_inner=True)
    bm_obj("hair", hb2, M['hair'], (0, .005, 1.66))
    for sx in (-1, 1):
        bm = bmesh.new(); bmesh.ops.create_uvsphere(bm, u_segments=6, v_segments=4, radius=.03)
        for v in bm.verts: v.co.x *= .3; v.co.y *= .7
        bm_obj("ear", bm, M['skin'], (sx * .083, 0, 1.655))
col(M['hair'], PR['hair_c'])
head_objs = [o for o in objs[head_start:]]
# hair styles (face code creates the 'short' shell)
def remove_obj(name):
    for o in list(objs):
        if o.name.split('.')[0] == name: objs.remove(o); bpy.data.objects.remove(o, do_unlink=True)
style = PR.get('hair', 'short')
if style == 'bald': remove_obj('hair')
elif style in ('long', 'bun'):
    if style == 'long':
        hb = bmesh.new(); bmesh.ops.create_uvsphere(hb, u_segments=20, v_segments=14, radius=.108)
        for v in hb.verts:
            v.co.x *= .9; v.co.y *= 1.0; v.co.z *= 1.2
            if v.co.z < 0: v.co.x *= (1 - v.co.z * .45); v.co.y *= (1 - v.co.z * .35)
        bmesh.ops.bisect_plane(hb, geom=hb.verts[:] + hb.edges[:] + hb.faces[:], plane_co=(0, 0, -.16), plane_no=(0, 0, 1), clear_inner=True)
        bmesh.ops.bisect_plane(hb, geom=hb.verts[:] + hb.edges[:] + hb.faces[:], plane_co=(0, .035, 0), plane_no=(0, -1, 0), clear_inner=True)
        bm_obj("hair_long", hb, M['hair'], (0, .005, 1.66))
    else:
        bm = bmesh.new(); bmesh.ops.create_uvsphere(bm, u_segments=10, v_segments=6, radius=.05)
        bm_obj("bun", bm, M['hair'], (0, -.085, 1.74))
if FEM:
    pass

# ---- headwear
HZ = 1.74
def hw(name, bm, loc=(0, .005, HZ), rot=(0, 0, 0), mt=None):
    o = bm_obj(name, bm, mt or HAT, loc); o.rotation_euler = rot; return o
ht = PR.get('hat', 'none')
if ht == 'fedora':
    prof = [(0, .118), (.03, .117), (.055, .113), (.075, .104), (.089, .09), (.097, .07), (.101, .045), (.103, .02), (.105, -.005), (.12, -.012), (.17, -.008), (.215, .004), (.228, .018), (.226, .012), (.2, -.006), (.15, -.022), (.106, -.022)]
    hw("hat", lathe(prof, 28))
elif ht == 'flat_cap':
    hw("cap", lathe([(0, .07), (.06, .068), (.1, .05), (.118, .015), (.116, -.01), (.108, -.02), (.0, -.02)], 20), loc=(0, .01, 1.715))
    hw("cap_visor", box(.15, .09, .008, .003), loc=(0, .125, 1.705), rot=(.28, 0, 0))
elif ht == 'beanie':
    hw("beanie", lathe([(0, .105), (.06, .098), (.1, .065), (.112, .02), (.116, -.02), (.108, -.035), (.118, -.04), (.12, -.07), (.0, -.07)], 20), loc=(0, .005, 1.72))
elif ht == 'peaked':
    hw("cap_crown", lathe([(0, .085), (.1, .085), (.15, .06), (.14, .02), (.116, .0), (.112, -.04), (.118, -.045), (.118, -.07), (.0, -.07)], 24), loc=(0, .005, 1.74))
    hw("cap_visor", box(.16, .1, .007, .003), loc=(0, .13, 1.69), rot=(.22, 0, 0), mt=M['shoes'])
    hw("cap_badge", cyl_bm := lathe([(0, 0), (.015, 0), (.015, .004), (0, .004)], 10), loc=(0, .124, 1.74), rot=(math.pi / 2, 0, 0), mt=M['gold'])
elif ht == 'hardhat':
    hw("hardhat", lathe([(0, .12), (.06, .114), (.108, .08), (.125, .03), (.13, -.005), (.16, -.012), (.16, -.02), (.125, -.02), (.0, -.02)], 24), loc=(0, .005, 1.72))
    hw("hardhat_ridge", box(.02, .22, .014, .004), loc=(0, .005, 1.84))
elif ht == 'beret':
    hw("beret", lathe([(0, .045), (.09, .05), (.145, .022), (.15, -.0), (.12, -.018), (.105, -.03), (.0, -.03)], 20), loc=(.025, .0, 1.735), rot=(.08, 0, .2))
elif ht == 'headscarf':
    hb = bmesh.new(); bmesh.ops.create_uvsphere(hb, u_segments=22, v_segments=14, radius=.11)
    for v in hb.verts:
        v.co.x *= .93; v.co.y *= 1.03; v.co.z *= 1.17
        if v.co.z < 0: s_ = 1 + v.co.z * 1.1; v.co.x *= s_; v.co.y *= (1 + v.co.z * .6)
    bmesh.ops.bisect_plane(hb, geom=hb.verts[:] + hb.edges[:] + hb.faces[:], plane_co=(0, 0, .02), plane_no=(0, -.9, .44), clear_inner=True)
    bmesh.ops.bisect_plane(hb, geom=hb.verts[:] + hb.edges[:] + hb.faces[:], plane_co=(0, 0, -.1), plane_no=(0, 0, 1), clear_inner=True)
    remove_obj('hair'); hw("headscarf", hb, loc=(0, .005, 1.66))
    bm = bmesh.new(); bmesh.ops.create_uvsphere(bm, u_segments=8, v_segments=5, radius=.035)
    hw("scarf_knot", bm, loc=(0, -.105, 1.62))
if ht == 'peaked' or ht == 'hardhat' or ht == 'beanie':
    pass

# ---- accessories
acc = PR.get('acc', [])
if not FAR:
    if 'backpack' in acc:
        bm_obj("backpack", box(.3, .12, .36, .02), HAT, (0, -.16, 1.2))
        for sx in (-1, 1): bm_obj("backpack_strap", box(.04, .02, .4, .004), M['coat_dark'], (sx * .12, .01, 1.28)).rotation_euler[0] = .05
    if 'apron' in acc: bm_obj("apron", box(.28, .02, .5, .006), mat("apron", (.12, .12, .1, 1), .8) if 'apron' not in bpy.data.materials else bpy.data.materials['apron'], (0, fy(0, .95, .01), .96))
    if 'sunglasses' in acc:
        for sx in (-1, 1): bm_obj("lens", box(.04, .008, .026, .004), M['shoes'], (sx * .034, .1, 1.672))
        bm_obj("glasses_bridge", box(.02, .008, .006, .001), M['shoes'], (0, .1, 1.676))
    if 'stethoscope' in acc:
        bm_obj("stethoscope", lathe([(.07, -.006), (.085, -.006), (.085, .006), (.07, .006)], 14), M['shoes'], (0, 0, 1.42)).scale = (1, 1, 1)
        bm_obj("stetho_bell", lathe([(0, 0), (.014, 0), (.014, .005), (0, .005)], 8), M['gold'], (.04, fy(.04, 1.15, .012), 1.15)).rotation_euler[0] = math.pi / 2
    if 'red_cross' in acc:
        bm_obj("red_cross_h", box(.05, .004, .014, .001), mat("red_cross", (.5, .03, .03, 1), .6) if 'red_cross' not in bpy.data.materials else bpy.data.materials['red_cross'], (-.09, fy(-.09, 1.24, .006), 1.24))
        bm_obj("red_cross_v", box(.014, .004, .05, .001), bpy.data.materials['red_cross'], (-.09, fy(-.09, 1.24, .006), 1.24))
    if 'radio_pouch' in acc: bm_obj("radio_pouch", box(.05, .03, .08, .006), M['coat_dark'], (.16, fy(.16, 1.16, .012) - .02, 1.16))
    if 'tool_belt' in acc:
        for k, x in enumerate((-.14, -.05, .06, .15)): bm_obj("tool", box(.03, .03, .07 + .01 * (k % 2), .004), M['shoes'], (x, fy(x * .6, .98, .01), .93))
    if 'briefcase_hint' in acc: pass
# head scale for children
if HEADS != 1.0:
    c = Vector((0, .005, 1.66))
    for o in objs[head_start:]:
        o.location = c + (o.location - c) * HEADS; o.scale = tuple(s * HEADS for s in o.scale)

# ---- rig + export
os.environ["REF_Z"] = "1.775"; os.environ["TARGET_H"] = str(PR['height'])
if FAR: os.environ["MANN"] = "1"
out_dir = "D:/Faceless/models/city/people"; os.makedirs(out_dir, exist_ok=True)
os.environ["OUTGLB"] = f"{out_dir}/{PN}{'_far' if FAR else ''}.glb"; os.environ["OUTBLEND"] = f"D:/Faceless/models/src/people/{PN}{'_far' if FAR else ''}.blend"
os.makedirs("D:/Faceless/models/src/people", exist_ok=True)
exec(compile(open("D:/Faceless/models/src/build_human_v4_rig.py", encoding="utf-8").read(), "v4_rig", "exec"), globals())
