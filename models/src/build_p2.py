"""Stage 7, P2 props: stepladder (open/folded), tripod turnstile (ok/jammed), CCTV cameras (wall, dome), security desk with CRT monitors + VCR,
striped barrel, wet-floor sign with mop bucket, stair/balcony railings (ok/broken), roof parapet (ok/broken).
Run: D:\\Cosmoteer\\blender.exe -b -P D:\\Faceless\\models\\src\\build_p2.py"""
exec(open("D:/Faceless/models/src/lib_props.py", encoding="utf-8").read())

def beam(p0, p1, sx, sy, material, parent=None, name="beam", bev=.003):
    p0, p1 = Vector(p0), Vector(p1); d = p1 - p0; mid = (p0 + p1) / 2
    o = box((sx, sy, d.length), material, loc=tuple(mid), bev=bev, parent=parent, name=name)
    o.rotation_mode = 'QUATERNION'; o.rotation_quaternion = Vector((0, 0, 1)).rotation_difference(d.normalized()); o.rotation_mode = 'XYZ'
    return o
def tube(p0, p1, r, material, parent=None, name="tube", seg=8):
    p0, p1 = Vector(p0), Vector(p1); d = p1 - p0; mid = (p0 + p1) / 2
    o = cyl(r, d.length, material, loc=tuple(mid), seg=seg, parent=parent, name=name)
    o.rotation_mode = 'QUATERNION'; o.rotation_quaternion = Vector((0, 0, 1)).rotation_difference(d.normalized()); o.rotation_mode = 'XYZ'
    return o
def meshes_under(root):
    out = []
    def rec(o):
        for c in o.children:
            if c.type == 'MESH': out.append(c)
            rec(c)
    rec(root); return out
def merge(root, name):
    bpy.context.view_layer.update()
    ms = meshes_under(root)
    if not ms: return None
    for m in ms:                     # bake world transform so the join is safe
        mw = m.matrix_world.copy(); m.parent = None; m.matrix_world = mw
    j = join(ms, name); j.parent = root; j.matrix_parent_inverse = root.matrix_world.inverted()
    return j
def emissive(name, color, strength, rough=.5): return mat(name, tuple(c * .3 for c in color), rough, 0.0, emit=color, emit_strength=strength)
OUTDIR = None
def done(name, anims=False):
    smooth_angle([o for o in bpy.data.objects if o.type == 'MESH'], 40)
    return export(name, anims=anims, out_dir=OUTDIR)
def new():
    fresh(); palette(); mat("aluminum", (.55, .57, .6), .35, .9); mat("yellow_paint", (.62, .46, .03), .6); mat("black_paint", (.025, .025, .03), .6)
    mat("crt_off", (.02, .025, .03), .2); mat("beige", (.42, .4, .33), .6); mat("cardboard", (.38, .28, .16), .9); mat("paper", (.62, .6, .55), .9)
    mat("red_cloth", (.28, .02, .02), .8); mat("brass", (.55, .4, .12), .4, .8); mat("tape_black", (.01, .01, .01), .4)

# ======================================================================= stepladder
def stepladder(folded):
    new(); AL, BK = MATS["aluminum"], MATS["rubber"]
    root = empty("state_ok" if not folded else "state_ok")
    if not folded:
        H = 1.55
        for sx in (-.26, .26):
            beam((sx, -.2, 0), (sx * .85, 0, H), .035, .016, AL, root, "rail_front")
            beam((sx * .9, .42, 0), (sx * .85, .03, H - .03), .03, .018, AL, root, "rail_back")
            box((.05, .08, .03), BK, loc=(sx, -.2, .015), parent=root, name="foot")
            box((.05, .08, .03), BK, loc=(sx * .9, .42, .015), parent=root, name="foot")
        for i in range(1, 6):
            t = i / 6.0; y = -.2 + .2 * t * (H * t < 1e9 and 1) ; z = t * H
            xw = (.26 - .26 * .15 * t)
            box((xw * 2 + .02, .09, .02), AL, loc=(0, -.2 + (.2) * t, z), bev=.003, parent=root, name="step")
        box((.5, .32, .03), MATS["plastic_black"], loc=(0, .1, H + .01), bev=.006, parent=root, name="platform")
        box((.44, .03, .12), MATS["plastic_black"], loc=(0, -.04, H + .09), bev=.004, parent=root, name="tool_rail")
        for sx in (-1, 1): beam((sx * .24, -.1, .55), (sx * .2, .24, .55), .02, .012, MATS["steel"], root, "spreader")
        box((.43, .03, .02), AL, loc=(0, .32, .6), parent=root, name="back_brace")
        empty("ip_use", (0, -.8, 0), size=.15); empty("ip_hand", (0, -.1, H * .7), size=.08)
        box((.6, .7, 1.6), None, loc=(0, .1, .8), bev=0, name="stepladder-convcol")
    else:
        a = .2   # leaning towards +Y (wall)
        for sx in (-.2, .2):
            beam((sx, -.2, 0), (sx, -.05, 1.6), .035, .016, AL, root, "rail_front")
            beam((sx, -.12, 0), (sx, .03, 1.6), .03, .016, AL, root, "rail_back")
        for i in range(1, 6): box((.42, .07, .02), AL, loc=(0, -.2 + .15 * (i / 6.0) - 0, i * .26), bev=.003, parent=root, name="step")
        box((.46, .22, .03), MATS["plastic_black"], loc=(0, -.04, 1.62), bev=.006, parent=root, name="platform")
        for sx in (-1, 1): box((.05, .08, .03), BK, loc=(sx * .2, -.2, .015), parent=root, name="foot")
        root.rotation_euler = (0, 0, 0)
        empty("ip_use", (0, -.7, 0), size=.15); empty("ip_hand", (0, -.2, 1.0), size=.08)
        box((.5, .3, 1.65), None, loc=(0, -.08, .82), bev=0, name="stepladder_folded-convcol")
    merge(root, "stepladder")
    done("stepladder_folded" if folded else "stepladder_open")

# ======================================================================= turnstile (tripod)
def turnstile():
    new(); G = MATS["paint_gray"]; ST = MATS["steel"]
    green = emissive("led_green", (.1, 1, .2), 3); red = emissive("led_red", (1, .1, .05), 3); dim = MATS["crt_off"]
    base = empty("turnstile_base")
    box((.5, .5, .05), MATS["concrete_dark"], loc=(0, 0, .025), bev=.005, parent=base, name="plate")
    box((.24, .38, 1.0), G, loc=(0, 0, .55), bev=.012, parent=base, name="post", seg=3)
    box((.28, .42, .06), MATS["steel_dark"], loc=(0, 0, 1.08), bev=.01, parent=base, name="cap")
    box((.2, .1, .16), MATS["plastic_black"], loc=(0, -.17, .95), bev=.008, parent=base, name="reader")
    box((.08, .02, .03), MATS["wire_black"], loc=(0, -.222, .98), bev=0, parent=base, name="card_slot")
    cyl(.095, .08, ST, loc=(.2, 0, .86), seg=12, rot=(0, math.pi / 2, 0), parent=base, name="hub_bearing")
    merge(base, "turnstile_body")
    # arms: hub tilted 45deg, 3 tubes at 120 deg; node 'arms' rotates around its local X
    arms = empty("arms", (.14, 0, .86), size=.1)
    cyl(.07, .12, ST, loc=(.0, 0, 0), seg=12, rot=(0, math.pi / 2, 0), parent=arms, name="hub")
    for k in range(3):
        a = k * 2 * math.pi / 3
        end = Vector((.12, math.cos(a) * .62, math.sin(a) * .62)) if False else Vector((.1, math.cos(a) * .56, math.sin(a) * .56))
        tube((.05, 0, 0), tuple(end), .018, ST, arms, "arm")
        sphere(.025, ST, loc=tuple(end), parent=arms, name="arm_tip", seg=8, rings=6)
    merge(arms, "turnstile_arms")
    # lamps (state dependent)
    so = empty("state_ok"); box((.03, .14, .012), green, loc=(0, -.10, 1.115), bev=0, parent=so, name="lamp_green")
    sl = empty("state_loose"); box((.03, .14, .012), red, loc=(0, -.10, 1.115), bev=0, parent=sl, name="lamp_red")
    # jam marker: bent third arm drawn by a second set of arms (state_loose) rotated 18 deg and a yellow warning tape tag
    arms_j = empty("arms_jam", (.14, 0, .86), size=.1, parent=sl); arms_j.rotation_euler = (.31, 0, 0)
    for k in range(3):
        a = k * 2 * math.pi / 3 + (.12 if k == 0 else 0)
        end = Vector((.1, math.cos(a) * .56, math.sin(a) * .56)) + (Vector((.0, 0, -.12)) if k == 0 else Vector((0, 0, 0)))
        tube((.05, 0, 0), tuple(end), .018, ST, arms_j, "arm_j")
    box((.02, .3, .02), MATS["paint_yellow"], loc=(.14, 0, .86 + .02), bev=0, parent=sl, name="tape")
    merge(so, "lamp_ok"); merge(sl, "jam_set")
    animate(arms, "pass", [(1, dict(rot=(0, 0, 0))), (18, dict(rot=(2 * math.pi / 3, 0, 0)))])
    animate(arms, "idle_jam", [(1, dict(rot=(0, 0, 0))), (3, dict(rot=(.08, 0, 0))), (5, dict(rot=(0, 0, 0)))])
    box((.5, 1.2, 1.1), None, loc=(0, 0, .55), bev=0, name="turnstile-col")
    empty("ip_use", (-.55, 0, 0), size=.15); empty("ip_hand", (.14, .45, .86), size=.08)
    done("turnstile", anims=True)

# ======================================================================= CCTV
def cctv_wall():
    new(); G = MATS["paint_gray"]; led = emissive("led_red", (1, .05, .02), 4); led_off = MATS["crt_off"]
    wall = empty("wall_bracket")
    box((.14, .02, .2), MATS["steel_dark"], loc=(0, .01, 0), bev=.003, parent=wall, name="plate")
    tube((0, .02, 0), (0, -.14, .06), .016, MATS["steel_dark"], wall, "arm")
    box((.06, .06, .06), MATS["steel_dark"], loc=(0, -.15, .07), bev=.004, parent=wall, name="joint")
    merge(wall, "bracket")
    for st, broken in (("state_ok", False), ("state_broken", True)):
        root = empty(st)
        head = empty("cam_head_" + ("broken" if broken else "ok"), (0, -.15, .07), size=.1, parent=root)
        box((.1, .3, .095), G, loc=(0, -.12, .06 - .07 + .07), bev=.012, parent=head, name="housing", seg=3)
        box((.12, .32, .018), G, loc=(0, -.13, .115), bev=.006, parent=head, name="hood")
        cyl(.034, .014, MATS["glass"], loc=(0, -.285, .055), seg=14, rot=(math.pi / 2, 0, 0), parent=head, name="lens")
        cyl(.045, .01, MATS["steel_dark"], loc=(0, -.275, .055), seg=14, rot=(math.pi / 2, 0, 0), parent=head, name="lens_ring")
        sphere(.007, led_off if broken else led, loc=(.035, -.27, .095), parent=head, seg=8, rings=5, name="led")
        if broken: box((.09, .02, .002), MATS["soot"], loc=(0, -.29, .05), bev=0, parent=head, name="crack")
        for c in list(head.children): c.location.z -= .07 if False else 0
        merge(head, head.name + "_mesh")
        # the housing was modelled around z=0.06; shift the merged mesh so the pivot sits at the bracket joint
        head.location = (0, -.15, .07)
        if broken: head.rotation_euler = (.45, 0, .25)
        else: animate(head, "sweep_loop", [(1, dict(rot=(0, 0, 0))), (25, dict(rot=(0, 0, -.7))), (49, dict(rot=(0, 0, 0))), (73, dict(rot=(0, 0, .7))), (97, dict(rot=(0, 0, 0)))])
    box((.2, .45, .25), None, loc=(0, -.12, .05), bev=0, name="cctv_wall-convcol")
    empty("ip_use", (0, -1.0, -1.3), size=.12)
    done("cctv_wall", anims=True)
def cctv_dome():
    new(); GL = mat("glass_dark", (.06, .07, .08), .05, 0.0); G = MATS["paint_gray"]; led = emissive("led_red", (1, .05, .02), 4)
    base = empty("dome_base")
    lathe([(0, 0), (.1, 0), (.11, .008), (.11, .035), (.085, .045), (0, .045)], G, parent=base, seg=20, name="mount", loc=(0, 0, 0))
    lathe([(.1, 0), (.095, -.04), (.075, -.085), (.04, -.108), (0, -.115)], GL, parent=base, seg=20, name="bubble")
    merge(base, "dome_shell")
    inner = empty("cam_head", (0, 0, -.045), size=.06)
    box((.05, .08, .05), MATS["steel_dark"], loc=(0, -.02, 0), bev=.004, parent=inner, name="cam")
    cyl(.016, .02, MATS["glass"], loc=(0, -.06, 0), seg=10, rot=(math.pi / 2, 0, 0), parent=inner, name="lens")
    merge(inner, "dome_cam")
    so = empty("state_ok"); sphere(.006, led, loc=(.085, 0, .02), parent=so, seg=8, rings=5, name="led_on")
    sb = empty("state_broken"); sphere(.006, MATS["crt_off"], loc=(.085, 0, .02), parent=sb, seg=8, rings=5, name="led_off")
    animate(inner, "sweep_loop", [(1, dict(rot=(0, 0, 0))), (25, dict(rot=(0, 0, -1.0))), (49, dict(rot=(0, 0, 0))), (73, dict(rot=(0, 0, 1.0))), (97, dict(rot=(0, 0, 0)))])
    box((.24, .24, .16), None, loc=(0, 0, -.03), bev=0, name="cctv_dome-convcol")
    done("cctv_dome", anims=True)

# ======================================================================= security desk
def desk():
    new(); BG, W_ = MATS["beige"], MATS["wood"]; screen = emissive("crt_screen", (.45, .55, .6), 1.2); off = MATS["crt_off"]
    d = empty("desk_body")
    box((1.7, .75, .06), W_, loc=(0, 0, .73), bev=.008, parent=d, name="top")
    box((1.6, .04, .72), MATS["paint_gray"], loc=(0, .34, .36), bev=.004, parent=d, name="back")
    for sx in (-.78, .78): box((.04, .7, .72), MATS["paint_gray"], loc=(sx, 0, .36), bev=.004, parent=d, name="side")
    box((.5, .66, .68), MATS["paint_gray"], loc=(-.52, 0, .38), bev=.006, parent=d, name="drawers")
    for i in range(3): box((.4, .02, .17), MATS["steel_dark"], loc=(-.52, -.335, .2 + i * .2), bev=.004, parent=d, name="drawer_front")
    box((1.7, .62, .24), MATS["paint_gray"], loc=(0, .06, 1.24), bev=.008, parent=d, name="monitor_shelf") if False else None
    box((.5, .4, .06), MATS["paint_gray"], loc=(.15, .12, .79), bev=.006, parent=d, name="shelf_low")
    box((.4, .09, .22), MATS["steel_dark"], loc=(-.05, .29, .895), bev=.004, parent=d, name="support")
    # keyboard + intercom + phone + lamp
    box((.44, .17, .025), MATS["beige"], loc=(.4, -.18, .775), bev=.004, parent=d, name="keyboard")
    box((.2, .14, .1), MATS["plastic_black"], loc=(.62, .1, .8), bev=.006, parent=d, name="intercom")
    box((.18, .18, .07), MATS["beige"], loc=(-.3, -.1, .795), bev=.01, parent=d, name="phone", seg=3)
    box((.15, .05, .04), MATS["beige"], loc=(-.3, -.1, .84), bev=.01, parent=d, name="handset")
    box((.32, .24, .08), MATS["beige"], loc=(.05, -.05, .77), bev=.006, parent=d, name="tape_deck_dummy") if False else None
    merge(d, "desk_mesh")
    # VCR + 4 CRT monitors stack (rack above the desk)
    rack = empty("monitor_rack")
    box((.9, .4, .03), MATS["steel_dark"], loc=(.1, .22, 1.05), bev=.003, parent=rack, name="r1")
    box((.9, .4, .03), MATS["steel_dark"], loc=(.1, .22, 1.4), bev=.003, parent=rack, name="r2")
    for sx in (-.4, .6): box((.04, .4, .4), MATS["steel_dark"], loc=(sx, .22, 1.225), bev=.003, parent=rack, name="post")
    # VCR on the desk
    box((.42, .3, .09), MATS["black_paint"], loc=(.05, -.05, .805), bev=.006, parent=rack, name="vcr")
    box((.22, .02, .03), MATS["steel_dark"], loc=(-.05, -.205, .81), bev=0, parent=rack, name="vcr_slot")
    for k in range(4): box((.025, .01, .012), MATS["steel"], loc=(.07 + k * .035, -.205, .79), bev=0, parent=rack, name="vcr_btn")
    box((.1, .01, .02), MATS["paint_yellow"], loc=(.17, -.205, .82), bev=0, parent=rack, name="vcr_label")
    states = {}
    for nm, scr in (("state_ok", screen), ("state_loose", off)):
        st = empty(nm)
        for i, (sx, z) in enumerate(((-.12, 1.06), (.32, 1.06), (-.12, 1.41), (.32, 1.41))):
            box((.36, .32, .3), MATS["beige"], loc=(sx, .21, z + .15), bev=.012, parent=st, name="crt_case", seg=2)
            box((.3, .02, .24), scr, loc=(sx, .03, z + .15), bev=.005, parent=st, name="crt_screen")
            box((.28, .2, .2), MATS["beige"], loc=(sx, .36, z + .15), bev=.02, parent=st, name="crt_back", taper=.85)
        merge(st, nm + "_mesh")
    merge(rack, "rack_mesh")
    box((1.7, .8, 1.6), None, loc=(0, 0, .8), bev=0, name="desk_security-convcol")
    empty("ip_use", (0, -.9, 0), size=.15); empty("ip_hand", (.05, -.2, .85), size=.08)
    done("desk_security")

# ======================================================================= striped barrel (tank)
def barrel():
    new(); BL = mat("tank_blue", (.08, .12, .17), .6, .4); Y = MATS["yellow_paint"]
    b = empty("barrel")
    lathe([(0, 0), (.29, 0), (.30, .02), (.3, .86), (.29, .88), (0, .88)], BL, parent=b, seg=24, name="body")
    for z in (.2, .66): lathe([(.295, z - .018), (.312, z - .01), (.312, z + .01), (.295, z + .018)], BL, parent=b, seg=24, name="rib")
    lathe([(.3, .38), (.303, .38), (.303, .52), (.3, .52)], Y, parent=b, seg=24, name="stripe")
    lathe([(0, .88), (.27, .88), (.25, .895), (0, .895)], MATS["steel"], parent=b, seg=20, name="lid")
    cyl(.035, .02, MATS["steel_dark"], loc=(.12, 0, .905), seg=10, parent=b, name="bung")
    cyl(.045, .02, MATS["steel_dark"], loc=(-.12, .08, .905), seg=10, parent=b, name="bung2")
    merge(b, "barrel_mesh")
    box((.6, .6, .88), None, loc=(0, 0, .44), bev=0, name="barrel-convcol")
    empty("ip_use", (0, -.7, 0), size=.12); empty("ip_hit", (0, 0, .44), size=.1)
    done("barrel_stripe")

# ======================================================================= wet floor sign + mop bucket
def mop():
    new(); Y = MATS["paint_yellow"]; BK = MATS["black_paint"]
    s = empty("sign")
    for sy in (-1, 1):
        # A-frame sign panels
        panel = box((.3, .015, .6), Y, loc=(0, sy * .12, .3), bev=.006, parent=s, name="panel")
        panel.rotation_euler = (sy * .24, 0, 0)
        tri = poly_prism([(-.08, -.06), (.08, -.06), (0, .06)], .004, BK, loc=(0, 0, 0), parent=s, name="warning_tri")
        tri.rotation_euler = (math.pi / 2 + sy * .24, 0, 0); tri.location = (0, sy * (.12 - .008 * sy) + (-.01 if sy < 0 else .01), .38)
        box((.2, .004, .03), BK, loc=(0, sy * .125, .22), bev=0, parent=s, name="bar").rotation_euler = (sy * .24, 0, 0)
    box((.3, .02, .04), Y, loc=(0, 0, .6), bev=.005, parent=s, name="hinge")
    merge(s, "sign_mesh"); s.location = (.55, -.1, 0)
    bk = empty("bucket"); lathe([(0, 0), (.17, 0), (.2, .3), (0, .3)], mat("bucket_blue", (.06, .12, .25), .6), parent=bk, seg=20, name="bucket_body")
    lathe([(.2, .3), (.205, .3), (.205, .31), (.2, .31)], MATS["steel"], parent=bk, seg=20, name="rim")
    tube((-.2, 0, .3), (.2, 0, .3), .006, MATS["steel"], bk, "handle")
    box((.28, .2, .12), MATS["black_paint"], loc=(0, 0, .35), bev=.01, parent=bk, name="wringer")
    merge(bk, "bucket_mesh"); bk.location = (0, 0, 0)
    mp = empty("mop", (0, 0, .0)); tube((.02, .0, .3), (.18, .0, 1.35), .012, MATS["wood"], mp, "handle")
    sphere(.075, MATS["paper"], loc=(.02, 0, .26), scale=(1, 1, 1.4), parent=mp, seg=10, rings=6, name="mop_head")
    box((.12, .03, .03), MATS["steel"], loc=(.04, 0, .42), bev=.004, parent=mp, name="clamp")
    merge(mp, "mop_mesh")
    box((1.0, .5, 1.4), None, loc=(.2, 0, .7), bev=0, name="mop-convcol")
    empty("ip_use", (0, -.7, 0), size=.12); empty("ip_hand", (.18, 0, 1.0), size=.08); empty("ip_hit", (-.3, -.1, .02), size=.1)
    done("mop_wet_sign")

# ======================================================================= railings
def railing(kind):
    new(); ST, PG = MATS["steel_dark"], MATS["paint_gray"]
    L_ = 2.0 if kind == "stairs" else 1.5; H_ = .95 if kind == "stairs" else 1.05
    def posts(parent, lean=0.0):
        for sx in (-L_ / 2, L_ / 2): box((.06, .06, H_), ST, loc=(sx, 0, H_ / 2), bev=.004, parent=parent, name="post")
    def balusters(parent, skip=(), n=11, bend=None):
        for i in range(n):
            if i in skip: continue
            x = -L_ / 2 + .1 + i * (L_ - .2) / (n - 1)
            if bend and i in bend: beam((x, 0, .1), (x + .05, .05, H_ - .1), .018, .018, ST, parent, "baluster_bent"); continue
            box((.018, .018, H_ - .14), ST, loc=(x, 0, .1 + (H_ - .14) / 2), bev=.002, parent=parent, name="baluster")
    ok = empty("state_ok"); posts(ok)
    box((L_, .07, .045), MATS["wood"] if kind == "stairs" else ST, loc=(0, 0, H_ + .0225), bev=.006, parent=ok, name="handrail")
    box((L_, .03, .03), ST, loc=(0, 0, .07), bev=.003, parent=ok, name="bottom_rail"); balusters(ok)
    merge(ok, "ok_mesh")
    br = empty("state_broken"); posts(br)
    # handrail snapped in the middle, left half sagging, right half hanging from the post; missing/bent balusters
    r1 = box((L_ * .55, .07, .045), MATS["wood"] if kind == "stairs" else ST, loc=(-L_ * .225, 0, H_ - .05), bev=.006, parent=br, name="handrail_a"); r1.rotation_euler = (0, .13, 0)
    r2 = box((L_ * .4, .07, .045), MATS["wood"] if kind == "stairs" else ST, loc=(L_ * .3, 0, H_ - .32), bev=.006, parent=br, name="handrail_b"); r2.rotation_euler = (0, -.75, 0)
    box((.04, .05, .04), MATS["soot"], loc=(-.05, 0, H_ - .18), bev=0, parent=br, name="splinter")
    box((L_, .03, .03), ST, loc=(0, 0, .07), bev=.003, parent=br, name="bottom_rail"); balusters(br, skip=(4, 5, 6), bend=(3, 7))
    for k, x in enumerate((-.02, .12, .24)): beam((x, .02, .05), (x + .3, .1, .02 + .02 * k), .02, .02, ST, br, "fallen_baluster").location.z += 0
    merge(br, "broken_mesh")
    box((L_, .15, H_), None, loc=(0, 0, H_ / 2), bev=0, name="railing-convcol")
    empty("ip_use", (0, -.7, 0), size=.12); empty("ip_hit", (0, .6, 0), size=.12); empty("ip_hand", (0, 0, H_), size=.08)
    done("railing_stairs" if kind == "stairs" else "railing_balcony")

def parapet():
    new(); C, CD = MATS["concrete"], MATS["concrete_dark"]
    roof = empty("roof_edge")
    box((3.4, 1.6, .2), CD, loc=(0, .8, -.1), bev=.01, parent=roof, name="roof_slab")
    box((3.4, .1, .1), MATS["steel_dark"], loc=(0, .05, .05), bev=.004, parent=roof, name="flashing")
    merge(roof, "roof_mesh")
    ok = empty("state_ok")
    box((3.0, .3, .9), C, loc=(0, 0, .45), bev=.01, parent=ok, name="wall")
    box((3.05, .36, .07), C, loc=(0, 0, .93), bev=.008, parent=ok, name="coping")
    for sx in (-1.0, 0, 1.0): box((.03, .31, .88), CD, loc=(sx, 0, .45), bev=0, parent=ok, name="seam")
    merge(ok, "ok_mesh")
    bk = empty("state_broken")
    box((1.0, .3, .9), C, loc=(-1.0, 0, .45), bev=.01, parent=bk, name="wall_l"); box((1.05, .36, .07), C, loc=(-1.0, 0, .93), bev=.008, parent=bk, name="coping_l")
    box((.75, .3, .9), C, loc=(1.12, 0, .45), bev=.01, parent=bk, name="wall_r"); box((.8, .36, .07), C, loc=(1.12, 0, .93), bev=.008, parent=bk, name="coping_r")
    box((.8, .3, .3), C, loc=(0.1, 0, .15), bev=.01, parent=bk, name="stub")                       # remaining bottom of the gap
    for i, x in enumerate((-.45, -.2, .1, .35)): beam((x, 0, .3), (x + .03, 0, .62 + .06 * (i % 2)), .016, .016, MATS["rebar_rust"], bk, "rebar")
    rnd = random.Random(2)
    for i in range(6): rock_blob(.07 + .04 * rnd.random(), C, seed=30 + i, loc=(-.4 + .25 * i, rnd.uniform(.3, .8), .04), flat=.6, subdiv=1, rough=.3, parent=bk, name="chunk")
    merge(bk, "broken_mesh")
    box((3.0, .36, .95), None, loc=(0, 0, .47), bev=0, name="parapet-col")
    empty("ip_use", (0, .8, 0), size=.12); empty("ip_hit", (0, -.9, -3.0), size=.12); empty("ip_hand", (.1, 0, .93), size=.08)
    done("parapet")

stepladder(False); stepladder(True); turnstile(); cctv_wall(); cctv_dome(); desk(); barrel(); mop(); railing("stairs"); railing("balcony"); parapet()
