"""Stage 8, group C: elevator + shaft, basement windows and basement modules, flashlight, spirit-glass pieces.
Run: GRP=<elevator|basement|spirit|all> D:\\Cosmoteer\\blender.exe -b -P build_move_c.py -> models/movement/<topic>/*.glb"""
import os
_a = open("D:/Faceless/models/src/build_move_a.py", encoding="utf-8").read()
exec(_a[:_a.index("GRP = os.environ.get")])
_b = open("D:/Faceless/models/src/build_move_b.py", encoding="utf-8").read()
exec(_b[_b.index("def card("):_b.index("def wall_stub(")])
FH = 2.8

def cmat():
    mnew(); mat("elevator_wall", (.2, .17, .12), .7); mat("mirror", (.4, .45, .5), .05, .9); mat("floor_lino", (.08, .08, .07), .8)
    mat("indicator_glow", (.4, .2, .02), .3, 0.0, emit=(1, .5, .1), emit_strength=3); mat("ceiling_lamp", (.6, .55, .4), .3, 0.0, emit=(1, .9, .6), emit_strength=2)
    mat("shaft_concrete", (.3, .3, .28), .95); mat("cable", (.07, .07, .07), .6, .6); mat("glass_dirty", (.1, .13, .13), .15); mat("counterweight_iron", (.1, .1, .1), .8, .4)

def elevator():
    out("elevator"); cmat(); root = empty("elevator"); SH = 3 * FH + .6; SW, SD = 1.8, 2.2
    # shaft (open front side to see inside is not needed; three walls + pit) - walls thin shells
    for sx in (-SW / 2 - .1, SW / 2 + .1): box((.2, SD + .2, SH + .6), MATS["shaft_concrete"], loc=(sx, 0, (SH - .6) / 2 + .0), bev=0, parent=root, name="wall_side")
    box((SW + .4, .2, SH + .6), MATS["shaft_concrete"], loc=(0, SD / 2 + .1, (SH - .6) / 2), bev=0, parent=root, name="wall_back")
    box((SW + .4, SD + .2, .2), MATS["shaft_concrete"], loc=(0, 0, -.7), bev=0, parent=root, name="pit_floor"); box((SW + .4, SD + .2, .25), MATS["shaft_concrete"], loc=(0, 0, SH + .15), bev=0, parent=root, name="shaft_roof")
    for sx in (-.65, .65): box((.08, .08, SH + .3), MATS["steel_dark"], loc=(sx, .5, (SH - .6) / 2), bev=0, parent=root, name="guide_rail")
    for k in range(int((SH + .4) / .3)): box((.35, .04, .03), MATS["steel"], loc=(-SW / 2 + .15, SD / 2 - .05, -.4 + k * .3), bev=0, parent=root, name="wall_staple"); [box((.03, .12, .03), MATS["steel"], loc=(-SW / 2 + .15 + sx, SD / 2 - .1, -.4 + k * .3), bev=0, parent=root, name="staple_leg") for sx in (-.15, .15)]
    for k in range(3):                                                             # landing doors
        z0 = k * FH
        d = empty(f"landing_door_{k}", (-.45, -SD / 2, z0 + 1.0), parent=None, size=.05)
        for sx, w in ((.0, .45), (.45, .45)): box((w, .05, 2.0), MATS["door_steel"], loc=(sx + w / 2, 0, 0), bev=.004, parent=d, name="door_leaf")
        box((.1, .02, .12), MATS["steel_dark"], loc=(.45, -.04, .1), bev=0, parent=d, name="key_lock_plate"); cyl(.015, .02, MATS["steel"], loc=(.45, -.05, .1), seg=8, rot=(math.pi / 2, 0, 0), parent=d, name="key_lock")
        merge(d, f"landing_door_{k}_mesh")
        animate(d, "open", [(1, dict(loc=(-.45, -SD / 2, z0 + 1.0))), (14, dict(loc=(-1.35, -SD / 2, z0 + 1.0)))]); animate(d, "close", [(1, dict(loc=(-1.35, -SD / 2, z0 + 1.0))), (14, dict(loc=(-.45, -SD / 2, z0 + 1.0)))])
        box((1.3, .3, .12), MATS["concrete_dark"], loc=(0, -SD / 2, z0 - .06), bev=0, parent=root, name="landing_sill")
        for sx in (-.7, .7): box((.12, .3, 2.2), MATS["paint_gray"], loc=(sx, -SD / 2, z0 + 1.1), bev=0, parent=root, name="door_jamb")
        box((1.5, .3, .12), MATS["paint_gray"], loc=(0, -SD / 2, z0 + 2.2), bev=0, parent=root, name="door_head")
    # cabin
    cab = empty("cabin", (0, 0, .05), size=.2)
    box((1.1, 1.4, .06), MATS["floor_lino"], loc=(0, 0, 0), bev=0, parent=cab, name="floor")
    for sx in (-.55, .55): box((.04, 1.4, 2.2), MATS["elevator_wall"], loc=(sx, 0, 1.1), bev=0, parent=cab, name="wall_side")
    box((1.1, .04, 2.2), MATS["elevator_wall"], loc=(0, .7, 1.1), bev=0, parent=cab, name="wall_back")
    box((1.1, 1.4, .06), MATS["elevator_wall"], loc=(0, 0, 2.2), bev=0, parent=cab, name="ceiling"); box((.5, .5, .02), MATS["ceiling_lamp"], loc=(0, .1, 2.16), bev=0, parent=cab, name="ceiling_lamp")
    box((.7, .02, 1.0), MATS["mirror"], loc=(0, .67, 1.35), bev=0, parent=cab, name="mirror"); box((.03, .3, .3), MATS["indicator_glow"], loc=(.0, .0, .0), bev=0, parent=cab, name="floor_display") if False else None
    box((.2, .02, .08), MATS["indicator_glow"], loc=(.45, -.62, 2.05), bev=0, parent=cab, name="floor_display")
    box((.14, .03, .5), MATS["steel_dark"], loc=(.5, -.65, 1.2), bev=0, parent=cab, name="button_panel")
    for k in range(4): box((.04, .02, .04), MATS["button_gray"], loc=(.5, -.67, 1.35 - k * .1), bev=0, parent=cab, name=f"button_{k}")
    for sx in (-.4, .4): box((.4, .04, 2.0), MATS["door_steel"], loc=(sx, -.7, 1.05), bev=0, parent=cab, name="cabin_door")
    hatch = empty("roof_hatch", (0, .0, 2.23), parent=cab, size=.1); box((.5, .5, .03), MATS["steel_dark"], loc=(0, 0, 0), bev=0, parent=hatch, name="hatch_plate")
    merge(cab, "cabin_mesh") if False else None
    ha = empty("hatch_anim", (0, .25, 2.26), parent=cab, size=.1); box((.5, .5, .03), MATS["steel_dark"], loc=(0, -.25, 0), bev=0, parent=ha, name="hatch_plate"); box((.1, .03, .03), MATS["steel"], loc=(0, -.45, .03), bev=0, parent=ha, name="hatch_handle")
    animate(ha, "hatch_open", [(1, dict(rot=(0, 0, 0))), (14, dict(rot=(-1.6, 0, 0)))])
    box((1.0, 1.3, .05), MATS["steel_dark"], loc=(0, 0, 2.28), bev=0, parent=cab, name="roof_plate"); empty("ip_use_roof", (0, 0, 2.35), parent=cab, size=.15)
    # cables and counterweight
    cw = empty("counterweight", (.0, .85, 4.2), size=.2); box((.5, .12, 1.4), MATS["counterweight_iron"], loc=(0, 0, 0), bev=0, parent=cw, name="weight")
    cable = empty("cables", (0, 0, 0), size=.1)
    for sx in (-.2, .2): tube((sx, .4, 2.35), (sx, .4, SH + .1), .012, MATS["cable"], cable, "cable_cab", 5)
    tube((0, .85, 4.9), (0, .85, SH + .1), .012, MATS["cable"], cable, "cable_cw", 5)
    h_up = 2 * FH
    animate(cab, "ride_up", [(1, dict(loc=(0, 0, .05))), (24, dict(loc=(0, 0, .05 + h_up * .5))), (72, dict(loc=(0, 0, .05 + h_up)))]); animate(cab, "ride_down", [(1, dict(loc=(0, 0, .05 + h_up))), (72, dict(loc=(0, 0, .05)))])
    animate(cw, "ride_up", [(1, dict(loc=(0, .85, 4.2))), (72, dict(loc=(0, .85, 4.2 - h_up)))]); animate(cw, "ride_down", [(1, dict(loc=(0, .85, 4.2 - h_up))), (72, dict(loc=(0, .85, 4.2)))])
    box((SW + .4, SD + .2, SH + 1), None, loc=(0, 0, (SH + .4) / 2 - .5), bev=0, name="elevator_shaft-col")
    empty("ip_use", (0, -SD / 2 - .9, 0), size=.2); empty("ip_hand", (-SW / 2 + .15, SD / 2 - .1, 1.2), size=.06); empty("ip_hit", (0, 0, -.6), size=.15); empty("ip_spark", (.5, -.65, 1.3), size=.06)
    done("elevator_shaft", anims=True)

def basement():
    out("basement"); cmat(); mat("glass_dirty", (.1, .13, .13), .15)
    for variant in ("closed", "ajar", "broken"):
        pass
    r = empty("basement_window"); wall = MATS["brick_wall"]
    box((1.6, .45, .9), wall, loc=(0, .22, .15), bev=0, parent=r, name="wall") if False else None
    for sx in (-.65, .65): box((.5, .45, .7), wall, loc=(sx, .22, .15), bev=0, parent=r, name="wall_side")
    box((.8, .45, .3), wall, loc=(0, .22, .5), bev=0, parent=r, name="wall_top"); box((.8, .45, .1), MATS["concrete_dark"], loc=(0, .22, -.15), bev=0, parent=r, name="sill")
    box((1.6, .3, .1), MATS["concrete_dark"], loc=(0, .0, .0), bev=0, parent=r, name="ground_edge")
    # light well
    for sx in (-.65, .65): box((.1, .8, 1.2), MATS["concrete"], loc=(sx, -.5, -.6), bev=0, parent=r, name="well_side")
    box((1.4, .1, 1.2), MATS["concrete"], loc=(0, -.9, -.6), bev=0, parent=r, name="well_front"); box((1.4, .8, .1), MATS["concrete_dark"], loc=(0, -.5, -1.2), bev=0, parent=r, name="well_floor")
    merge(r, "wall_mesh")
    fr = empty("frame"); [box(s, MATS["window_frame"], loc=l, bev=0, parent=fr, name="frame_bar") for s, l in (((.84, .06, .05), (0, .1, .27)), ((.84, .06, .05), (0, .1, -.07)), ((.05, .06, .4), (-.395, .1, .1)), ((.05, .06, .4), (.395, .1, .1)))]
    merge(fr, "frame_mesh")
    so = empty("state_ok"); box((.74, .02, .32), MATS["glass_dirty"], loc=(0, .1, .1), bev=0, parent=so, name="glass")
    sl = empty("state_loose"); sash = empty("sash", (0, .1, .27), parent=sl); sash.rotation_euler = (.9, 0, 0); box((.74, .02, .32), MATS["glass_dirty"], loc=(0, 0, -.16), bev=0, parent=sash, name="glass"); box((.74, .04, .04), MATS["window_frame"], loc=(0, 0, -.33), bev=0, parent=sash, name="sash_bar")
    sb = empty("state_broken")
    for k in range(5): p = poly_prism([(0, 0), (.1, .04), (.04, .2)], .006, MATS["glass_dirty"], loc=(-.3 + k * .15, .1, .27 - k * .02), parent=sb, name="shard_in_frame"); p.rotation_euler = (math.pi / 2, 0, .3 * k)
    shards = empty("shards", (0, -.5, -1.15), size=.1); [poly_prism([(0, 0), (.1, .04), (.04, .15)], .006, MATS["glass_dirty"], loc=(-.4 + .13 * k, .2 * (k % 3), .01), parent=shards, name="shard") for k in range(10)]
    gr_ok = empty("grille_ok"); [box((.025, .025, .5), MATS["steel_dark"], loc=(-.36 + k * .12, -.1, .1), bev=0, parent=gr_ok, name="bar") for k in range(7)]; box((.84, .03, .04), MATS["steel_dark"], loc=(0, -.1, .34), bev=0, parent=gr_ok, name="bar_h"); box((.84, .03, .04), MATS["steel_dark"], loc=(0, -.1, -.14), bev=0, parent=gr_ok, name="bar_h")
    gr_cut = empty("grille_cut"); [box((.025, .025, .5), MATS["steel_dark"], loc=(-.36 + k * .12, -.1, .1), bev=0, parent=gr_cut, name="bar") for k in (0, 1, 5, 6)]
    for k in (2, 3, 4): box((.025, .025, .15), MATS["steel_dark"], loc=(-.36 + k * .12, -.1, .3), bev=0, parent=gr_cut, name="bar_stub_up"); box((.025, .025, .15), MATS["steel_dark"], loc=(-.36 + k * .12, -.1, -.1), bev=0, parent=gr_cut, name="bar_stub_down")
    box((.84, .03, .04), MATS["steel_dark"], loc=(0, -.1, .34), bev=0, parent=gr_cut, name="bar_h"); box((.84, .03, .04), MATS["steel_dark"], loc=(0, -.1, -.14), bev=0, parent=gr_cut, name="bar_h")
    box((1.6, .6, 1.0), None, loc=(0, 0, .0), bev=0, name="basement_window-col"); empty("ip_use", (0, -.9, .05), size=.12); empty("ip_hand", (0, -.1, .4), size=.06); empty("ip_hit", (0, .6, -1.2), size=.12)
    done("basement_window")
    # modules (8 m long, 2.4 m high; walls drawn as thin plates; floor and ceiling)
    def module(name, kind):
        cmat(); root = empty("module"); L, W, H = 8.0, 3.0, 2.4; C_ = MATS["shaft_concrete"]
        box((L, W, .15), MATS["concrete_dark"], loc=(0, 0, -.075), bev=0, parent=root, name="floor"); box((L, W, .15), C_, loc=(0, 0, H + .075), bev=0, parent=root, name="ceiling")
        for sy in (-1, 1): box((L, .15, H), C_, loc=(0, sy * (W / 2 + .075), H / 2), bev=0, parent=root, name="wall")
        for sx in (-1, 1): box((.15, W, H), C_, loc=(sx * (L / 2 + .075), 0, H / 2), bev=0, parent=root, name="end_wall") if kind != "pipes" else None
        for k in range(4): box((.06, W - .1, .12), MATS["steel_dark"], loc=(-3 + k * 2, 0, H - .1), bev=0, parent=root, name="cable_tray")
        for k in range(2): box((.3, .3, .06), MATS["ceiling_lamp"], loc=(-2 + k * 4, 0, H - .03), bev=0, parent=root, name="lamp")
        if kind == "pipes":
            for z, y, d_ in ((2.0, -1.1, .22), (1.7, -1.1, .12), (2.1, 1.1, .18)): tube((-L / 2, y, z), (L / 2, y, z), d_ / 2, mat("pipe_foil", (.4, .42, .42), .55, .6), root, "pipe", 12)
            for sx in range(-3, 4, 2): box((.1, .4, .06), MATS["steel_dark"], loc=(sx, -1.1, 1.85), bev=0, parent=root, name="pipe_hanger")
            box((.8, .1, 1.7), MATS["door_steel"], loc=(L / 2 - .1, 0, .85), bev=0, parent=root, name="door_end")
            box((.8, .8, .06), MATS["steel_dark"], loc=(-L / 2 + 1.0, 0, H - .02), bev=0, parent=root, name="ceiling_hatch_up")
        elif kind == "storage":
            for sy in (-1, 1):
                for k in range(3):
                    x = -2.6 + k * 2.6; cage = empty(f"cage_{sy}_{k}", (x, sy * (W / 2 - .85), 0), parent=root)
                    for z in (.0, 1.1, 2.1): box((1.6, 1.4, .04), MATS["wood"], loc=(0, 0, z + .02), bev=0, parent=cage, name="board") if z == 0 else None
                    for i in range(8): box((.05, .02, 2.3), MATS["wood"], loc=(-.7 + i * .2, sy * -.7, 1.15), bev=0, parent=cage, name="plank")
                    for i in range(6): beam((-.8, sy * -.7, .2 + i * .35), (.8, sy * -.7, .35 + i * .35), .01, .01, MATS["steel"], cage, "mesh_wire", 0) if i % 2 else None
                    box((.7, .04, 1.9), MATS["wood"], loc=(.0, sy * -.7 - sy * .04, 1.0), bev=0, parent=cage, name="cage_door")
                    box((.07, .05, .04), MATS["steel"], loc=(.28, sy * -.7 - sy * .08, 1.0), bev=0, parent=cage, name="cage_lock")
            box((.8, .1, 1.7), MATS["door_steel"], loc=(L / 2 - .1, 0, .85), bev=0, parent=root, name="door_end")
        else:
            box((1.6, 2.4, .1), MATS["steel_dark"], loc=(-L / 2 + 1.4, 0, H - .03), bev=0, parent=root, name="ladder_hatch_frame"); box((.7, .7, .04), MATS["steel"], loc=(-L / 2 + 1.4, 0, H - .01), bev=0, parent=root, name="hatch_up")
            for k in range(7): box((.5, .04, .03), MATS["steel"], loc=(-L / 2 + 1.4, -.7, .3 + k * .3), bev=0, parent=root, name="ladder_rung")
            for sx in (-.2, .2): box((.04, .04, 2.2), MATS["steel"], loc=(-L / 2 + 1.4 + sx, -.7, 1.1), bev=0, parent=root, name="ladder_rail")
            box((.9, .1, 1.9), MATS["door_steel"], loc=(L / 2 - .1, 0, .95), bev=0, parent=root, name="door_end")
            for k in range(3): tube((-L / 2, 1.1, 1.2 + k * .2), (L / 2, 1.1, 1.2 + k * .2), .03, MATS["steel_dark"], root, "conduit", 6)
        merge(root, "module_mesh")
        box((L, W, H), None, loc=(0, 0, H / 2), bev=0, name=name + "-convcol"); empty("ip_use", (0, 0, 0), size=.15); empty("ip_hand", (-L / 2 + 1.4, -.7, 1.0), size=.06); done(name)
    module("basement_corridor_pipes", "pipes"); module("basement_storage_cages", "storage"); module("basement_tech_hatch", "tech")

def spirit_pieces():
    out("spirit"); cmat(); mat("glass_spirit", (.1, .18, .2), .08, 0.0, emit=(.35, .3, .15), emit_strength=.15); mat("vent_spirit", (.1, .1, .11), .5, .6, emit=(.3, .22, .08), emit_strength=.12)
    mnew(); mat("glass_spirit", (.1, .18, .2), .08, 0.0, emit=(.35, .3, .15), emit_strength=.15); r = empty("spirit_window")
    for sx in (-.6, .6): box((.1, .2, 1.4), MATS["window_frame"], loc=(sx, 0, .7), bev=0, parent=r, name="frame_side")
    for z in (0, 1.4): box((1.3, .2, .1), MATS["window_frame"], loc=(0, 0, z), bev=0, parent=r, name="frame_bar")
    box((.04, .12, 1.3), MATS["window_frame"], loc=(0, 0, .7), bev=0, parent=r, name="mullion"); box((1.4, .3, .05), MATS["concrete_dark"], loc=(0, -.08, -.03), bev=0, parent=r, name="sill")
    for sx in (-.3, .3): box((.54, .02, 1.28), MATS["glass_spirit"], loc=(sx, 0, .7), bev=0, parent=r, name="glass")
    box((1.3, .25, 1.5), None, loc=(0, 0, .7), bev=0, name="spirit_window-col"); empty("ip_use", (0, -.9, 0), size=.15); empty("ip_hit", (0, 0, .7), size=.15); done("spirit_window")
    mnew(); mat("vent_spirit", (.1, .1, .11), .5, .6, emit=(.3, .22, .08), emit_strength=.12); r = empty("spirit_vent_grille")
    box((.7, .1, .7), MATS["concrete_dark"], loc=(0, .05, 0), bev=0, parent=r, name="frame")
    box((.58, .02, .58), MATS["soot"], loc=(0, -.03, 0), bev=0, parent=r, name="dark_behind"); [box((.03, .03, .58), MATS["vent_spirit"], loc=(-.25 + k * .1, -.06, 0), bev=0, parent=r, name="bar") for k in range(6)]
    for z in (-.3, .3): box((.6, .03, .04), MATS["vent_spirit"], loc=(0, -.06, z), bev=0, parent=r, name="rail")
    box((.7, .15, .7), None, loc=(0, 0, 0), bev=0, name="spirit_vent_grille-col"); empty("ip_use", (0, -.6, -.35), size=.12); done("spirit_vent_grille")
    mnew(); rm = mat("ripple_gold", (.6, .5, .25), .5, 0.0, emit=(1, .85, .45), emit_strength=1.2)
    r = empty("ripple_origin"); bm = bmesh.new(); uv = bm.loops.layers.uv.new("UVMap"); seg = 48; r0, r1 = .8, 1.0
    for i in range(seg):
        a0, a1 = 2 * math.pi * i / seg, 2 * math.pi * (i + 1) / seg
        v = [bm.verts.new((math.cos(a0) * r0, 0, math.sin(a0) * r0)), bm.verts.new((math.cos(a0) * r1, 0, math.sin(a0) * r1)), bm.verts.new((math.cos(a1) * r1, 0, math.sin(a1) * r1)), bm.verts.new((math.cos(a1) * r0, 0, math.sin(a1) * r0))]
        f = bm.faces.new(v)
        for l, (u_, v_) in zip(f.loops, ((0, i / seg), (1, i / seg), (1, (i + 1) / seg), (0, (i + 1) / seg))): l[uv].uv = (u_, v_)
    ring = mesh_obj("ripple_ring", bm, rm, parent=r, smooth=False)
    animate(r, "ripple", [(1, dict(scale=(.05, .05, .05))), (12, dict(scale=(.6, .6, .6))), (30, dict(scale=(1.4, 1.4, 1.4)))]); animate(r, "ripple_double", [(1, dict(scale=(.05, .05, .05))), (10, dict(scale=(.5, .5, .5))), (18, dict(scale=(.3, .3, .3))), (36, dict(scale=(1.6, 1.6, 1.6)))])
    empty("ip_hit", (0, 0, 0), size=.1); done("spirit_ripple", anims=True)

GRP = os.environ.get("GRP", "all")
for k, f in {"elevator": elevator, "basement": basement, "spirit": spirit_pieces}.items():
    if GRP in ("all", k): f()
