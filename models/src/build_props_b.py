"""Street props, stage 3 (part B): trees (birch, poplar, maple, bare), bushes, fences, garages, transformer booth, press kiosk, playground, pull-up bar,
carpet beater, standpipe, tower crane, antenna tower, satellite dish, vent shaft, roof hatch, fire escape, downpipe, plank bridge, crate stack, laundry line, shop signs.
Run: D:\\Cosmoteer\\blender.exe -b -P build_props_b.py -> models/city/props/*.glb"""
_s = open("D:/Faceless/models/src/build_props_a.py", encoding="utf-8").read()
exec(_s[:_s.index("# ------------------------------------------------------------------ street lamp")])

def foliage(name, root, color, rough, positions, r, seed, flat=.75, subdiv=2, mat_name="foliage"):
    m = mat(mat_name, color, rough)
    rnd = random.Random(seed)
    for i, p in enumerate(positions):
        rock_blob(r * rnd.uniform(.8, 1.15), m, seed=seed + i, loc=p, flat=flat, subdiv=subdiv, rough=.28, parent=root, name=name)

def trunk(root, height, r0, r1, mat_, lean=(0, 0)):
    lathe([(0, 0), (r0, 0), (r0 * .9, .5), (r1, height), (0, height)], mat_, parent=root, seg=10, name="trunk")

def tree(kind):
    pnew(); bark = mat("bark", (.1, .07, .05), .95); root = empty("tree_" + kind)
    if kind == "birch":
        white = mat("bark_birch", (.5, .5, .46), .9); trunk(root, 5.0, .12, .06, white)
        for z in (.6, 1.3, 2.0, 2.9, 3.8): box((.14, .14, .05), MATS["soot"], loc=(0, 0, z), bev=0, parent=root, name="bark_mark").scale = (1, .4, 1)
        for a, h, d in ((0, 3.8, .5), (2.1, 4.4, .6), (4.2, 4.0, .55)): tube((0, 0, 3.0), (math.cos(a) * d, math.sin(a) * d, h), .025, white, root, "branch", 6)
        foliage("crown", root, (.14, .22, .08), .85, [(.0, 0, 4.3), (.5, .3, 4.0), (-.4, .4, 4.2), (.1, -.5, 4.5), (-.3, -.3, 3.7), (.4, -.4, 3.8), (0, .1, 4.9)], .62, 3)
        h_ = 5.4
    elif kind == "poplar":
        trunk(root, 4.2, .16, .08, bark)
        foliage("crown", root, (.1, .2, .08), .85, [(0, 0, 1.8 + k * .85) for k in range(7)], .62, 11, flat=1.7)
        h_ = 8.0
    elif kind == "maple":
        trunk(root, 3.2, .22, .12, bark)
        for a in (.3, 1.7, 3.0, 4.4, 5.5): tube((0, 0, 2.7), (math.cos(a) * 1.0, math.sin(a) * 1.0, 4.2), .06, bark, root, "branch", 6)
        foliage("crown", root, (.16, .26, .07), .85, [(math.cos(a) * 1.2, math.sin(a) * 1.2, 4.0 + .15 * k) for k, a in enumerate((.3, 1.2, 2.2, 3.2, 4.2, 5.2))] + [(0, 0, 4.8), (.4, .2, 5.4), (-.4, -.1, 4.4)], 1.05, 21, flat=.8)
        h_ = 6.4
    else:  # bare / autumn
        trunk(root, 3.4, .2, .09, bark)
        for k, a in enumerate((0, 1.1, 2.2, 3.3, 4.4, 5.5)):
            p1 = (math.cos(a) * .6, math.sin(a) * .6, 3.0 + .3 * (k % 2)); p2 = (math.cos(a) * 1.5, math.sin(a) * 1.5, 4.6 + .3 * (k % 3))
            tube((0, 0, 2.4 + .2 * (k % 3)), p1, .06, bark, root, "branch_a", 6); tube(p1, p2, .035, bark, root, "branch_b", 6)
            tube(p2, (p2[0] * 1.2, p2[1] * 1.2, p2[2] + .8), .018, bark, root, "twig", 5); tube(p1, (p1[0] * 1.6, p1[1] * 1.6 + .3, p1[2] + .9), .02, bark, root, "twig", 5)
        foliage("leaves", root, (.4, .2, .05), .9, [(.9, .3, 4.0), (-.8, -.5, 4.2), (.2, 1.1, 3.8)], .25, 31, flat=.5, subdiv=1, mat_name="leaves_autumn")
        h_ = 6.0
    merge(root, "tree_mesh")
    box((.4, .4, 3.0), None, loc=(0, 0, 1.5), bev=0, name=f"tree_{kind}-col"); empty("ip_use", (.8, 0, 0), size=.15); empty("ip_hit", (0, 0, 1.2), size=.12)
    done("tree_" + kind)

def bush(v):
    pnew(); r = empty("bush"); m = mat("foliage", (.1, .2, .07) if v == 0 else (.18, .22, .06), .85)
    rnd = random.Random(5 + v)
    for i in range(6 + v * 2): rock_blob(.32 + .1 * rnd.random(), m, seed=40 + i + v * 7, loc=(rnd.uniform(-.55, .55), rnd.uniform(-.4, .4), .35 + rnd.uniform(0, .2)), flat=.8, subdiv=1, rough=.3, parent=r, name="clump")
    merge(r, "bush_mesh"); box((1.2, 1.0, .8), None, loc=(0, 0, .4), bev=0, name="bush-convcol"); done("bush_a" if v == 0 else "bush_b")

def fences():
    pnew(); r = empty("fence"); ST = MATS["steel_dark"]                # chain-link 3 m
    for sx in (-1.5, 0, 1.5): cyl(.04, 1.8, ST, loc=(sx, 0, .9), seg=8, parent=r, name="post")
    box((3.0, .03, .04), ST, loc=(0, 0, 1.78), bev=0, parent=r, name="top_rail"); box((3.0, .03, .04), ST, loc=(0, 0, .15), bev=0, parent=r, name="bottom_rail")
    for i in range(-14, 15):                                            # diagonal wire lines
        beam((i * .1 - .2, 0, .15), (i * .1 + .2, 0, 1.78), .006, .006, ST, r, "wire", 0)
    merge(r, "mesh_fence"); box((3.1, .1, 1.8), None, loc=(0, 0, .9), bev=0, name="fence_mesh-col"); done("fence_mesh")
    pnew(); r = empty("fence"); C = MATS["concrete"]; CD = MATS["concrete_dark"]       # concrete panels 3 m
    for sx in (-1.5, 0, 1.5): box((.22, .26, 2.4), CD, loc=(sx, 0, 1.2), bev=.01, parent=r, name="post")
    for k in range(6): box((2.8, .12, .28), C, loc=(-.0, 0, .2 + k * .4), bev=.008, parent=r, name="panel")
    for sx in (-1.4, 1.4): box((.1, .16, .1), CD, loc=(sx, 0, 2.45), bev=.01, parent=r, name="cap")
    merge(r, "concrete_fence"); box((3.1, .28, 2.4), None, loc=(0, 0, 1.2), bev=0, name="fence_concrete-col"); done("fence_concrete")
    pnew(); r = empty("fence"); W_ = MATS["wood"]                                       # picket 3 m
    for sx in (-1.5, 1.5): box((.09, .09, 1.2), W_, loc=(sx, 0, .6), bev=.006, parent=r, name="post")
    for z in (.3, .85): box((3.0, .05, .07), W_, loc=(0, .04, z), bev=.004, parent=r, name="rail")
    for i in range(18): box((.08, .02, 1.0), W_, loc=(-1.4 + i * .165, -.02, .55 + (.03 if i % 5 == 0 else 0)), bev=.004, parent=r, name="picket")
    merge(r, "picket_fence"); box((3.1, .12, 1.2), None, loc=(0, 0, .6), bev=0, name="fence_picket-col"); done("fence_picket")

def garages():
    for n_, one in ((1, "garage_gate"), (5, "garage_row")):
        pnew(); r = empty(one); BK = MATS["brick"]; MT = mat("garage_door", (.3, .2, .08), .65, .3)
        for g in range(n_):
            x0 = (g - (n_ - 1) / 2) * 3.0
            box((3.0, 5.0, 2.7), BK, loc=(x0, 2.5, 1.35), bev=.01, parent=r, name="shell")
            box((2.5, .1, 2.2), MT, loc=(x0, -.04, 1.1), bev=.01, parent=r, name="door")
            for k in range(5): box((2.4, .02, .04), MATS["steel_dark"], loc=(x0, -.1, .3 + k * .4), bev=0, parent=r, name="door_rib")
            box((.12, .06, .18), MATS["steel_dark"], loc=(x0 + .95, -.12, 1.1), bev=.006, parent=r, name="handle"); box((.14, .04, .1), MATS["steel"], loc=(x0 + .95, -.14, 1.0), bev=0, parent=r, name="lock_plate")
            box((2.7, .06, .16), MATS["concrete_dark"], loc=(x0, -.03, 2.3), bev=.004, parent=r, name="lintel")
        box((3.0 * n_ + .2, 5.2, .22), MATS["asphalt"], loc=(0, 2.5, 2.8), bev=.01, parent=r, name="roof")
        merge(r, "garage_mesh"); box((3.0 * n_, 5.0, 2.8), None, loc=(0, 2.5, 1.4), bev=0, name=one + "-col"); empty("ip_use", (0, -1.2, 0), size=.15); empty("ip_hand", (.95, -.2, 1.1), size=.08)
        done(one)

def transformer_booth():
    pnew(); r = empty("transformer_booth")
    so = empty("state_ok"); sl = empty("state_loose")
    box((2.6, 2.0, 3.0), MATS["brick"], loc=(0, 0, 1.5), bev=.01, parent=r, name="body"); box((2.8, 2.2, .2), MATS["concrete_dark"], loc=(0, 0, 3.1), bev=.01, parent=r, name="roof")
    box((.9, .06, 2.0), MATS["steel_dark"], loc=(0, -1.03, 1.0), bev=.006, parent=r, name="door_ok")
    box((.28, .03, .28), MATS["sign_yellow"] if "sign_yellow" in MATS else MATS["paint_yellow"], loc=(0, -1.07, 2.2), bev=0, parent=r, name="warning_sign")
    for x in (-.8, .8): box((.1, .04, .5), MATS["steel"], loc=(x, -1.03, 1.0), bev=.004, parent=r, name="vent_grille")
    for k in range(3): cyl(.04, .3, MATS["insulator"], loc=(-.7 + k * .7, 0, 3.35), seg=8, parent=r, name="insulator")
    merge(r, "booth_mesh")
    hd = empty("door_anim", (-.45, -1.04, 1.0), size=.1); box((.9, .06, 2.0), MATS["steel_dark"], loc=(.45, 0, 0), bev=.006, parent=hd, name="door_leaf"); merge(hd, "door_mesh")
    animate(hd, "open", [(1, dict(rot=(0, 0, 0))), (20, dict(rot=(0, 0, -1.6)))]); animate(hd, "close", [(1, dict(rot=(0, 0, -1.6))), (20, dict(rot=(0, 0, 0)))])
    empty("ip_spark", (0, -1.0, 1.3), size=.1); empty("ip_use", (0, -1.6, 0), size=.15); empty("ip_hand", (.5, -1.1, 1.0), size=.08)
    box((2.7, 2.1, 3.2), None, loc=(0, 0, 1.6), bev=0, name="transformer_booth-col")
    done("transformer_booth", anims=True)

def kiosk():
    pnew(); r = empty("kiosk"); G = MATS["green_paint"]
    box((2.0, 1.5, 2.4), G, loc=(0, 0, 1.2), bev=.02, parent=r, name="body"); box((2.3, 1.8, .12), MATS["steel_dark"], loc=(0, 0, 2.46), bev=.01, parent=r, name="roof")
    box((1.5, .05, .9), MATS["glass_light"], loc=(0, -.77, 1.5), bev=0, parent=r, name="window"); box((1.7, .3, .06), MATS["wood"], loc=(0, -.9, 1.0), bev=.008, parent=r, name="counter")
    box((1.4, .04, .45), MATS["sign_blue"], loc=(0, -.78, 2.2), bev=0, parent=r, name="sign_board"); box((1.1, .01, .1), MATS["sign_white"], loc=(0, -.8, 2.2), bev=0, parent=r, name="sign_text")
    for k in range(4): box((.3, .01, .4), MATS["poster"], loc=(-.6 + k * .4, -.78, 1.25), bev=0, parent=r, name="newspaper")
    merge(r, "kiosk_mesh"); box((2.1, 1.6, 2.5), None, loc=(0, 0, 1.25), bev=0, name="kiosk-col"); empty("ip_use", (0, -1.4, 0), size=.15); empty("ip_hand", (0, -.9, 1.1), size=.08)
    done("kiosk")

def playground():
    pnew(); ST = MATS["paint_yellow"]; W_ = MATS["wood"]
    r = empty("sandbox")
    for sx, sy, w, d in ((0, .9, 2.0, .1), (0, -.9, 2.0, .1), (1.0, 0, .1, 1.8), (-1.0, 0, .1, 1.8)): box((w, d, .3), W_, loc=(sx, sy, .15), bev=.008, parent=r, name="board")
    box((1.9, 1.7, .2), mat("sand", (.35, .3, .2), 1.0), loc=(0, 0, .1), bev=0, parent=r, name="sand"); merge(r, "sandbox_mesh"); box((2.1, 2.0, .35), None, loc=(0, 0, .17), bev=0, name="sandbox-col"); done("sandbox")
    pnew(); ST = MATS["paint_yellow"]; W_ = MATS["wood"]; r = empty("slide")
    for sx in (-.3, .3): box((.06, .06, 1.9), ST, loc=(sx, 0, .95), bev=.004, parent=r, name="post")
    box((.9, .8, .06), MATS["wood"], loc=(0, 0, 1.55), bev=.006, parent=r, name="platform"); box((.7, .06, .8), ST, loc=(0, .4, 1.9), bev=.004, parent=r, name="rail") if False else None
    for sx in (-.35, .35): beam((sx, .0, .05), (sx, .0, 1.55), .02, .02, ST, r, "ladder_rail", 0) if False else None
    for k in range(5): box((.5, .06, .03), MATS["steel"], loc=(0, .5, .35 + k * .3), bev=0, parent=r, name="ladder_step").rotation_euler = (0, 0, 0)
    for sx in (-.35, .35): beam((sx, .55, .05), (sx, .25, 1.5), .03, .03, ST, r, "ladder_side", .002)
    beam((0, -.4, 1.58), (0, -1.9, .1), .55, .05, MATS["steel"], r, "slide_pan", .003)
    for sx in (-.3, .3): beam((sx, -.4, 1.62), (sx, -1.9, .18), .04, .1, ST, r, "slide_side", .003)
    merge(r, "slide_mesh"); box((1.0, 2.7, 1.9), None, loc=(0, -.7, .95), bev=0, name="slide-convcol"); empty("ip_use", (0, 1.2, 0), size=.15); done("slide")
    pnew(); ST = MATS["paint_yellow"]; W_ = MATS["wood"]; r = empty("swing")
    for sx in (-1.3, 1.3):
        beam((sx, -.6, 0), (sx, 0, 2.2), .08, .08, ST, r, "a_leg_f", .004); beam((sx, .6, 0), (sx, 0, 2.2), .08, .08, ST, r, "a_leg_b", .004)
    tube((-1.3, 0, 2.2), (1.3, 0, 2.2), .04, ST, r, "top_bar", 8)
    sw = empty("seat_pivot", (0, 0, 2.2), size=.1)
    for sx in (-.4, .4): tube((sx, 0, 0), (sx, 0, -1.7), .008, MATS["steel"], sw, "chain", 4)
    box((.5, .2, .04), MATS["wood"], loc=(0, 0, -1.72), bev=.006, parent=sw, name="seat")
    animate(sw, "swing_loop", [(1, dict(rot=(.0, 0, 0))), (13, dict(rot=(.5, 0, 0))), (25, dict(rot=(0, 0, 0))), (37, dict(rot=(-.5, 0, 0))), (49, dict(rot=(0, 0, 0)))])
    merge(r, "swing_frame")
    box((2.8, 1.4, 2.3), None, loc=(0, 0, 1.15), bev=0, name="swing-col"); empty("ip_use", (0, -1.2, 0), size=.15); empty("ip_hand", (0, 0, .5), size=.08); done("swing", anims=True)

def yard_small():
    pnew(); r = empty("pullup_bar"); ST = MATS["steel_dark"]                          # turnik
    for sx in (-1.0, 1.0): cyl(.05, 2.6, ST, loc=(sx, 0, 1.3), seg=8, parent=r, name="post")
    tube((-1.0, 0, 2.5), (1.0, 0, 2.5), .025, MATS["steel"], r, "bar", 8); tube((-1.0, 0, 2.0), (1.0, 0, 2.0), .025, MATS["steel"], r, "bar_low", 8)
    merge(r, "bar_mesh"); box((2.2, .3, 2.6), None, loc=(0, 0, 1.3), bev=0, name="pullup_bar-col"); empty("ip_use", (0, -.7, 0), size=.15); empty("ip_hand", (0, 0, 2.5), size=.08); done("pullup_bar")
    pnew(); ST = MATS["steel_dark"]; r = empty("carpet_beater")                                                 # kovrochistka
    for sx in (-1.0, 1.0): box((.08, .08, 2.0), ST, loc=(sx, 0, 1.0), bev=.004, parent=r, name="post")
    tube((-1.0, 0, 1.95), (1.0, 0, 1.95), .03, ST, r, "bar", 8); tube((-1.0, 0, 1.2), (1.0, 0, 1.2), .02, ST, r, "bar_low", 8)
    merge(r, "beater_mesh"); box((2.2, .3, 2.0), None, loc=(0, 0, 1.0), bev=0, name="carpet_beater-col"); empty("ip_use", (0, -.7, 0), size=.15); done("carpet_beater")
    pnew(); ST = MATS["steel_dark"]; r = empty("standpipe")                                                     # kolonka
    cyl(.1, 1.3, MATS["steel_dark"], loc=(0, 0, .65), seg=10, parent=r, name="body"); cyl(.14, .1, MATS["steel_dark"], loc=(0, 0, 1.3), seg=10, parent=r, name="cap")
    tube((0, 0, 1.1), (0, -.3, 1.05), .02, MATS["steel"], r, "spout", 6); beam((.1, 0, 1.2), (.35, 0, 1.0), .03, .02, MATS["steel_dark"], r, "lever", .002); box((.4, .4, .06), MATS["concrete_dark"], loc=(0, -.08, .03), bev=.004, parent=r, name="plinth")
    merge(r, "standpipe_mesh"); box((.4, .4, 1.4), None, loc=(0, 0, .7), bev=0, name="standpipe-col"); empty("ip_use", (0, -.7, 0), size=.15); empty("ip_hand", (.3, 0, 1.0), size=.08); done("standpipe")

def tall_structures():
    pnew(); ST = MATS["steel_dark"]; Y = MATS["paint_yellow"]; r = empty("tower_crane")
    box((.4, .4, 18.0), Y, loc=(0, 0, 9.0), bev=.01, parent=r, name="mast"); box((.9, .9, .6), MATS["concrete_dark"], loc=(0, 0, .3), bev=.01, parent=r, name="base")
    for k in range(18): beam((0, -.2, k), (0, .2, k + 1), .04, .04, ST, r, "mast_brace", 0) if False else None
    jib = empty("jib", (0, 0, 18.3), parent=r, size=.3)
    beam((-3, 0, 0), (14, 0, 0), .35, .5, Y, jib, "jib_arm", .01); beam((-3, 0, .35), (-3, 0, 1.3), .1, .1, ST, jib, "mast_top", 0) if False else None
    box((2.0, .9, .8), MATS["concrete"], loc=(-2.6, 0, -.2), bev=.01, parent=jib, name="counterweight"); box((1.1, 1.3, 1.5), Y, loc=(-.2, 0, -1.0), bev=.01, parent=jib, name="cab")
    tube((12.0, 0, -.1), (12.0, 0, -6.0), .015, ST, jib, "cable", 4); box((.5, .3, .4), ST, loc=(12.0, 0, -6.2), bev=.01, parent=jib, name="hook")
    animate(jib, "slew_loop", [(1, dict(rot=(0, 0, 0))), (97, dict(rot=(0, 0, math.pi))), (193, dict(rot=(0, 0, 2 * math.pi)))])
    box((1.0, 1.0, 18.5), None, loc=(0, 0, 9.2), bev=0, name="tower_crane-col"); empty("ip_use", (2.0, 0, 0), size=.2)
    done("tower_crane", anims=True)
    pnew(); ST = MATS["steel_dark"]; Y = MATS["paint_yellow"]; r = empty("antenna_tower")
    for sx, sy in ((-.4, -.4), (.4, -.4), (-.4, .4), (.4, .4)): beam((sx, sy, 0), (sx * .25, sy * .25, 10), .05, .05, ST, r, "leg", .002)
    for k in range(1, 10):
        z = k; w = .4 * (1 - z / 10 * .75)
        for a, b in (((-w, -w), (w, -w)), ((w, -w), (w, w)), ((w, w), (-w, w)), ((-w, w), (-w, -w))): beam((a[0], a[1], z), (b[0], b[1], z), .03, .03, ST, r, "ring", 0)
    tube((0, 0, 10), (0, 0, 12.5), .03, ST, r, "mast", 6); sphere(.06, MATS["lamp_red"] if "lamp_red" in MATS else ST, loc=(0, 0, 12.55), seg=8, rings=5, parent=r, name="beacon")
    merge(r, "tower_mesh"); box((1.0, 1.0, 12.5), None, loc=(0, 0, 6.2), bev=0, name="antenna_tower-col"); empty("ip_use", (1.2, 0, 0), size=.15); done("antenna_tower")
    pnew(); ST = MATS["steel_dark"]; Y = MATS["paint_yellow"]; r = empty("satellite_dish")
    lathe([(0, 0), (.4, .12), (.55, .22), (.58, .24), (.54, .235), (.38, .12), (0, .02)], MATS["paint_gray"], parent=r, seg=20, name="dish", rot=(math.pi / 2 - .4, 0, 0), loc=(0, 0, .6))
    tube((0, -.1, .15), (0, 0, .55), .03, ST, r, "arm", 6); box((.3, .3, .08), ST, loc=(0, -.1, .05), bev=.01, parent=r, name="base"); tube((0, .0, .6), (0, -.55, .85), .015, ST, r, "feed_arm", 4); sphere(.04, MATS["paint_gray"], loc=(0, -.55, .87), seg=8, rings=5, parent=r, name="lnb")
    merge(r, "dish_mesh"); box((.7, .5, .9), None, loc=(0, -.1, .5), bev=0, name="satellite_dish-col"); done("satellite_dish")
    pnew(); ST = MATS["steel_dark"]; Y = MATS["paint_yellow"]; r = empty("vent_shaft")
    box((1.0, 1.0, .9), MATS["brick"], loc=(0, 0, .45), bev=.01, parent=r, name="shaft"); box((1.2, 1.2, .1), MATS["concrete_dark"], loc=(0, 0, .95), bev=.01, parent=r, name="cap")
    for k in range(6): box((.8, .03, .04), MATS["steel_dark"], loc=(0, -.51, .2 + k * .12), bev=0, parent=r, name="louver")
    box((.5, .5, .4), MATS["paint_gray"], loc=(0, 0, 1.2), bev=.02, parent=r, name="chimney_cap"); merge(r, "vent_mesh"); box((1.2, 1.2, 1.0), None, loc=(0, 0, .5), bev=0, name="vent_shaft-col"); empty("ip_use", (0, -1.0, 0), size=.15); done("vent_shaft")
    pnew(); ST = MATS["steel_dark"]; Y = MATS["paint_yellow"]; r = empty("roof_hatch")
    so = empty("state_ok"); sl = empty("state_loose")
    box((1.0, 1.0, .5), MATS["concrete"], loc=(0, 0, .25), bev=.01, parent=r, name="curb")
    lid = empty("hatch_lid", (0, .5, .5), parent=r, size=.1); box((1.0, 1.0, .06), MATS["steel_dark"], loc=(0, -.5, .03), bev=.006, parent=lid, name="lid"); box((.2, .04, .04), MATS["steel"], loc=(0, -.9, .09), bev=.004, parent=lid, name="handle")
    merge(lid, "lid_mesh")
    animate(lid, "open", [(1, dict(rot=(0, 0, 0))), (16, dict(rot=(1.55, 0, 0)))]); animate(lid, "close", [(1, dict(rot=(1.55, 0, 0))), (16, dict(rot=(0, 0, 0)))])
    merge(r, "hatch_base") if False else None
    box((1.1, 1.1, .55), None, loc=(0, 0, .27), bev=0, name="roof_hatch-col"); empty("ip_use", (0, -1.0, 0), size=.15); empty("ip_hand", (0, -.4, .55), size=.08); done("roof_hatch", anims=True)

def fire_escape():
    pnew(); ST = MATS["steel_dark"]; r = empty("fire_escape")
    # straight flight with landing, one 3 m storey
    for sx in (-.45, .45):
        beam((sx, -.9, 0), (sx, 1.0, 3.0), .06, .04, ST, r, "stringer", .003)
        tube((sx, 1.0, 3.9), (sx, 1.0, 3.0), .02, ST, r, "rail_post", 6)
        beam((sx, -.9, .95), (sx, 1.0, 3.95), .035, .035, ST, r, "handrail", 0)
    for k in range(14): box((.9, .26, .03), ST, loc=(0, -.8 + k * .14, .1 + k * .21), bev=.002, parent=r, name="tread")
    box((1.4, 1.2, .05), ST, loc=(0, 1.6, 3.05), bev=.003, parent=r, name="landing")
    for sx in (-.7, .7): tube((sx, 2.1, 3.05), (sx, 2.1, 4.0), .02, ST, r, "landing_post", 6)
    tube((-.7, 2.1, 4.0), (.7, 2.1, 4.0), .02, ST, r, "landing_rail", 6); tube((-.7, 1.0, 4.0), (-.7, 2.1, 4.0), .02, ST, r, "landing_rail_side", 6); tube((.7, 1.0, 4.0), (.7, 2.1, 4.0), .02, ST, r, "landing_rail_side", 6)
    merge(r, "escape_mesh"); box((1.5, 3.3, 3.1), None, loc=(0, .6, 1.5), bev=0, name="fire_escape-convcol"); empty("ip_use", (0, -1.4, 0), size=.15); empty("ip_hand", (.45, 1.0, 3.5), size=.08); empty("ip_hit", (0, 1.6, 3.05), size=.15)
    done("fire_escape")

def misc():
    pnew(); r = empty("downpipe"); ST = MATS["steel_dark"]
    cyl(.05, 3.6, ST, loc=(0, 0, 1.8), seg=8, parent=r, name="pipe")
    for z in (.4, 1.4, 2.4, 3.4): box((.12, .04, .05), ST, loc=(0, .05, z), bev=0, parent=r, name="clamp")
    tube((0, 0, .15), (0, -.35, .1), .05, ST, r, "elbow", 8); merge(r, "pipe_mesh"); box((.2, .2, 3.6), None, loc=(0, 0, 1.8), bev=0, name="downpipe-col"); done("downpipe")
    pnew(); r = empty("plank_bridge")
    for k in range(5): box((.3, 2.4, .04), MATS["wood"], loc=(-.6 + k * .3, 0, .0), bev=.004, parent=r, name="plank")
    for sx in (-.6, .0, .6): box((.06, 2.4, .05), MATS["wood"], loc=(sx, 0, -.06), bev=.004, parent=r, name="support") if False else None
    box((1.6, .06, .06), MATS["wood"], loc=(0, .8, -.05), bev=.004, parent=r, name="cross"); box((1.6, .06, .06), MATS["wood"], loc=(0, -.8, -.05), bev=.004, parent=r, name="cross")
    merge(r, "planks"); box((1.6, 2.5, .1), None, loc=(0, 0, 0), bev=0, name="plank_bridge-convcol"); empty("ip_use", (0, -1.4, 0), size=.15); done("plank_bridge")
    pnew(); r = empty("crate_stack"); W_ = MATS["wood"]
    for i, (x, y, z, rz) in enumerate(((0, 0, .25, 0), (.62, 0, .25, .1), (.3, .02, .75, .05), (-.55, .7, .25, .4))):
        c = empty("crate", (x, y, z), parent=r, size=.05); c.rotation_euler = (0, 0, rz)
        box((.55, .55, .5), W_, loc=(0, 0, 0), bev=.006, parent=c, name="crate_box")
        for sx in (-.27, .27):
            for sy in (-.27, .27): box((.04, .04, .52), MATS["wood"], loc=(sx, sy, 0), bev=0, parent=c, name="crate_post")
        for zz in (-.15, .15): box((.57, .57, .03), MATS["steel_dark"], loc=(0, 0, zz), bev=0, parent=c, name="crate_band")
    merge(r, "crates_mesh"); box((1.6, 1.4, 1.0), None, loc=(.1, .2, .5), bev=0, name="crate_stack-convcol"); empty("ip_hand", (.3, 0, 1.0), size=.08); done("crate_stack")
    pnew(); r = empty("laundry_line"); ST = MATS["steel_dark"]
    for sx in (-1.8, 1.8): cyl(.03, 2.0, ST, loc=(sx, 0, 1.0), seg=8, parent=r, name="post")
    tube((-1.8, 0, 1.95), (1.8, 0, 1.85), .006, MATS["steel"], r, "rope", 4)
    for k, (c_, w, h) in enumerate(((.45, .5, .8), (.25, .6, .5), (.5, .45, .7), (.3, .55, .45))):
        cm = mat(f"cloth_{k}", (c_, c_ * .8, c_ * .6), .95); box((w, .02, h), cm, loc=(-1.3 + k * .85, 0, 1.85 - h / 2 - .02 + .0), bev=.004, parent=r, name="cloth")
    merge(r, "line_mesh"); box((3.8, .3, 2.0), None, loc=(0, 0, 1.0), bev=0, name="laundry_line-col"); done("laundry_line")
    pnew(); r = empty("shop_sign")
    box((1.6, .08, .5), MATS["sign_blue"], loc=(0, 0, 0), bev=.01, parent=r, name="board"); box((1.4, .02, .12), MATS["sign_white"], loc=(0, -.05, .06), bev=0, parent=r, name="text_a"); box((1.0, .02, .08), MATS["sign_white"], loc=(-.1, -.05, -.1), bev=0, parent=r, name="text_b")
    for sx in (-.7, .7): tube((sx, 0, .25), (sx, .3, .55), .015, MATS["steel_dark"], r, "bracket", 6)
    merge(r, "sign_mesh"); done("shop_sign")

for k in ("birch", "poplar", "maple", "bare"): tree(k)
bush(0); bush(1); fences(); garages(); transformer_booth(); kiosk(); playground(); yard_small(); tall_structures(); fire_escape(); misc()
