"""Stage 8 (movement through the city), group A: cheap climbing aids.
bins as steps, crate steps, modular fences, vehicle extras, emergency-exit door, roof tiles, passage arches, gates, padlock, intercom.
Run: GRP=<name|all> D:\\Cosmoteer\\blender.exe -b -P build_move_a.py -> models/movement/<topic>/*.glb"""
import os
_s = open("D:/Faceless/models/src/build_props_a.py", encoding="utf-8").read()
exec(_s[:_s.index("# ------------------------------------------------------------------ street lamp")])
MOVE = "D:/Faceless/models/movement"
_b = open("D:/Faceless/models/src/build_buildings.py", encoding="utf-8").read()
exec(_b[_b.index("def perforated"):_b.index("def balcony")])
def out(topic):
    global OUTDIR
    OUTDIR = f"{MOVE}/{topic}"; os.makedirs(OUTDIR, exist_ok=True)
def mnew():
    pnew(); mat("roof_bitumen", (.05, .05, .055), .95); mat("roof_slate", (.18, .2, .2), .7, .3); mat("roof_gravel", (.22, .21, .2), 1.0); mat("roof_wet", (.03, .035, .045), .12)
    mat("roof_planks", (.17, .11, .07), .95); mat("water", (.04, .1, .13), .05); mat("profnastil", (.15, .28, .2), .6, .4); mat("rusty", (.25, .12, .06), .8, .4)
    mat("barbed", (.18, .18, .19), .5, .8); mat("cloth_rag", (.4, .08, .08), .95); mat("led_red", (.4, .02, .02), .3, 0.0, emit=(1, .05, .03), emit_strength=4); mat("sign_green_glow", (.02, .3, .1), .4, 0.0, emit=(.1, 1, .3), emit_strength=3)
    mat("brick_wall", (.24, .11, .08), .95); mat("panel_wall", (.34, .33, .3), .95); mat("building_window", (.03, .045, .06), .1, 0.0); mat("window_frame", (.3, .3, .28), .6); mat("roof_tar", (.05, .05, .055), .95); mat("brass", (.55, .4, .12), .4, .8)
    mat("balcony_slab", (.28, .28, .26), .95); mat("balcony_rail", (.12, .13, .14), .7); mat("loggia_glass", (.2, .28, .3), .15); mat("door_steel", (.1, .12, .11), .6); mat("column_white", (.5, .5, .46), .9)
    mat("display_glow", (.1, .3, .2), .3, 0.0, emit=(.3, 1, .6), emit_strength=2); mat("button_gray", (.4, .4, .38), .6)

# ============================================================== A1 bins as steps + crates
def bin_step(name, h, w, d):
    mnew(); Y = MATS["paint_yellow"]; G = MATS["green_paint"]
    ok = empty("state_ok"); box((w, d, h * .9), G, loc=(0, 0, h * .45), bev=.015, parent=ok, name="body", seg=2, taper=.92)
    box((w + .04, d + .04, .08), MATS["steel_dark"], loc=(0, 0, h * .9), bev=.01, parent=ok, name="rim"); box((w + .02, d + .02, .14), Y, loc=(0, 0, h * .6), bev=.004, parent=ok, name="yellow_stripe")
    for sx in (-w / 2 + .12, w / 2 - .12): cyl(.07, .05, MATS["rubber"], loc=(sx, d / 2 - .1, .08), seg=10, rot=(0, math.pi / 2, 0), parent=ok, name="wheel")
    for sx in (-w * .3, 0, w * .3): box((.05, d + .03, h * .6), MATS["steel_dark"], loc=(sx, 0, h * .4), bev=0, parent=ok, name="rib")
    lid = empty("lid_ok", (0, d / 2, h * .94), parent=ok, size=.1); box((w + .02, d, .05), MATS["steel_dark"], loc=(0, -d / 2, 0), bev=.008, parent=lid, name="lid_plate"); box((.3, .05, .05), MATS["steel"], loc=(0, -d + .06, .04), bev=.004, parent=lid, name="lid_handle")
    merge(ok, "body_mesh_ok") if False else None
    sl = empty("state_loose")
    box((w, d, h * .9), G, loc=(0, 0, h * .45), bev=.015, parent=sl, name="body", seg=2, taper=.92); box((w + .04, d + .04, .08), MATS["steel_dark"], loc=(0, 0, h * .9), bev=.01, parent=sl, name="rim"); box((w + .02, d + .02, .14), Y, loc=(0, 0, h * .6), bev=.004, parent=sl, name="yellow_stripe")
    lid2 = empty("lid_dented", (0, d / 2, h * .94), parent=sl, size=.1); lid2.rotation_euler = (-.06, 0, .03)
    box((w + .02, d, .05), MATS["steel_dark"], loc=(0, -d / 2, 0), bev=.008, parent=lid2, name="lid_plate"); box((w * .5, d * .5, .05), MATS["steel_dark"], loc=(0, -d / 2, -.05), bev=.02, parent=lid2, name="dent")
    # separate animated lid (clang) for the transition
    la = empty("lid_anim", (0, d / 2, h * .94), size=.1); box((w + .02, d, .05), MATS["steel_dark"], loc=(0, -d / 2, 0), bev=.008, parent=la, name="lid_plate")
    animate(la, "lid_clang", [(1, dict(rot=(0, 0, 0))), (3, dict(rot=(-.18, 0, .05))), (6, dict(rot=(.05, 0, -.03))), (9, dict(rot=(-.08, 0, .02))), (13, dict(rot=(0, 0, 0)))])
    animate(la, "lid_open", [(1, dict(rot=(0, 0, 0))), (14, dict(rot=(-1.8, 0, 0)))])
    box((w + .1, d + .1, h), None, loc=(0, 0, h / 2), bev=0, name=name + "-convcol")
    empty("ip_use", (0, 0, h + .05), size=.12); empty("ip_hand", (0, -d / 2 - .02, h * .9), size=.08); empty("ip_hit", (0, -d / 2 - .5, 0), size=.1)
    done(name, anims=True)
def bins_and_crates():
    out("steps")
    for nm, h, w, d in (("bin_step_s", .95, .8, .6), ("bin_step_m", 1.2, 1.1, .75), ("bin_step_l", 1.45, 1.8, 1.1)): bin_step(nm, h, w, d)
    for h, nm in ((.5, "crate_step_50"), (.8, "crate_step_80"), (1.1, "crate_step_110")):
        mnew(); W_ = MATS["wood"]; r = empty("crate")
        box((.9, .7, h), W_, loc=(0, 0, h / 2), bev=.008, parent=r, name="crate_box")
        for z in [k * .27 + .1 for k in range(int(h / .27))]: box((.92, .72, .05), MATS["steel_dark"], loc=(0, 0, z), bev=0, parent=r, name="band")
        for sx in (-.43, .43):
            for sy in (-.33, .33): box((.06, .06, h + .02), W_, loc=(sx, sy, h / 2), bev=0, parent=r, name="post")
        merge(r, "crate_mesh"); box((.9, .7, h), None, loc=(0, 0, h / 2), bev=0, name=nm + "-convcol"); empty("ip_use", (0, 0, h + .02), size=.1); empty("ip_hand", (0, -.36, h), size=.08); done(nm)
    mnew(); r = empty("crate_stair"); W_ = MATS["wood"]                                  # stack as a stair: 1 / 2 / 3 crates
    for k, (x, n) in enumerate(((0, 3), (.95, 2), (1.9, 1))):
        for z in range(n): box((.9, .7, .5), W_, loc=(x, 0, .25 + z * .5), bev=.008, parent=r, name="crate_box")
    merge(r, "stair_mesh"); box((2.8, .8, 1.5), None, loc=(.95, 0, .75), bev=0, name="crate_stair-convcol"); empty("ip_use", (.95, 0, 1.05), size=.1); empty("ip_hand", (0, -.36, 1.5), size=.08); done("crate_stair")

# ============================================================== A2 fences (modules of 2.5 m)
def fence_section(name, kind):
    mnew(); r = empty("fence"); ST = MATS["steel_dark"]; Wd = MATS["wood"]; C = MATS["concrete"]; L_ = 2.5
    ok = empty("state_ok", parent=None)
    def posts(h, p, mat_=None):
        for sx in (-L_ / 2, L_ / 2): box((p, p, h), mat_ or ST, loc=(sx, 0, h / 2), bev=.004, parent=ok, name="post")
    h = 1.2
    if kind == "low_picket":
        h = 1.1; posts(h, .09, Wd)
        for z in (.3, .8): box((L_, .05, .07), Wd, loc=(0, .04, z), bev=.004, parent=ok, name="rail")
        for i in range(13): box((.08, .02, 1.0), Wd, loc=(-L_ / 2 + .1 + i * .2, -.02, .55), bev=.004, parent=ok, name="picket")
    elif kind == "low_concrete":
        h = 1.2; posts(h, .2, C)
        for k in range(3): box((L_ - .2, .1, .35), C, loc=(0, 0, .22 + k * .4), bev=.006, parent=ok, name="slab")
    elif kind == "mid_profnastil":
        h = 1.8; posts(h, .08, ST)
        for i in range(int(L_ / .2)): box((.1, .04, 1.7), MATS["profnastil"], loc=(-L_ / 2 + .1 + i * .2, 0, .9), bev=0, parent=ok, name="sheet")
        for z in (.3, 1.5): box((L_, .04, .05), ST, loc=(0, .04, z), bev=0, parent=ok, name="rail")
    elif kind == "mid_chainlink":
        h = 1.8; posts(h, .06, ST)
        box((L_, .03, .04), ST, loc=(0, 0, 1.78), bev=0, parent=ok, name="top_rail")
        for i in range(-12, 13): beam((i * .1 - .15, 0, .15), (i * .1 + .15, 0, 1.78), .006, .006, ST, ok, "wire", 0)
    elif kind == "high_barbed":
        h = 2.4; posts(h, .22, C)
        for k in range(6): box((L_ - .2, .1, .35), C, loc=(0, 0, .22 + k * .38), bev=.006, parent=ok, name="slab")
        for sx in (-L_ / 2, L_ / 2): beam((sx, 0, 2.4), (sx, .25, 2.75), .04, .04, ST, ok, "outrigger", 0)
        for z, y in ((2.55, .08), (2.7, .2)):
            for i in range(30): box((.02, .02, .14), MATS["barbed"], loc=(-L_ / 2 + i * .085, y, z), bev=0, parent=ok, name="barb").rotation_euler = (0, .5 * ((i % 2) - .5), 0)
            tube((-L_ / 2, y, z), (L_ / 2, y, z), .006, MATS["barbed"], ok, "wire", 4)
        sl = empty("state_loose")
        for z, y in ((2.55, .08), (2.7, .2)): tube((-L_ / 2, y, z), (L_ / 2, y, z), .006, MATS["barbed"], sl, "wire", 4)
        box((.35, .02, .45), MATS["cloth_rag"], loc=(.3, .08, 2.35), bev=0, parent=sl, name="cloth_rag").rotation_euler = (0, 0, .3)
        box((.25, .02, .3), MATS["cloth_rag"], loc=(.45, .08, 2.15), bev=0, parent=sl, name="cloth_rag_b").rotation_euler = (0, 0, -.2)
        empty("ip_spark", (.3, .08, 2.5), size=.08)
    elif kind == "bars":
        h = 2.0; posts(h, .1, ST)
        for z in (.2, 1.0, 1.95): box((L_, .06, .06), ST, loc=(0, 0, z), bev=0, parent=ok, name="rail")
        n = int((L_ - .15) / .12)
        for i in range(n): box((.025, .025, 1.95), ST, loc=(-L_ / 2 + .1 + i * .12, 0, 1.0), bev=0, parent=ok, name="bar")
    elif kind == "park_iron":
        h = 2.0; posts(h, .12, ST)
        for z in (.25, 1.55): box((L_, .05, .08), ST, loc=(0, 0, z), bev=0, parent=ok, name="rail")
        for i in range(int((L_ - .15) / .14)):
            x = -L_ / 2 + .12 + i * .14; box((.03, .03, 1.7), ST, loc=(x, 0, .85), bev=0, parent=ok, name="bar"); cyl(.025, .14, ST, loc=(x, 0, 1.78), seg=4, r2=.001, parent=ok, name="spear")
        for sx in (-L_ / 2, L_ / 2): sphere(.07, ST, loc=(sx, 0, 2.08), seg=8, rings=5, parent=ok, name="post_ball")
    elif kind == "loose_board":
        h = 1.8; posts(h, .1, Wd)
        for z in (.3, 1.5): box((L_, .05, .07), Wd, loc=(0, .04, z), bev=.004, parent=ok, name="rail")
        for i in range(12):
            if i == 5: continue
            box((.19, .02, 1.7), Wd, loc=(-L_ / 2 + .12 + i * .21, -.02, .9), bev=.004, parent=ok, name="board")
        sl = empty("state_loose")
        for i in range(12):
            if i == 5: bd = box((.19, .02, 1.7), Wd, loc=(-L_ / 2 + .12 + i * .21 + .22, -.14, .9), bev=.004, parent=sl, name="board_bent"); bd.rotation_euler = (0, .0, .0); bd.rotation_euler = (.0, .35, 0); continue
            box((.19, .02, 1.7), Wd, loc=(-L_ / 2 + .12 + i * .21, -.02, .9), bev=.004, parent=sl, name="board")
        for sx in (-L_ / 2, L_ / 2): box((.1, .1, 1.8), Wd, loc=(sx, 0, .9), bev=.004, parent=sl, name="post")
        for z in (.3, 1.5): box((L_, .05, .07), Wd, loc=(0, .04, z), bev=.004, parent=sl, name="rail")
    merge(ok, "ok_mesh")
    if kind in ("high_barbed", "loose_board"):
        if "state_loose" in bpy.data.objects: merge(bpy.data.objects["state_loose"], "loose_mesh")
    box((L_, .3, h), None, loc=(0, 0, h / 2), bev=0, name=name + "-col")
    empty("ip_hand", (0, 0, h), size=.08); empty("ip_use", (0, -.7, 0), size=.12); empty("ip_hit", (0, .8, 0), size=.12)
    done(name)

def fences():
    out("fences")
    for nm, k in (("fence_low_picket", "low_picket"), ("fence_low_concrete", "low_concrete"), ("fence_mid_profnastil", "mid_profnastil"), ("fence_mid_chainlink", "mid_chainlink"), ("fence_high_barbed", "high_barbed"),
                  ("fence_bars", "bars"), ("fence_park_iron", "park_iron"), ("fence_loose_board", "loose_board")): fence_section(nm, k)
    # post / corner / gates
    mnew(); ST = MATS["steel_dark"]; r = empty("post"); box((.2, .2, 2.2), MATS["concrete"], loc=(0, 0, 1.1), bev=.008, parent=r, name="post"); box((.28, .28, .08), MATS["concrete_dark"], loc=(0, 0, 2.24), bev=.004, parent=r, name="cap"); merge(r, "post_mesh")
    box((.25, .25, 2.2), None, loc=(0, 0, 1.1), bev=0, name="fence_post-col"); empty("ip_hand", (0, 0, 2.2), size=.08); done("fence_post")
    mnew(); r = empty("corner"); Wd = MATS["wood"]
    for sx in (0,): box((.2, .2, 1.8), MATS["concrete"], loc=(0, 0, .9), bev=.008, parent=r, name="post")
    for ang in (0, -math.pi / 2):
        s_ = empty("arm", (0, 0, 0), parent=r); s_.rotation_euler = (0, 0, ang)
        for z in (.3, 1.4): box((2.3, .05, .07), Wd, loc=(1.25, 0, z), bev=.004, parent=s_, name="rail")
        for i in range(10): box((.12, .02, 1.6), Wd, loc=(.3 + i * .22, 0, .8), bev=.004, parent=s_, name="board")
    merge(r, "corner_mesh") if False else None
    box((2.6, 2.6, 1.8), None, loc=(1.25, -1.25, .9), bev=0, name="fence_corner-col"); done("fence_corner")
    for nm, kind in (("gate_picket_closed", "closed"), ("gate_picket_open", "open")):
        mnew(); Wd = MATS["wood"]; r = empty("gate")
        for sx in (-.55, .55): box((.12, .12, 1.4), Wd, loc=(sx, 0, .7), bev=.006, parent=r, name="post")
        hinge = empty("gate_leaf", (-.45, 0, 0), parent=r); hinge.rotation_euler = (0, 0, 0 if kind == "closed" else -1.5)
        for z in (.25, .95): box((.86, .05, .07), Wd, loc=(.45, 0, z), bev=.004, parent=hinge, name="rail")
        for i in range(5): box((.1, .02, 1.05), Wd, loc=(.1 + i * .18, -.02, .62), bev=.004, parent=hinge, name="picket")
        beam((.1, 0, .25), (.85, 0, .95), .05, .03, Wd, hinge, "brace", .003); box((.08, .05, .1), MATS["steel"], loc=(.82, -.04, .75), bev=0, parent=hinge, name="latch")
        merge(hinge, "leaf_mesh"); merge(r, "frame_mesh") if False else None
        box((1.3, .3, 1.4), None, loc=(0, 0, .7), bev=0, name=nm + "-col"); empty("ip_use", (0, -.7, 0), size=.12); empty("ip_hand", (.4, -.05, 1.0), size=.08)
        if kind == "closed":
            animate(hinge, "open", [(1, dict(rot=(0, 0, 0))), (18, dict(rot=(0, 0, -1.5)))])
        done(nm, anims=(kind == "closed"))

# ============================================================== A4 emergency-exit door
def emergency_door():
    out("doors"); mnew(); ST = MATS["door_steel"] if "door_steel" in MATS else MATS["steel_dark"]; GR = mat("door_gray", (.2, .22, .22), .6, .3)
    fr = empty("frame")
    for sx in (-.55, .55): box((.1, .24, 2.25), MATS["paint_gray"], loc=(sx, 0, 1.12), bev=.004, parent=fr, name="jamb")
    box((1.2, .24, .1), MATS["paint_gray"], loc=(0, 0, 2.2), bev=.004, parent=fr, name="head_jamb")
    box((1.2, .3, .06), MATS["concrete_dark"], loc=(0, 0, .03), bev=.004, parent=fr, name="threshold")
    box((.54, .03, .22), MATS["sign_green_glow"], loc=(0, -.13, 2.4), bev=0, parent=fr, name="sign_exit")
    for k, (x, w) in enumerate(((-.2, .02), (-.1, .03), (.0, .035), (.12, .03), (.22, .025))): box((w, .035, .14), MATS["door_gray"] if False else MATS["black_paint"], loc=(x, -.145, 2.4), bev=0, parent=fr, name="exit_glyph")
    box((.08, .24, .2), MATS["led_red"], loc=(-.35, -.14, 2.6), bev=.01, parent=fr, name="siren_lamp_base") if False else None
    # emergency beacon and bell
    bc = empty("beacon", (.45, -.14, 2.55), parent=None, size=.08); cyl(.07, .1, MATS["led_red"], loc=(0, 0, 0), seg=10, parent=bc, name="beacon_dome"); box((.06, .02, .1), MATS["paint_gray"], loc=(0, 0, -.07), bev=0, parent=bc, name="bracket")
    animate(bc, "beacon_loop", [(1, dict(scale=(1, 1, 1))), (7, dict(scale=(.55, .55, .55))), (13, dict(scale=(1, 1, 1))), (19, dict(scale=(.55, .55, .55))), (25, dict(scale=(1, 1, 1)))])
    lathe([(.0, 0), (.09, 0), (.08, .06), (.0, .08)], MATS["brass"] if "brass" in MATS else MATS["steel"], loc=(-.45, -.15, 2.5), seg=12, name="bell", parent=None)
    merge(fr, "frame_mesh")
    def leaf(name, parent, angle):
        hinge = empty(name, (-.5, -.02, 1.1), parent=parent, size=.06); hinge.rotation_euler = (0, 0, angle)
        box((1.0, .06, 2.1), GR, loc=(.5, 0, 0), bev=.006, parent=hinge, name="leaf")
        box((.7, .01, 1.6), MATS["paint_gray"], loc=(.5, .035, 0), bev=0, parent=hinge, name="outside_plate")          # blind outside
        box((.86, .05, .08), MATS["steel"], loc=(.5, -.06, -.05), bev=.01, parent=hinge, name="push_bar")                 # inside push bar
        for sx in (.12, .88): box((.06, .06, .12), MATS["steel_dark"], loc=(sx, -.045, -.05), bev=0, parent=hinge, name="bar_mount")
        box((.12, .02, .12), MATS["paint_yellow"], loc=(.5, -.04, .45), bev=0, parent=hinge, name="push_label")
        merge(hinge, name + "_mesh"); return hinge
    so = empty("state_ok"); leaf("door_closed", so, 0.0)
    sl = empty("state_loose"); leaf("door_open", sl, -1.9)
    d = leaf("door_anim", None, 0.0)
    animate(d, "open", [(1, dict(rot=(0, 0, 0))), (6, dict(rot=(0, 0, .05))), (22, dict(rot=(0, 0, -1.9)))]); animate(d, "close", [(1, dict(rot=(0, 0, -1.9))), (16, dict(rot=(0, 0, -.1))), (20, dict(rot=(0, 0, 0)))])
    pb = empty("push_bar_anim", (0, -.08, 1.05), size=.05); box((.86, .05, .08), MATS["steel"], loc=(0, 0, 0), bev=.01, parent=pb, name="bar")
    animate(pb, "push_bar_press", [(1, dict(loc=(0, -.08, 1.05))), (5, dict(loc=(0, .0, 1.05))), (9, dict(loc=(0, -.08, 1.05)))]); merge(pb, "bar_mesh")
    box((1.25, .3, 2.3), None, loc=(0, 0, 1.15), bev=0, name="door_emergency-col"); empty("ip_use", (0, -.9, 0), size=.15); empty("ip_hand", (0, -.1, 1.05), size=.08)
    done("door_emergency", anims=True)

# ============================================================== A5 roof tiles
def roof_tiles():
    out("roofs")
    for nm, matn in (("roof_tile_bitumen", "roof_bitumen"), ("roof_tile_slate", "roof_slate"), ("roof_tile_gravel", "roof_gravel"), ("roof_tile_wet", "roof_wet"), ("roof_tile_planks", "roof_planks")):
        mnew(); r = empty("roof_tile"); M_ = MATS[matn]
        box((4.0, 4.0, .12), M_, loc=(0, 0, -.06), bev=.004, parent=r, name="slab")
        box((4.0, .08, .22), MATS["concrete_dark"], loc=(0, 1.96, .11), bev=0, parent=r, name="lip_back"); box((.08, 4.0, .22), MATS["concrete_dark"], loc=(1.96, 0, .11), bev=0, parent=r, name="lip_side")
        if matn == "roof_bitumen":
            for k, (x, y) in enumerate(((-1.0, -.7), (.9, .5), (-.3, 1.2))): box((.9, .7, .012), mat("patch_dark", (.025, .025, .03), .9), loc=(x, y, .006), bev=0, parent=r, name="patch")
        if matn == "roof_slate":
            for i in range(20): box((4.0, .1, .05), M_, loc=(0, -1.95 + i * .2, .05), bev=0, parent=r, name="wave")
        if matn == "roof_gravel":
            rnd = random.Random(2)
            for i in range(40): rock_blob(.06, M_, seed=60 + i, loc=(rnd.uniform(-1.8, 1.8), rnd.uniform(-1.8, 1.8), .02), flat=.5, subdiv=0, rough=.3, parent=r, name="stone")
        if matn == "roof_wet":
            for (x, y, w_, d_) in ((-.8, .3, 1.4, 1.0), (1.0, -.8, .9, .7)): box((w_, d_, .006), MATS["water"], loc=(x, y, .004), bev=0, parent=r, name="puddle")
        if matn == "roof_planks":
            ok = empty("state_ok"); sl = empty("state_loose")
            for i in range(14):
                z_ = 0.0 if i != 6 else 0.0
                box((.28, 3.9, .04), M_, loc=(-1.95 + i * .3, 0, .02), bev=.004, parent=ok, name="plank")
                if i == 6: box((.28, 3.9, .04), M_, loc=(-1.95 + i * .3, 0, -.05), bev=.004, parent=sl, name="plank_sagged").rotation_euler = (.0, 0, 0)
                else: box((.28, 3.9, .04), M_, loc=(-1.95 + i * .3, 0, .02), bev=.004, parent=sl, name="plank")
            for k in (-1.2, 0, 1.2): box((4.0, .1, .08), M_, loc=(0, k, -.04), bev=0, parent=r, name="joist")
            merge(ok, "ok_mesh"); merge(sl, "loose_mesh")
        merge(r, "tile_mesh")
        box((4.0, 4.0, .2), None, loc=(0, 0, -.1), bev=0, name=nm + "-col"); empty("ip_use", (0, 0, .05), size=.15); empty("ip_hit", (0, -2.2, -.1), size=.15); done(nm)
    mnew(); r = empty("parapet_piece"); C = MATS["concrete"]
    box((4.0, .35, .9), C, loc=(0, 0, .45), bev=.01, parent=r, name="wall"); box((4.05, .4, .07), C, loc=(0, 0, .93), bev=.008, parent=r, name="coping")
    for sx in (-1.0, 1.0): box((.03, .36, .88), MATS["concrete_dark"], loc=(sx, 0, .45), bev=0, parent=r, name="seam")
    merge(r, "parapet_mesh"); box((4.0, .4, .95), None, loc=(0, 0, .47), bev=0, name="roof_parapet-col"); empty("ip_hand", (0, 0, .96), size=.08); empty("ip_use", (0, .6, 0), size=.12); done("roof_parapet")

# ============================================================== A6 passage arches, gates, padlock, intercom
def arch(name, material):
    out("passage"); mnew(); r = empty("arch"); M_ = MATS[material]; W, D, H = 10.0, 7.0, 6.2; AW, AH = 3.3, 3.2
    # wall segment with a through arch at ground level
    left_w = (W - AW) / 2
    for sx in (-1, 1): box((left_w, D, H), M_, loc=(sx * (AW / 2 + left_w / 2), 0, H / 2), bev=0, parent=r, name="pier")
    box((AW, D, H - AH), M_, loc=(0, 0, AH + (H - AH) / 2), bev=0, parent=r, name="over_arch")
    lathe([(.0, 0), (AW / 2, 0), (AW / 2, .01)], M_, parent=r, seg=4, name="x") if False else None
    # arch vault (half cylinder) hidden in the beam above: show a curved soffit
    for k in range(9):
        a0 = math.pi * k / 9; a1 = math.pi * (k + 1) / 9
    box((AW, D - .4, .2), MATS["roof_tar"], loc=(0, 0, AH - .1), bev=0, parent=r, name="soffit")
    for sx in (-AW / 2, AW / 2): box((.12, D, .12), MATS["concrete_dark"], loc=(sx, 0, .06), bev=0, parent=r, name="kerb")
    box((AW, .3, .3), MATS["concrete_dark"], loc=(0, -D / 2 + .1, AH + .15), bev=0, parent=r, name="arch_beam_f")
    # windows on the upper floor
    for side, nm in (("front", 0), ("back", 0)):
        o = perforated("facade_" + side, 4, 1, W / 4 * 1.0, 3.0, 1.4, 1.4, .9, M_, MATS["building_window"], MATS["window_frame"], parent=r, skip=lambda i, j: False, x0=0, z0=AH + .05)
        o.location = (-W / 2, -D / 2, 0) if side == "front" else (W / 2, D / 2, 0)
        if side == "back": o.rotation_euler = (0, 0, math.pi)
    # surveillance camera above the arch
    cam = empty("cam_head", (0, -D / 2 - .1, AH + .5), size=.1); box((.1, .3, .09), MATS["paint_gray"], loc=(0, -.1, 0), bev=.01, parent=cam, name="housing"); cyl(.03, .02, MATS["glass"], loc=(0, -.26, 0), seg=10, rot=(math.pi / 2, 0, 0), parent=cam, name="lens")
    animate(cam, "sweep_loop", [(1, dict(rot=(0, 0, 0))), (25, dict(rot=(0, 0, -.6))), (49, dict(rot=(0, 0, 0))), (73, dict(rot=(0, 0, .6))), (97, dict(rot=(0, 0, 0)))])
    box((W, D, H), None, loc=(0, 0, H / 2), bev=0, name=name + "-col") if False else None
    for sx in (-1, 1): box((left_w, D, H), None, loc=(sx * (AW / 2 + left_w / 2), 0, H / 2), bev=0, name=name + f"_pier{sx}-col")
    box((AW, D, H - AH), None, loc=(0, 0, AH + (H - AH) / 2), bev=0, name=name + "_top-col")
    empty("ip_use", (0, -D / 2 - 1.0, 0), size=.2); empty("ip_hit", (0, 0, 0), size=.15); empty("ip_hand", (AW / 2, -D / 2, 1.2), size=.08)
    done(name, anims=True)

def padlock_item():
    out("passage");
    for state in ("closed", "open", "broken"):
        mnew(); r = empty("padlock"); box((.06, .02, .045), MATS["steel_dark"], loc=(0, 0, 0), bev=.005, parent=r, name="body"); box((.052, .0012, .012), MATS["brass"] if "brass" in MATS else MATS["steel"], loc=(0, -.0106, -.005), bev=0, parent=r, name="plate")
        if state == "closed":
            for sx in (-.0215, .0215): cyl(.0045, .036, MATS["steel"], loc=(sx, 0, .0405), seg=8, parent=r, name="shackle_leg")
            box((.047, .009, .008), MATS["steel"], loc=(0, 0, .0575), bev=.003, parent=r, name="shackle_top")
        elif state == "open":
            cyl(.0045, .036, MATS["steel"], loc=(-.0215, 0, .0405), seg=8, parent=r, name="shackle_leg"); cyl(.0045, .02, MATS["steel"], loc=(.0215, 0, .0285), seg=8, parent=r, name="shackle_stub")
            box((.047, .009, .008), MATS["steel"], loc=(-.003, .0, .0575), bev=.003, parent=r, name="shackle_top").rotation_euler = (0, -.5, 0)
        else:
            box((.06, .02, .045), MATS["steel_dark"], loc=(.01, 0, -.01), bev=.005, parent=r, name="body_broken").rotation_euler = (0, .4, 0); box((.02, .009, .008), MATS["steel"], loc=(.06, .0, .02), bev=.002, parent=r, name="shackle_cut")
        merge(r, "padlock_mesh"); empty("ip_hand", (0, 0, 0), size=.03); done("item_padlock_" + state + "_hand")
        # ground variant: lying on the floor
        mnew(); r = empty("padlock"); b = box((.06, .02, .045), MATS["steel_dark"], loc=(0, 0, .0225), bev=.005, parent=r, name="body"); b.rotation_euler = (0, 0, .4)
        box((.02, .02, .02), None, loc=(0, 0, .01), bev=0, name="item_padlock_ground-convcol"); empty("ip_hand", (0, 0, .03), size=.03); done("item_padlock_" + state + "_ground")

def gates_and_intercom():
    out("passage")
    ST = None
    for nm, variant in (("gate_yard_closed", "latch"), ("gate_yard_open", "open"), ("gate_yard_code", "code"), ("gate_yard_welded", "welded"), ("gate_yard_chain", "chain")):
        mnew(); ST = MATS["steel_dark"]; r = empty("gate"); H = 2.0
        for sx in (-.65, .65): box((.14, .14, H + .1), MATS["concrete"], loc=(sx, 0, (H + .1) / 2), bev=.006, parent=r, name="post")
        hinge = empty("gate_leaf", (-.55, 0, 0), parent=r); hinge.rotation_euler = (0, 0, -1.6 if variant == "open" else 0)
        for z in (.25, .75, 1.3, 1.85): box((1.1, .04, .06), ST, loc=(.55, 0, z), bev=0, parent=hinge, name="rail")
        for i in range(8): box((.03, .03, 1.95), ST, loc=(.1 + i * .13, 0, 1.0), bev=0, parent=hinge, name="bar")
        beam((.1, 0, .25), (1.0, 0, 1.85), .04, .03, ST, hinge, "brace", .002)
        if variant == "latch": box((.1, .05, .04), MATS["steel"], loc=(1.0, -.04, 1.0), bev=0, parent=hinge, name="latch"); box((.06, .05, .12), MATS["steel"], loc=(1.0, -.06, 1.0), bev=0, parent=hinge, name="latch_catch")
        if variant == "code": box((.12, .04, .18), MATS["plastic_black"], loc=(1.02, -.06, 1.15), bev=.006, parent=hinge, name="code_panel"); [box((.025, .012, .025), MATS["button_gray"], loc=(.985 + (k % 3) * .035, -.09, 1.2 - (k // 3) * .035), bev=0, parent=hinge, name="code_key") for k in range(9)]
        if variant == "welded":
            for z in (.25, 1.0, 1.85): box((.12, .08, .04), MATS["rusty"], loc=(1.05, -.02, z), bev=0, parent=hinge, name="weld")
            box((1.2, .02, .06), MATS["rusty"], loc=(.55, 0, 1.0), bev=0, parent=hinge, name="weld_bar")
        if variant == "chain":
            for k in range(10): cyl(.012, .05, MATS["steel"], loc=(.95 + (k % 2) * .02, -.05, .85 + k * .035), seg=6, rot=(0, .4 * (k % 2), 0), parent=hinge, name="chain_link")
            box((.06, .02, .045), MATS["steel_dark"], loc=(1.0, -.07, .9), bev=.004, parent=hinge, name="padlock")
        merge(hinge, "leaf_mesh")
        if variant in ("latch",): animate(hinge, "open", [(1, dict(rot=(0, 0, 0))), (18, dict(rot=(0, 0, -1.6)))])
        box((1.4, .3, H), None, loc=(0, 0, H / 2), bev=0, name=nm + "-col"); empty("ip_use", (0, -.8, 0), size=.12); empty("ip_hand", (.45, -.05, H), size=.08)
        done(nm, anims=(variant == "latch"))
    # intercom panel
    mnew(); r = empty("intercom"); box((.16, .05, .3), MATS["steel_dark"], loc=(0, 0, 0), bev=.006, parent=r, name="panel")
    so = empty("state_ok"); sl = empty("state_loose")
    box((.12, .01, .045), MATS["display_glow"], loc=(0, -.03, .11), bev=0, parent=so, name="display_on"); box((.12, .01, .045), MATS["crt_off"], loc=(0, -.03, .11), bev=0, parent=sl, name="display_off")
    keys = empty("keys", (0, -.03, 0), parent=r)
    for k in range(12): box((.028, .012, .026), MATS["button_gray"], loc=(-.04 + (k % 3) * .04, 0, .06 - (k // 3) * .04), bev=.002, parent=keys, name=f"key_{k}")
    box((.05, .014, .03), MATS["paint_yellow"], loc=(0, -.03, -.13), bev=.003, parent=r, name="call_button")
    k5 = empty("key_press", (0, -.03, .02), size=.02); box((.028, .012, .026), MATS["button_gray"], loc=(0, 0, 0), bev=.002, parent=k5, name="key")
    animate(k5, "press", [(1, dict(loc=(0, -.03, .02))), (3, dict(loc=(0, -.01, .02))), (6, dict(loc=(0, -.03, .02)))]); merge(k5, "key_mesh")
    merge(r, "panel_mesh") if False else None
    box((.2, .08, .34), None, loc=(0, 0, 0), bev=0, name="intercom-col"); empty("ip_use", (0, -.6, -1.0), size=.12); empty("ip_hand", (0, -.05, 0), size=.04); done("intercom_panel", anims=True)

# ============================================================== A3 vehicle extras (decals + clearance helper dummy)
def vehicle_decals():
    out("vehicles_extras"); mnew()
    r = empty("footprint")
    sole = [(-.045, -.13), (.045, -.13), (.05, -.05), (.04, .0), (.045, .06), (.03, .13), (-.03, .13), (-.045, .06), (-.04, 0), (-.05, -.05)]
    bm = bmesh.new(); uv = bm.loops.layers.uv.new("UVMap"); vs = [bm.verts.new((x, y, .003)) for x, y in sole]; f = bm.faces.new(vs); f.normal_update()
    if f.normal.z < 0: f.normal_flip()
    for l in f.loops: l[uv].uv = ((l.vert.co.x + .06) / .12, (l.vert.co.y + .14) / .28)
    mesh_obj("sole_print", bm, mat("decal_footprint", (.1, .09, .08), .9), smooth=False, parent=r); empty("ip_hit", (0, 0, 0), size=.05); done("decal_footprint")
    mnew(); r = empty("dent_hood")                                            # dents are separate nodes toggled by the game on cars
    for nm, (w_, d_, z_) in (("dent_hood_overlay", (.9, .8, .965)), ("dent_roof_overlay", (.9, 1.0, 1.405))):
        bm = bmesh.new(); bmesh.ops.create_uvsphere(bm, u_segments=12, v_segments=8, radius=.5)
        for v in bm.verts: v.co.x *= w_; v.co.y *= d_; v.co.z *= .05 if v.co.z < 0 else .004
        mesh_obj(nm, bm, mat("dent_paint", (.06, .07, .09), .5, .3), loc=(0, 0, 0), parent=r)
    done("car_dent_overlays")

GRP = os.environ.get("GRP", "all")
steps = {"bins": bins_and_crates, "fences": fences, "door": emergency_door, "roofs": roof_tiles, "arch": lambda: (arch("arch_passage_brick", "brick_wall"), arch("arch_passage_panel", "panel_wall")), "padlock": padlock_item, "gates": gates_and_intercom, "decals": vehicle_decals}
for k, f in steps.items():
    if GRP in ("all", k): f()
