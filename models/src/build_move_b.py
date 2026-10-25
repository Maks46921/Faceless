"""Stage 8, group B: balconies, ditches and cover, heating pipes, vents and antennas, crawl holes, glass roofs, projectiles.
Run: GRP=<balcony|ditch|pipes|vents|holes|glass|proj|all> D:\\Cosmoteer\\blender.exe -b -P build_move_b.py -> models/movement/<topic>/*.glb"""
import os
_a = open("D:/Faceless/models/src/build_move_a.py", encoding="utf-8").read()
exec(_a[:_a.index("GRP = os.environ.get")])
FH = 2.8
def card(name, w, h, material, flare=1.0, uvs=((0, 0), (1, 0), (1, 1), (0, 1))):
    bm = bmesh.new(); uv = bm.loops.layers.uv.new("UVMap")
    vs = [bm.verts.new((-w / 2, 0, 0)), bm.verts.new((w / 2, 0, 0)), bm.verts.new((w / 2 * flare, 0, h)), bm.verts.new((-w / 2 * flare, 0, h))]
    f = bm.faces.new(vs)
    for l, uvv in zip(f.loops, uvs): l[uv].uv = uvv
    return mesh_obj(name, bm, material, smooth=False)

def wall_stub(root, w=3.0, brick=False, door=True, h=FH, z0=0.0):
    wm = MATS["brick_wall"] if brick else MATS["panel_wall"]
    box((w, .3, h), wm, loc=(0, .15, z0 + h / 2), bev=0, parent=root, name="wall")
    if door: box((.9, .06, 2.1), MATS["wood"], loc=(0, -.015, z0 + 1.05), bev=0, parent=root, name="door_closed_panel")
    mount = empty("mount_facade", (0, 0, z0), parent=root, size=.2)

def slab_and_rail(root, w, d, style="panel", glazed=False, brick=False):
    box((w, d, .16), MATS["balcony_slab"], loc=(0, -d / 2, -.08), bev=0, parent=root, name="slab")
    if style == "panel":
        box((w, .06, 1.05), MATS["panel_wall"], loc=(0, -d + .03, .525), bev=0, parent=root, name="rail_front")
        for sx in (-w / 2 + .03, w / 2 - .03): box((.06, d, 1.05), MATS["panel_wall"], loc=(sx, -d / 2, .525), bev=0, parent=root, name="rail_side")
    elif style == "brick":
        box((w, .12, 1.05), MATS["brick_wall"], loc=(0, -d + .06, .525), bev=0, parent=root, name="rail_front")
        for sx in (-w / 2 + .06, w / 2 - .06): box((.12, d, 1.05), MATS["brick_wall"], loc=(sx, -d / 2, .525), bev=0, parent=root, name="rail_side")
    elif style == "bars":
        for sx in (-w / 2 + .03, w / 2 - .03): box((.05, d, .05), MATS["balcony_rail"], loc=(sx, -d / 2, 1.03), bev=0, parent=root, name="rail_top_side")
        box((w, .05, .05), MATS["balcony_rail"], loc=(0, -d + .03, 1.03), bev=0, parent=root, name="rail_top")
        n = int(w / .12)
        for i in range(n): box((.025, .025, 1.0), MATS["balcony_rail"], loc=(-w / 2 + .06 + i * .12, -d + .03, .5), bev=0, parent=root, name="bar")
        for k in range(int(d / .12)):
            for sx in (-w / 2 + .03, w / 2 - .03): box((.025, .025, 1.0), MATS["balcony_rail"], loc=(sx, -.06 - k * .12, .5), bev=0, parent=root, name="bar_side")
    if glazed:
        for z in (1.1,): box((w, .04, 1.4), MATS["loggia_glass"], loc=(0, -d + .02, 1.1 + .7), bev=0, parent=root, name="glass_front")
        for sx in (-w / 2, w / 2): box((.04, d, 1.4), MATS["loggia_glass"], loc=(sx, -d / 2, 1.1 + .7), bev=0, parent=root, name="glass_side")
        box((w, d, .08), MATS["balcony_slab"], loc=(0, -d / 2, 2.55), bev=0, parent=root, name="loggia_roof")

def balcony(name, w=2.7, d=1.1, style="panel", brick=False, glazed=False, extra=None, door_states=False, anims=None):
    out("balconies"); mnew(); root = empty("balcony")
    wall_stub(root, w + .4, brick, door=not door_states)
    slab_and_rail(root, w, d, style, glazed)
    if extra: extra(root, w, d)
    merge(root, "balcony_mesh") if extra is None and not door_states else None
    box((w, d, .2), None, loc=(0, -d / 2, -.1), bev=0, name=name + "-col")
    empty("ip_use", (0, -d / 2, .02), size=.15); empty("ip_hand", (0, -d, 1.05), size=.08); empty("ip_hit", (0, -d - .8, -2.7), size=.15)
    done(name, anims=bool(anims))
def junk(root, w, d):
    bike = empty("bicycle", (-.6 * w / 2, -.6, .0), parent=root, size=.1)
    for x in (-.45, .45): cyl(.34, .03, MATS["rubber"], loc=(x, 0, .34), seg=14, rot=(0, math.pi / 2, math.pi / 2), parent=bike, name="wheel").rotation_euler = (math.pi / 2, 0, 0)
    beam((-.45, 0, .34), (0, 0, .6), .03, .03, MATS["steel_dark"], bike, "frame", 0); beam((0, 0, .6), (.45, 0, .34), .03, .03, MATS["steel_dark"], bike, "frame2", 0); beam((-.45, 0, .34), (.0, 0, .34), .03, .03, MATS["steel_dark"], bike, "frame3", 0)
    box((.4, .05, .06), MATS["steel_dark"], loc=(.4, 0, .75), bev=0, parent=bike, name="handlebar")
    for k, (x, y, z, s_) in enumerate(((.7, -.4, .0, .45), (.7, -.4, .45, .4), (.35, -.8, .0, .5), (-.2, -.85, .0, .4))): box((s_, s_, s_), MATS["cardboard"], loc=(x, y, z + s_ / 2), bev=.01, parent=root, name="cardboard_box")
    box((.6, .6, 1.5), mat("fridge_white", (.45, .45, .42), .5), loc=(-.9, -.4, .75), bev=.02, parent=root, name="old_fridge"); box((.02, .04, .5), MATS["steel"], loc=(-.6, -.7, 1.0), bev=0, parent=root, name="fridge_handle")
    for k in range(3): beam((.9 + k * .05, -1.0, .0), (.95 + k * .05, -1.0, 1.7), .035, .02, mat("ski_blue", (.1, .2, .4), .6), root, "ski", 0)
def laundry(root, w, d):
    for sx in (-w / 2 + .05, w / 2 - .05): tube((sx, -d + .1, .9), (sx, -d + .1, 2.4), .015, MATS["steel_dark"], root, "line_post", 5) if False else None
    tube((-w / 2 + .1, -d + .15, 2.35), (w / 2 - .1, -d + .15, 2.3), .006, MATS["steel"], root, "rope", 4); tube((-w / 2 + .1, -d + .6, 2.35), (w / 2 - .1, -d + .6, 2.3), .006, MATS["steel"], root, "rope2", 4)
    for k, c_ in enumerate((.45, .2, .5, .3, .38)):
        cm = mat(f"cloth{k}", (c_, c_ * .8, c_ * .7), .95); box((.4 + .05 * (k % 2), .02, .6), cm, loc=(-w / 2 + .35 + k * (w - .5) / 5, -d + .15, 2.0), bev=0, parent=root, name="cloth")
    for k in range(3):                                         # drying rack
        beam((.3 + k * .12, -.4, 0), (.3 + k * .12, -.4, 1.0), .02, .02, MATS["steel"], root, "rack_leg", 0)
    box((.6, .5, .03), MATS["steel"], loc=(.4, -.4, 1.0), bev=0, parent=root, name="rack_top")
    for k in range(4): box((.35, .02, .5), mat(f"cloth_r{k}", (.35, .3 + k * .05, .2), .95), loc=(.4, -.4 + (k - 1.5) * .09, .75), bev=0, parent=root, name="rack_cloth")
def flowers(root, w, d):
    for k, x in enumerate((-.9, 0, .9)):
        pot = empty(f"flowerpot_{k}", (x, -d + .17, 1.05), parent=root, size=.08)
        lathe([(0, 0), (.11, 0), (.15, .22), (0, .22)], mat("pot_clay", (.3, .12, .06), .9), parent=pot, seg=10, name="pot"); sphere(.14, mat("flower_green", (.1, .2, .06), .9), loc=(0, 0, .3), seg=8, rings=5, parent=pot, name="leaves", scale=(1, 1, .8))
        sphere(.04, mat(f"flower_{k}", (.5, .1 + .1 * k, .1), .8), loc=(.03, 0, .42), seg=6, rings=4, parent=pot, name="bloom")
        animate(pot, "fall", [(1, dict(loc=(x, -d + .17, 1.05), rot=(0, 0, 0))), (8, dict(loc=(x, -d - .1, .6), rot=(.4, 0, .6))), (20, dict(loc=(x + .1, -d - .5, -1.4), rot=(1.8, 0, 2.0))), (34, dict(loc=(x + .15, -d - .7, -2.7), rot=(3.0, 0, 3.0)))])
def balconies():
    balcony("balcony_open_panel", 2.7, 1.1, "panel"); balcony("balcony_open_brick", 2.7, 1.1, "brick", True); balcony("balcony_bars", 2.4, 1.0, "bars")
    balcony("balcony_glazed", 2.7, 1.1, "panel", glazed=True); balcony("balcony_junk", 3.0, 1.2, "panel", extra=junk); balcony("balcony_laundry", 3.0, 1.2, "bars", extra=laundry)
    balcony("balcony_flowers", 2.7, 1.1, "bars", extra=flowers, anims=True)
    # door / window states
    out("balconies"); mnew(); root = empty("door_set"); w = 3.0
    box((.15, .3, 2.2), MATS["paint_gray"], loc=(-.5, .15, 1.1), bev=0, parent=root, name="jamb_l"); box((.15, .3, 2.2), MATS["paint_gray"], loc=(.5, .15, 1.1), bev=0, parent=root, name="jamb_r"); box((1.15, .3, .12), MATS["paint_gray"], loc=(0, .15, 2.16), bev=0, parent=root, name="head")
    merge(root, "frame_mesh")
    def leaf(nm, parent, ang, broken=False):
        h = empty(nm, (-.42, 0, 1.02), parent=parent, size=.05); h.rotation_euler = (0, 0, ang)
        box((.84, .05, 2.05), MATS["wood"], loc=(.42, 0, 0), bev=.005, parent=h, name="leaf")
        gl = box((.6, .02, 1.1), MATS["building_window"] if not broken else MATS["building_window"], loc=(.42, -.03, .35), bev=0, parent=h, name="glass")
        if broken:
            for k in range(4): box((.12, .02, .2), MATS["building_window"], loc=(.2 + k * .12, -.03, .8 - k * .22), bev=0, parent=h, name="shard_hang").rotation_euler = (0, .6 * k, 0)
        box((.1, .03, .03), MATS["steel"], loc=(.76, -.05, -.05), bev=0, parent=h, name="handle")
        merge(h, nm + "_mesh"); return h
    leaf("door_closed", empty("state_ok"), 0.0); leaf("door_open", empty("state_loose"), 1.6); leaf("door_broken", empty("state_broken"), .5, True)
    ld = leaf("door_anim", None, 0.0); animate(ld, "open", [(1, dict(rot=(0, 0, 0))), (18, dict(rot=(0, 0, 1.6)))]); animate(ld, "close", [(1, dict(rot=(0, 0, 1.6))), (16, dict(rot=(0, 0, .1))), (18, dict(rot=(0, 0, 0)))])
    box((1.2, .3, 2.2), None, loc=(0, .1, 1.1), bev=0, name="balcony_door-col"); empty("ip_use", (0, -.8, 0), size=.15); empty("ip_hand", (.3, -.06, 1.0), size=.08); done("balcony_door", anims=True)
    # dangerous balcony (flat 12): ok / loose / broken + collapse
    out("balconies"); mnew(); root = empty("danger_balcony"); w, d = 2.7, 1.1
    wall_stub(root, w + .4, False, True)
    so = empty("state_ok"); slab_and_rail(so, w, d, "bars"); sl = empty("state_loose")
    pv = empty("slab_pivot", (0, 0, 0), parent=sl); pv.rotation_euler = (-.1, 0, .03)
    box((w, d, .16), MATS["balcony_slab"], loc=(0, -d / 2, -.08), bev=0, parent=pv, name="slab")
    for k in range(8): box((.4, .015, .01), MATS["soot"], loc=(-1.0 + k * .28, -d + .2 - (k % 3) * .3, .005), bev=0, parent=pv, name="crack").rotation_euler = (0, 0, .5 * (k % 2))
    for sx in (-w / 2 + .03, w / 2 - .03): box((.05, d, .05), MATS["balcony_rail"], loc=(sx, -d / 2, 1.03), bev=0, parent=pv, name="rail_top_side")
    box((w, .05, .05), MATS["balcony_rail"], loc=(0, -d + .03, 1.03), bev=0, parent=pv, name="rail_top")
    for i in range(int(w / .12)): box((.025, .025, 1.0), MATS["balcony_rail"], loc=(-w / 2 + .06 + i * .12, -d + .03, .5), bev=0, parent=pv, name="bar")
    for sx in (-.9, .9): box((.1, .2, .06), MATS["rusty"], loc=(sx, -.1, -.19), bev=0, parent=sl, name="bracket_rusty")
    sb = empty("state_broken")
    box((w * .45, d * .6, .16), MATS["balcony_slab"], loc=(-.8, -d * .3, -.08), bev=0, parent=sb, name="slab_stub").rotation_euler = (-.5, 0, 0)
    for k in range(5): beam((-.9 + k * .35, -.2, -.1), (-.85 + k * .35, -.6, -.5), .015, .015, MATS["rebar_rust"], sb, "rebar", 0)
    for sx in (-.9, .9): box((.1, .2, .06), MATS["rusty"], loc=(sx, -.1, -.19), bev=0, parent=sb, name="bracket_rusty")
    fall = empty("slab_fall", (0, 0, 0), size=.2); box((w, d, .16), MATS["balcony_slab"], loc=(0, -d / 2, -.08), bev=0, parent=fall, name="slab"); box((w, .05, 1.0), MATS["balcony_rail"], loc=(0, -d + .03, .5), bev=0, parent=fall, name="rail")
    animate(fall, "collapse", [(1, dict(loc=(0, 0, 0), rot=(0, 0, 0))), (6, dict(loc=(0, -.05, -.08), rot=(-.18, 0, .04))), (14, dict(loc=(.0, -.4, -1.4), rot=(-.9, 0, .1))), (24, dict(loc=(.05, -1.0, -2.65), rot=(-1.4, 0, .2))), (30, dict(loc=(.05, -1.2, -2.7), rot=(-1.45, 0, .25)))])
    deb = empty("debris", (0, 0, -2.75), size=.1)
    rnd = random.Random(1)
    for i in range(9): rock_blob(.12 + .1 * rnd.random(), MATS["concrete"], seed=80 + i, loc=(rnd.uniform(-1.0, 1.0), rnd.uniform(-2.2, -.8), .0), flat=.6, subdiv=1, rough=.3, parent=deb, name="chunk")
    box((w, d, .2), None, loc=(0, -d / 2, -.1), bev=0, name="danger_balcony-col"); empty("ip_use", (0, -d / 2, .02), size=.15); empty("ip_hand", (0, -d, 1.05), size=.08); empty("ip_hit", (0, -d - .8, -2.7), size=.15)
    done("balcony_danger", anims=True)

# ============================================================== ditches, bushes, decals
def ditches():
    out("terrain")
    for nm, w in (("ditch_2m", 2.0), ("ditch_3m", 3.0)):
        mnew(); r = empty("ditch"); earth = mat("earth", (.14, .1, .06), 1.0)
        for sy in (-1, 1): beam((0, sy * (w / 2 + .3), .0), (0, sy * (w / 2 - .05), -.8), 5.0, .3, earth, r, "bank", 0) if False else None
        for sy in (-1, 1):
            bm = bmesh.new(); vs = [bm.verts.new(p) for p in ((-2.5, sy * (w / 2 + 1.2), 0), (2.5, sy * (w / 2 + 1.2), 0), (2.5, sy * (w / 2), -.8), (-2.5, sy * (w / 2), -.8))]; f = bm.faces.new(vs if sy > 0 else vs[::-1]); f.normal_update()
            mesh_obj("bank", bm, earth, parent=r, smooth=False)
        bm = bmesh.new(); vs = [bm.verts.new(p) for p in ((-2.5, -w / 2, -.8), (2.5, -w / 2, -.8), (2.5, w / 2, -.8), (-2.5, w / 2, -.8))]; bm.faces.new(vs[::-1]); mesh_obj("bed", bm, earth, parent=r, smooth=False)
        bm = bmesh.new(); vs = [bm.verts.new(p) for p in ((-2.5, -w / 2 + .1, -.55), (2.5, -w / 2 + .1, -.55), (2.5, w / 2 - .1, -.55), (-2.5, w / 2 - .1, -.55))]; f = bm.faces.new(vs); f.normal_update()
        if f.normal.z < 0: f.normal_flip()
        mesh_obj("water", bm, MATS["water"], parent=r, smooth=False)
        for k in range(int(w / .55)): rock_blob(.22, MATS["stone"], seed=90 + k, loc=(-1.0 + (k % 2) * .8, -w / 2 + .35 + k * .5, -.52), flat=.55, subdiv=1, rough=.2, parent=r, name="stepping_stone")
        merge(r, "ditch_mesh") if False else None
        box((5.0, w + 2.4, .1), None, loc=(0, 0, -.05), bev=0, name=nm + "-col"); empty("ip_use", (0, -w / 2 - .8, 0), size=.15); empty("ip_hit", (0, 0, -.55), size=.15); done(nm)
    mnew(); r = empty("plank_over_ditch"); Wd = MATS["wood"]
    so = empty("state_ok"); box((.3, 3.2, .05), Wd, loc=(0, 0, .02), bev=.004, parent=so, name="plank"); box((.3, .05, .1), Wd, loc=(0, 1.55, -.02), bev=0, parent=so, name="cleat")
    sl = empty("state_loose"); box((.3, 3.2, .05), Wd, loc=(.9, .8, -.2), bev=.004, parent=sl, name="plank_dropped").rotation_euler = (.6, 0, .4)
    box((.3, 3.2, .1), None, loc=(0, 0, 0), bev=0, name="plank_over_ditch-convcol"); empty("ip_use", (0, -1.9, 0), size=.15); empty("ip_hand", (0, -1.4, .05), size=.08); done("plank_over_ditch")
    for kind, seed in (("bush_dense_a", 3), ("bush_dense_b", 7), ("tall_grass", 11)):
        mnew(); r = empty("bush"); rnd = random.Random(seed)
        if kind == "tall_grass":
            gm = mat("grass", (.14, .2, .06), .95)
            for i in range(60):
                x, y = rnd.uniform(-.9, .9), rnd.uniform(-.7, .7); beam((x, y, 0), (x + rnd.uniform(-.2, .2), y + rnd.uniform(-.2, .2), rnd.uniform(.8, 1.3)), .04, .01, gm, r, "blade", 0)
        else:
            gm = mat("foliage", (.1, .2, .07) if seed == 3 else (.18, .22, .06), .85)
            for i in range(14): rock_blob(.32 + .14 * rnd.random(), gm, seed=seed * 10 + i, loc=(rnd.uniform(-.9, .9), rnd.uniform(-.7, .7), .4 + rnd.uniform(0, .5)), flat=.9, subdiv=1, rough=.3, parent=r, name="clump")
        merge(r, "bush_mesh"); box((2.0, 1.6, 1.3), None, loc=(0, 0, .65), bev=0, name=kind + "-convcol"); empty("ip_use", (0, -1.2, 0), size=.12); empty("ip_hand", (0, -.8, 1.0), size=.08); done(kind)
    # mud ruts + wet footprints decals
    mnew(); mud = mat("decal_mud", (.09, .06, .035), .9)
    bm = bmesh.new(); uv = bm.loops.layers.uv.new("UVMap")
    for sx in (-.35, .35):
        for i in range(10):
            y0, y1 = -2.0 + i * .4, -1.6 + i * .4; x0 = sx + .02 * math.sin(i * 1.3); x1 = sx + .02 * math.sin((i + 1) * 1.3)
            f = bm.faces.new([bm.verts.new((x0 - .1, y0, .003)), bm.verts.new((x0 + .1, y0, .003)), bm.verts.new((x1 + .1, y1, .003)), bm.verts.new((x1 - .1, y1, .003))])
            for l, u in zip(f.loops, ((0, i / 10), (1, i / 10), (1, (i + 1) / 10), (0, (i + 1) / 10))): l[uv].uv = u
    mesh_obj("ruts", bm, mud, smooth=False); empty("ip_hit", (0, 0, 0), size=.1); done("decal_mud_ruts")
    mnew(); wet = mat("decal_wet_print", (.05, .07, .09), .1)
    bm = bmesh.new(); uv = bm.loops.layers.uv.new("UVMap")
    for i in range(8):
        x = .12 if i % 2 else -.12; y = -1.6 + i * .45
        for dx, dy, r_ in ((0, 0, 1.0), (0, -.18, .7)):
            c = Vector((x + dx, y + dy, .003)); vs = [bm.verts.new((c.x + math.cos(t) * .06 * r_, c.y + math.sin(t) * .09 * r_, .003)) for t in [k * 2 * math.pi / 8 for k in range(8)]]; f = bm.faces.new(vs)
            for l in f.loops: l[uv].uv = ((l.vert.co.x + .3) / .6, (l.vert.co.y + 2) / 4)
    mesh_obj("prints", bm, wet, smooth=False); empty("ip_hit", (0, 0, 0), size=.1); done("decal_wet_prints")
    mnew(); r = empty("park_gate"); ST = MATS["steel_dark"]
    for sx in (-1.8, 1.8): box((.4, .4, 3.0), MATS["concrete"], loc=(sx, 0, 1.5), bev=.01, parent=r, name="pillar"); sphere(.22, MATS["concrete_dark"], loc=(sx, 0, 3.15), seg=10, rings=6, parent=r, name="finial")
    for sd, s_ in (("l", -1), ("r", 1)):
        hg = empty("leaf_" + sd, (s_ * 1.6, 0, 0), parent=r)
        for z in (.3, 2.1): box((1.4, .05, .07), ST, loc=(-s_ * .7, 0, z), bev=0, parent=hg, name="rail")
        for i in range(10): x = -s_ * (.1 + i * .14); box((.03, .03, 2.0), ST, loc=(x, 0, 1.15), bev=0, parent=hg, name="bar"); cyl(.025, .14, ST, loc=(x, 0, 2.25), seg=4, r2=.001, parent=hg, name="spear")
        merge(hg, "leaf_mesh_" + sd); animate(hg, "open", [(1, dict(rot=(0, 0, 0))), (26, dict(rot=(0, 0, s_ * 1.5)))]) if False else None
    merge(r, "park_gate_frame") if False else None
    box((4.0, .4, 3.0), None, loc=(0, 0, 1.5), bev=0, name="park_gate-col"); empty("ip_use", (0, -1.0, 0), size=.15); empty("ip_hand", (-1.0, -.05, 2.0), size=.08); done("park_gate", anims=False)

# ============================================================== heating pipes
def pipes():
    out("pipes")
    def pipe_body(parent, p0, p1, r=.3):
        tube(p0, p1, r, mat("pipe_foil", (.4, .42, .42), .55, .6), parent, "pipe", 14)
        L_ = (Vector(p1) - Vector(p0)).length; n = int(L_ / 1.0)
        for k in range(1, n):
            q = Vector(p0).lerp(Vector(p1), k / n); cyl(r + .012, .06, MATS["steel_dark"], loc=tuple(q), seg=14, parent=parent, name="clamp").rotation_euler = (0, math.pi / 2 if abs(p1[0] - p0[0]) > 1 else 0, math.pi / 2 if abs(p1[1] - p0[1]) > 1 else 0)
    def support(parent, x, y, h, r=.3):
        for sx in (-1, 1): beam((x + sx * .35, y, 0), (x + sx * .35, y, h - r), .12, .12, MATS["concrete"], parent, "support_leg", 0)
        box((1.1, .3, .15), MATS["concrete_dark"], loc=(x, y, h - r - .08), bev=0, parent=parent, name="support_beam")
    mnew(); r = empty("heating_pipe_6m"); pipe_body(r, (-3, 0, 2.5), (3, 0, 2.5))
    for x in (-2.8, 0, 2.8):
        for sy in (-1, 1): beam((x, sy * .3, 0), (x, sy * .3, 2.15), .15, .15, MATS["concrete"], r, "support_leg", 0)
        box((.2, .85, .15), MATS["concrete_dark"], loc=(x, 0, 2.15), bev=0, parent=r, name="support_beam")
    for k in range(2): box((.1, .6, .01), MATS["steel_dark"], loc=(-1 + k * 2, 0, 2.81), bev=0, parent=r, name="patch")
    for k in range(4): box((.5, .6, .06), MATS["concrete"], loc=(-3.4, 0, .03 + k * .17), bev=0, parent=r, name="step") if False else None
    merge(r, "pipe_mesh")
    # step stool
    stp = empty("step_up", (-3.6, 0, 0), parent=r) if False else None
    box((6.0, .8, .8), None, loc=(0, 0, 2.5), bev=0, name="heating_pipe_6m-convcol"); empty("ip_use", (0, 0, 2.82), size=.12); empty("ip_hand", (0, -.3, 2.6), size=.08); empty("ip_hit", (0, 0, 0), size=.1); done("heating_pipe_6m")
    mnew(); r = empty("heating_pipe_corner"); pipe_body(r, (-3, 0, 2.5), (0, 0, 2.5)); pipe_body(r, (0, 0, 2.5), (0, 3, 2.5)); sphere(.35, mat("pipe_foil", (.4, .42, .42), .55, .6), loc=(0, 0, 2.5), seg=14, rings=8, parent=r, name="elbow")
    for p in ((-2.6, 0), (0, 2.6)):
        for sy in (-1, 1): beam((p[0] + (sy * .3 if p[1] == 0 else 0), p[1] + (sy * .3 if p[0] == 0 else 0), 0), (p[0] + (sy * .3 if p[1] == 0 else 0), p[1] + (sy * .3 if p[0] == 0 else 0), 2.15), .15, .15, MATS["concrete"], r, "support_leg", 0)
    merge(r, "corner_mesh"); box((3.8, 3.8, .8), None, loc=(-1.5, 1.5, 2.5), bev=0, name="heating_pipe_corner-convcol"); empty("ip_use", (0, 0, 2.85), size=.12); empty("ip_hand", (0, -.35, 2.6), size=.08); done("heating_pipe_corner")
    mnew(); r = empty("pipe_compensator"); pm = mat("pipe_foil", (.4, .42, .42), .55, .6)                 # pi-shaped span over a road, 11 m wide, 5 m high
    for sx in (-5.5, 5.5):
        for sy in (-.3, .3): beam((sx, sy, 0), (sx, sy, 4.5), .3, .3, MATS["concrete"], r, "pylon", 0)
        box((1.0, 1.0, .25), MATS["concrete_dark"], loc=(sx, 0, 4.6), bev=0, parent=r, name="saddle")
    tube((-8, 0, 5.0), (-5.5, 0, 5.0), .3, pm, r, "pipe_in", 14); tube((-5.5, 0, 5.0), (5.5, 0, 5.0), .3, pm, r, "pipe_span", 14); tube((5.5, 0, 5.0), (8, 0, 5.0), .3, pm, r, "pipe_out", 14)
    for sx in (-3.5, 3.5): tube((sx, 0, 5.0), (sx, 0, 6.0), .3, pm, r, "loop_up", 14);
    tube((-3.5, 0, 6.0), (3.5, 0, 6.0), .3, pm, r, "loop_top", 14)
    for k in range(-5, 6): beam((k * 1.0, -.35, 5.0), (k * 1.0, .35, 5.0), .08, .02, MATS["steel_dark"], r, "hanger", 0) if False else None
    for k in range(12): cyl(.31, .06, MATS["steel_dark"], loc=(-5 + k * .9, 0, 5.0), seg=14, rot=(0, math.pi / 2, 0), parent=r, name="clamp")
    # service ladder at one pylon
    for k in range(14): box((.5, .04, .04), MATS["steel"], loc=(-5.5, -.5, .3 + k * .32), bev=0, parent=r, name="rung")
    merge(r, "compensator_mesh"); box((16, .8, 1.2), None, loc=(0, 0, 5.3), bev=0, name="pipe_compensator-col"); empty("ip_use", (-5.5, -.9, 0), size=.15); empty("ip_hand", (-5.5, -.5, 1.5), size=.08); empty("ip_hit", (0, 0, 0), size=.15); done("pipe_compensator")
    mnew(); r = empty("heating_pipe_burst"); pm = mat("pipe_foil", (.4, .42, .42), .55, .6)
    so = empty("state_ok"); tube((-3, 0, 2.5), (3, 0, 2.5), .3, pm, so, "pipe", 14)
    sl = empty("state_loose"); tube((-3, 0, 2.5), (-.4, 0, 2.5), .3, pm, sl, "pipe_a", 14); tube((.4, 0, 2.5), (3, 0, 2.5), .3, pm, sl, "pipe_b", 14)
    for k in range(6): beam((-.4 + k * .16, .0, 2.5 + .25), (-.2 + k * .16, 0, 2.9), .08, .01, MATS["rusty"], sl, "torn_foil", 0)
    steam = empty("steam", (0, 0, 2.7), parent=sl)
    for k in range(5):
        c = card(f"steam_card_{k}", .9 + k * .12, 1.2 + k * .5, mat("vfx_steam", (.8, .8, .82), 1.0, 0.0, emit=(.8, .8, .82), emit_strength=.4), 1.5 + k * .1); c.rotation_euler = (0, 0, k * 1.0); c.location = (0, 0, k * .15); c.parent = steam
    animate(steam, "steam_loop", [(1, dict(scale=(1, 1, 1))), (13, dict(scale=(1.2, 1.2, 1.4))), (25, dict(scale=(1, 1, 1)))])
    for sx in (-2.8, 0, 2.8):
        for sy in (-1, 1): beam((sx, sy * .3, 0), (sx, sy * .3, 2.15), .15, .15, MATS["concrete"], r, "support_leg", 0)
    box((6.0, .8, .8), None, loc=(0, 0, 2.5), bev=0, name="heating_pipe_burst-convcol"); empty("ip_spark", (0, 0, 2.8), size=.15); empty("ip_use", (0, 0, 2.82), size=.12); empty("ip_hand", (0, -.3, 2.6), size=.08); done("heating_pipe_burst", anims=True)

# ============================================================== vents and antenna
def vents():
    out("vents"); ST = None
    for nm, state in (("vent_hatch_roof", "hatch"),):
        mnew(); ST = MATS["steel_dark"]; r = empty("vent_hatch")
        box((.8, .8, .2), MATS["concrete"], loc=(0, 0, .1), bev=0, parent=r, name="curb")
        so = empty("state_ok"); gr = box((.6, .6, .03), ST, loc=(0, 0, .215), bev=0, parent=so, name="grille_plate")
        for i in range(5): box((.02, .6, .03), ST, loc=(-.24 + i * .12, 0, .24), bev=0, parent=so, name="grille_bar")
        for sx in (-.27, .27):
            for sy in (-.27, .27): cyl(.022, .02, MATS["steel"], loc=(sx, sy, .25), seg=6, parent=so, name="screw")
        sl = empty("state_loose"); lid = empty("grille_open", (0, .3, .215), parent=sl, size=.1); lid.rotation_euler = (-1.7, 0, 0)
        box((.6, .6, .03), ST, loc=(0, -.3, 0), bev=0, parent=lid, name="grille_plate")
        for i in range(5): box((.02, .6, .03), ST, loc=(-.24 + i * .12, -.3, .03), bev=0, parent=lid, name="grille_bar")
        box((.54, .54, .04), MATS["soot"], loc=(0, 0, .2), bev=0, parent=sl, name="shaft_dark")
        ga = empty("grille_anim", (0, .3, .215), size=.1); box((.6, .6, .03), ST, loc=(0, -.3, 0), bev=0, parent=ga, name="grille_plate")
        animate(ga, "open", [(1, dict(rot=(0, 0, 0))), (12, dict(rot=(-1.7, 0, 0)))]); animate(ga, "close", [(1, dict(rot=(-1.7, 0, 0))), (12, dict(rot=(0, 0, 0)))])
        box((.8, .8, .25), None, loc=(0, 0, .12), bev=0, name="vent_hatch-col"); empty("ip_use", (0, -.6, .2), size=.12); empty("ip_hand", (0, .3, .22), size=.06); done(nm, anims=True)
    mnew(); ST = MATS["steel_dark"]; r = empty("vent_shaft_ladder"); H = 4.5                           # shaft interior with staples each 0.3 m, open front for readability
    for sx in (-.4, .4): box((.1, .8, H), MATS["concrete"], loc=(sx, 0, H / 2), bev=0, parent=r, name="wall_side")
    box((.9, .1, H), MATS["concrete"], loc=(0, .4, H / 2), bev=0, parent=r, name="wall_back")
    for k in range(int(H / .3)): box((.3, .04, .03), ST, loc=(0, .32, .3 + k * .3), bev=0, parent=r, name="staple"); [box((.03, .12, .03), ST, loc=(sx, .35, .3 + k * .3), bev=0, parent=r, name="staple_leg") for sx in (-.15, .15)]
    box((.9, .8, .1), MATS["concrete_dark"], loc=(0, 0, .05), bev=0, parent=r, name="floor")
    merge(r, "shaft_mesh"); box((.9, .8, H), None, loc=(0, 0, H / 2), bev=0, name="vent_shaft_ladder-convcol"); empty("ip_use", (0, .0, .1), size=.12); empty("ip_hand", (0, .32, 1.2), size=.06); done("vent_shaft_ladder")
    mnew(); ST = MATS["steel_dark"]; r = empty("stairwell_grille")
    so = empty("state_ok"); sl = empty("state_loose")
    for parent, ang in ((so, 0.0), (sl, 1.5)):
        for sx in (-.55, .55): box((.06, .06, 2.4), ST, loc=(sx, 0, 1.2), bev=0, parent=so if parent is so else sl, name="post") if parent is so else None
    for sx in (-.55, .55): box((.06, .06, 2.4), ST, loc=(sx, 0, 1.2), bev=0, parent=sl, name="post")
    def grille(nm, parent, ang):
        hg = empty(nm, (-.5, 0, 0), parent=parent); hg.rotation_euler = (0, 0, ang)
        for z in (.1, 1.2, 2.3): box((1.0, .04, .06), ST, loc=(.5, 0, z), bev=0, parent=hg, name="rail")
        for i in range(8): box((.025, .025, 2.3), ST, loc=(.08 + i * .12, 0, 1.2), bev=0, parent=hg, name="bar")
        box((.08, .06, .12), MATS["steel"], loc=(.92, -.04, 1.2), bev=0, parent=hg, name="lock"); merge(hg, nm + "_mesh"); return hg
    grille("grille_closed", so, 0.0); grille("grille_open", sl, 1.5); ga = grille("grille_anim", None, 0.0)
    animate(ga, "open", [(1, dict(rot=(0, 0, 0))), (16, dict(rot=(0, 0, 1.5)))]); animate(ga, "close", [(1, dict(rot=(0, 0, 1.5))), (16, dict(rot=(0, 0, 0)))])
    box((1.2, .2, 2.4), None, loc=(0, 0, 1.2), bev=0, name="stairwell_grille-col"); empty("ip_use", (0, -.8, 0), size=.12); empty("ip_hand", (.4, -.06, 1.2), size=.06); done("stairwell_grille", anims=True)
    mnew(); ST = MATS["steel_dark"]; r = empty("antenna_mast_10m")
    box((2.4, 2.4, .12), MATS["concrete_dark"], loc=(0, 0, .06), bev=0, parent=r, name="platform"); box((.3, .3, .3), MATS["concrete"], loc=(0, 0, .27), bev=0, parent=r, name="base_block")
    tube((0, 0, .2), (0, 0, 10.0), .05, ST, r, "mast", 8)
    for z in (2.5, 5.0, 7.5, 10.0):
        for a in (0, 2.1, 4.2): tube((0, 0, z), (math.cos(a) * 1.0, math.sin(a) * 1.0, z - .35), .012, ST, r, "bracket", 4)
    for a in (.5, 2.6, 4.7):
        for z in (6.0, 10.0): tube((0, 0, z), (math.cos(a) * 3.2, math.sin(a) * 3.2, .12), .006, MATS["steel"], r, "guy_wire", 4)
        box((.4, .4, .08), MATS["concrete_dark"], loc=(math.cos(a) * 3.2, math.sin(a) * 3.2, .04), bev=0, parent=r, name="anchor")
    for z, ln in ((8.0, 1.5), (9.0, 1.1), (7.0, 1.8)): box((ln, .03, .03), ST, loc=(ln / 2, 0, z), bev=0, parent=r, name="dipole"); box((.03, .03, .5), ST, loc=(ln * .9, 0, z), bev=0, parent=r, name="dipole_v")
    merge(r, "mast_mesh"); box((.4, .4, 10.0), None, loc=(0, 0, 5.0), bev=0, name="antenna_mast_10m-col"); empty("ip_use", (1.0, 0, .12), size=.15); empty("ip_hand", (.06, 0, 1.4), size=.06); empty("ip_hit", (0, 0, 10.0), size=.15); done("antenna_mast_10m")

# ============================================================== holes / crawl passages
def holes():
    out("holes");
    mnew(); ST = MATS["steel_dark"]; r = empty("hole_fence_cut"); L_ = 2.5
    for sx in (-L_ / 2, L_ / 2): cyl(.04, 1.8, ST, loc=(sx, 0, .9), seg=8, parent=r, name="post")
    box((L_, .03, .04), ST, loc=(0, 0, 1.78), bev=0, parent=r, name="top_rail")
    for i in range(-12, 13):                                                  # wire diagonals except where a flap is cut out
        x = i * .1
        if abs(x) < .45: continue
        beam((x - .15, 0, .15), (x + .15, 0, 1.78), .006, .006, ST, r, "wire", 0)
    for k in range(5): beam((-.45 + k * .02, 0, .15 + k * .12), (-.7, 0, .1 + k * .1), .005, .005, ST, r, "cut_wire", 0)
    box((.9, .01, .7), mat("flap_wire", (.2, .2, .22), .5, .6), loc=(.6, -.05, .3), bev=0, parent=r, name="peeled_flap").rotation_euler = (.5, 0, .3)
    merge(r, "fence_mesh"); box((L_, .2, 1.8), None, loc=(0, 0, .9), bev=0, name="hole_fence_cut-col"); empty("ip_use", (0, -.8, 0), size=.15); empty("ip_hit", (0, .8, 0), size=.15); empty("ip_hand", (-.5, 0, 1.78), size=.06); done("hole_fence_cut")
    mnew(); Wd = MATS["wood"]; r = empty("hole_fence_boards")
    for sx in (-1.25, 1.25): box((.1, .1, 1.8), Wd, loc=(sx, 0, .9), bev=0, parent=r, name="post")
    for z in (.3, 1.5): box((2.5, .05, .07), Wd, loc=(0, .04, z), bev=0, parent=r, name="rail")
    for i in range(12):
        if i in (5, 6): continue
        box((.19, .02, 1.7), Wd, loc=(-1.25 + .12 + i * .21, -.02, .9), bev=0, parent=r, name="board")
    box((.19, .02, .6), Wd, loc=(-.18, -.2, .3), bev=0, parent=r, name="board_stub").rotation_euler = (0, .3, .5)
    merge(r, "boards_mesh"); box((2.5, .2, 1.8), None, loc=(0, 0, .9), bev=0, name="hole_fence_boards-col"); empty("ip_use", (0, -.8, 0), size=.15); empty("ip_hit", (0, .8, 0), size=.15); done("hole_fence_boards")
    mnew(); r = empty("hole_wall_slab"); C = MATS["concrete"]
    box((1.4, .3, 2.4), C, loc=(-1.7, 0, 1.2), bev=0, parent=r, name="slab_l"); box((1.4, .3, 2.4), C, loc=(1.7, 0, 1.2), bev=0, parent=r, name="slab_r"); box((1.2, .3, 1.5), C, loc=(0, 0, 1.65), bev=0, parent=r, name="slab_top")
    for k in range(6): beam((-.55 + k * .22, 0, .85), (-.5 + k * .22, -.1, .55), .015, .015, MATS["rebar_rust"], r, "rebar", 0)
    rnd = random.Random(9)
    for i in range(8): rock_blob(.09 + .06 * rnd.random(), C, seed=120 + i, loc=(rnd.uniform(-.8, .8), rnd.uniform(-.9, -.2), .05), flat=.6, subdiv=1, rough=.3, parent=r, name="rubble")
    merge(r, "wall_mesh"); box((1.4, .3, 2.4), None, loc=(-1.7, 0, 1.2), bev=0, name="slab_l-col"); box((1.4, .3, 2.4), None, loc=(1.7, 0, 1.2), bev=0, name="slab_r-col"); box((1.2, .3, 1.5), None, loc=(0, 0, 1.65), bev=0, name="slab_top-col")
    empty("ip_use", (0, -1.0, 0), size=.15); empty("ip_hit", (0, 1.0, 0), size=.15); empty("ip_hand", (-.6, -.1, .9), size=.06); done("hole_wall_slab")
    mnew(); r = empty("hole_bush"); gm = mat("foliage", (.1, .2, .07), .85); rnd = random.Random(4)
    for i in range(16):
        a = rnd.uniform(0, 2 * math.pi);
        if -.7 < math.sin(a) < .7 and math.cos(a) < 0: continue
        rock_blob(.4 + .12 * rnd.random(), gm, seed=150 + i, loc=(math.cos(a) * .95, math.sin(a) * .8, .45), flat=.9, subdiv=1, rough=.3, parent=r, name="clump")
    for k in range(4): rock_blob(.45, gm, seed=170 + k, loc=(-.2 + k * .5, .6 * (1 if k % 2 else -1), .8), flat=.7, subdiv=1, rough=.3, parent=r, name="roof_clump")
    merge(r, "bush_mesh"); box((2.0, 1.8, 1.0), None, loc=(0, 0, .5), bev=0, name="hole_bush-convcol"); empty("ip_use", (-1.4, 0, 0), size=.15); empty("ip_hit", (1.4, 0, 0), size=.15); done("hole_bush")
    # chalk / graffiti / path decals, stash items
    for nm, shape in (("decal_chalk_arrow", "arrow"), ("decal_graffiti_garages", "scribble"), ("decal_trodden_path", "path")):
        mnew(); col = {"arrow": (.55, .55, .5), "scribble": (.4, .1, .1), "path": (.1, .075, .045)}[shape]; m_ = mat(nm, col, .9)
        bm = bmesh.new(); uv = bm.loops.layers.uv.new("UVMap")
        if shape == "arrow": polys = [[(-.25, -.03), (.2, -.03), (.2, -.1), (.3, 0), (.2, .1), (.2, .03), (-.25, .03)]]
        elif shape == "scribble": polys = [[(-.4 + i * .1, .1 * ((i % 2) * 2 - 1)), (-.4 + i * .1 + .1, .1 * ((i % 2) * 2 - 1) - .02), (-.4 + i * .1 + .1, .1 * ((i % 2) * 2 - 1) + .02)] for i in range(8)] + [[(-.35, -.18), (.1, -.18), (.1, -.14), (-.35, -.14)], [(.1, -.22), (.3, -.16), (.1, -.1)]]
        else: polys = [[(-.4, -3 + k * .7 + .1 * math.sin(k)), (.4, -3 + k * .7 + .1 * math.sin(k)), (.38, -2.4 + k * .7), (-.38, -2.4 + k * .7)] for k in range(8)]
        for pl in polys:
            f = bm.faces.new([bm.verts.new((x, y, .004)) for x, y in pl]); f.normal_update()
            if f.normal.z < 0: f.normal_flip()
            for l in f.loops: l[uv].uv = ((l.vert.co.x + .5) / 1.0, (l.vert.co.y + 3) / 6)
        mesh_obj(nm, bm, m_, smooth=False); empty("ip_hit", (0, 0, 0), size=.1); done(nm)
    mnew(); r = empty("stash"); bm_ = lathe([(0, 0), (.035, 0), (.04, .1), (.02, .2), (.015, .27), (0, .27)], mat("bottle_glass", (.08, .2, .1), .15), parent=r, seg=10, name="bottle"); box((.1, .08, .002), MATS["paper"], loc=(.1, .02, .001), bev=0, parent=r, name="note")
    merge(r, "stash_mesh"); box((.2, .2, .27), None, loc=(0, 0, .13), bev=0, name="stash-convcol"); empty("ip_hand", (0, 0, .15), size=.04); done("item_stash")

# ============================================================== glass roofs + projectiles
def glass_roofs():
    out("glass")
    def shards(parent, n, area, h):
        rnd = random.Random(n)
        for i in range(n):
            p = poly_prism([(0, 0), (rnd.uniform(.06, .16), rnd.uniform(0, .05)), (rnd.uniform(.02, .1), rnd.uniform(.08, .18))], .006, MATS["loggia_glass"], loc=(rnd.uniform(-area[0], area[0]), rnd.uniform(-area[1], area[1]), h), parent=parent, name="shard"); p.rotation_euler = (rnd.uniform(-.3, .3), rnd.uniform(-.3, .3), rnd.uniform(0, 6))
    mnew(); ST = MATS["steel_dark"]; GL = MATS["loggia_glass"]; r = empty("glass_canopy"); W, D = 3.0, 1.4
    for sx in (-W / 2 + .1, W / 2 - .1): beam((sx, 0, 3.4), (sx, -D + .1, 2.7), .05, .05, ST, r, "bracket", 0); tube((sx, 0, 3.0), (sx, -D + .15, 2.75), .02, ST, r, "tie_rod", 5)
    merge(r, "frame_mesh")
    so = empty("state_ok"); g1 = box((W, D, .012), GL, loc=(0, -D / 2, 3.04), bev=0, parent=so, name="glass"); g1.rotation_euler = (.22, 0, 0)
    for sx in (-W / 2 + .03, 0, W / 2 - .03): box((.05, D, .05), ST, loc=(sx, -D / 2, 3.02), bev=0, parent=so, name="mullion").rotation_euler = (.22, 0, 0)
    sl = empty("state_loose"); box((W, D, .012), GL, loc=(0, -D / 2, 3.04), bev=0, parent=sl, name="glass").rotation_euler = (.22, 0, 0)
    for k in range(7): box((.5 + k * .15, .01, .01), MATS["soot"], loc=(-W / 2 + .3 + k * .4, -.25 - (k % 3) * .35, 3.06), bev=0, parent=sl, name="crack").rotation_euler = (.22, 0, .4 * (k % 3 - 1))
    sb = empty("state_broken")
    for k, x in enumerate((-1.2, 1.2)): box((.8, D, .012), GL, loc=(x, -D / 2, 3.04), bev=0, parent=sb, name="glass_remaining").rotation_euler = (.22, 0, 0)
    for k in range(5): shard_t = poly_prism([(0, 0), (.1, .04), (.05, .25)], .006, GL, loc=(-.3 + k * .15, -.2 - .15 * (k % 2), 2.96), parent=sb, name="shard_hanging"); shard_t.rotation_euler = (1.5 + .3 * k, 0, .4 * k)
    sh = empty("shards", (0, -D / 2, 0), size=.1); shards(sh, 40, (1.4, .9), .01)
    fall = empty("shatter_group", (0, -D / 2, 3.0), size=.1)
    for k in range(10):
        p = poly_prism([(0, 0), (.2, .02), (.08, .3)], .006, GL, loc=(-1.2 + k * .26, 0, 0), parent=fall, name="shatter_piece"); p.rotation_euler = (.2, 0, .3 * k)
        animate(p, "shatter", [(1, dict(loc=(-1.2 + k * .26, 0, 0), rot=(.2, 0, .3 * k))), (8, dict(loc=(-1.2 + k * .26 + .1 * (k % 3 - 1), -.2 - .1 * (k % 4), -.6), rot=(1.2, .6, .3 * k + 1))), (18, dict(loc=(-1.2 + k * .26 + .2 * (k % 3 - 1), -.5 - .1 * (k % 4), -3.0), rot=(2.8, 1.4, .3 * k + 3)))])
    box((W, D, .1), None, loc=(0, -D / 2, 3.0), bev=0, name="glass_canopy-convcol"); empty("ip_use", (0, -D / 2, 0), size=.15); empty("ip_hit", (0, -D / 2, 0), size=.15); empty("ip_hand", (0, -D, 2.75), size=.06); done("glass_canopy", anims=True)
    # skylight, winter garden, greenhouse (single state glb each, with states)
    def framed_roof(nm, W, D, H, n_u, n_v, gable=True, cafe=False):
        mnew(); ST = MATS["steel_dark"]; GL = MATS["loggia_glass"]; r = empty(nm)
        for sx in (-W / 2, W / 2):
            for sy in (-D / 2, D / 2): box((.1, .1, H), ST, loc=(sx, sy, H / 2), bev=0, parent=r, name="post")
        for sx in (-W / 2, W / 2): box((.08, D, .08), ST, loc=(sx, 0, H), bev=0, parent=r, name="eave")
        for sy in (-D / 2, D / 2): box((W, .08, .08), ST, loc=(0, sy, H), bev=0, parent=r, name="side_beam")
        ridge = H + (W / 2) * .5
        box((.08, D, .08), ST, loc=(0, 0, ridge), bev=0, parent=r, name="ridge")
        for k in range(n_v + 1):
            y = -D / 2 + k * D / n_v
            for sx in (-1, 1): beam((sx * W / 2, y, H), (0, y, ridge), .06, .06, ST, r, "rafter", 0)
        for k in range(n_u): pass
        if cafe:
            for sx in (-W / 2, W / 2): box((.04, D, H * .8), GL, loc=(sx, 0, H * .45), bev=0, parent=r, name="wall_glass")
        merge(r, "frame_mesh")
        so = empty("state_ok"); sl = empty("state_loose"); sb = empty("state_broken")
        for parent, broken in ((so, False), (sl, False), (sb, True)):
            for sx in (-1, 1):
                for k in range(n_v):
                    if broken and k in (1,) and sx == 1: continue
                    y = -D / 2 + (k + .5) * D / n_v; g = box((math.hypot(W / 2, ridge - H) * .98, D / n_v * .96, .012), GL, loc=(sx * W / 4, y, (H + ridge) / 2 + .02), bev=0, parent=parent, name="pane")
                    g.rotation_euler = (0, sx * math.atan2(ridge - H, W / 2) * -1, 0)
        for k in range(6): box((.5, .01, .01), MATS["soot"], loc=(-1 + k * .4, -D / 4 + .15 * k, ridge - .3), bev=0, parent=sl, name="crack").rotation_euler = (0, 0, .5 * (k % 3))
        for k in range(8): shard_t = poly_prism([(0, 0), (.12, .04), (.05, .22)], .006, GL, loc=(.6 + .1 * k, .1 + .1 * (k % 3), ridge - .15 - .1 * k), parent=sb, name="shard_hanging"); shard_t.rotation_euler = (1.4, 0, .5 * k)
        sh = empty("shards", (0, 0, 0), size=.1); shards(sh, 50, (W / 2, D / 2), .01)
        box((W, D, H + .8), None, loc=(0, 0, (H + .8) / 2), bev=0, name=nm + "-convcol"); empty("ip_use", (0, -D / 2 - .8, 0), size=.15); empty("ip_hit", (.8, 0, 0), size=.15); empty("ip_hand", (-W / 2, -D / 2, H), size=.06); done(nm)
    framed_roof("skylight_stair", 2.4, 3.6, .4, 2, 3, cafe=False); framed_roof("winter_garden_cafe", 5.0, 7.0, 2.8, 2, 4, cafe=True); framed_roof("greenhouse_park", 4.0, 9.0, 1.8, 2, 6, cafe=True)

def projectiles():
    exec(open("D:/Faceless/models/src/build_items.py", encoding="utf-8").read()[:open("D:/Faceless/models/src/build_items.py", encoding="utf-8").read().index("# ---------------- knife (kitchen)")], globals())
    out("items")
    def brick():
        P = []; mm = mat("brick_item", (.3, .12, .08), .95)
        P.append(box(.215, .102, .065, .003) if False else None)
        P = [None]; return [globals()["box"] if False else None]
    pass

GRP = os.environ.get("GRP", "all")
steps = {"balcony": balconies, "ditch": ditches, "pipes": pipes, "vents": vents, "holes": holes, "glass": glass_roofs}
for k, f in steps.items():
    if GRP in ("all", k): f()
