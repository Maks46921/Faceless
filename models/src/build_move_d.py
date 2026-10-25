"""Stage 8, group D: industrial pipelines, brick chimney with climbing staples, tower crane (animated), construction site kit, janitor cart.
Run: GRP=<pipes|chimney|crane|site|cart|all> D:\\Cosmoteer\\blender.exe -b -P build_move_d.py -> models/movement/<industry|construction>/*.glb, city/props/janitor_cart.glb
Conventions: metres, front -Y (glTF +Z), origin at ground centre, `-convcol` collision, ip_use / ip_hand / ip_hit empties."""
import os
_a = open("D:/Faceless/models/src/build_move_a.py", encoding="utf-8").read()
exec(_a[:_a.index("GRP = os.environ.get")])
_b = open("D:/Faceless/models/src/build_move_b.py", encoding="utf-8").read()
exec(_b[_b.index("def card("):_b.index("def wall_stub(")])
FH = 2.8


def dmat():
    mnew(); mat("pipe_orange", (.5, .2, .04), .5, .5); mat("pipe_steel", (.22, .23, .25), .45, .7); mat("pipe_rust", (.3, .13, .06), .8, .4); mat("grating", (.12, .12, .13), .6, .6)
    mat("brick_chimney", (.28, .12, .08), .95); mat("paint_white", (.55, .55, .52), .8); mat("paint_red", (.4, .05, .04), .8); mat("crane_yellow", (.6, .42, .03), .6, .2)
    mat("concrete_gray", (.3, .3, .28), .95); mat("sheet_green", (.1, .25, .15), .6, .3); mat("cabin_blue", (.1, .2, .3), .7); mat("clay", (.25, .17, .1), 1.0); mat("rebar", (.25, .12, .07), .7, .6)
    mat("mixer_orange", (.55, .25, .03), .6, .3); mat("vinyl_blue", (.05, .1, .22), .8); mat("bucket_yellow", (.6, .5, .05), .5); mat("wet_floor", (.65, .55, .02), .5)
    mat("wood_pale", (.3, .22, .12), .9)


# ============================================================== pipelines
def rack_supports(root, xs, z=3.4, w=1.6):
    for x in xs:
        for sy in (-w / 2, w / 2): beam((x, sy, 0), (x, sy, z), .16, .16, MATS["steel_dark"], root, "rack_leg", 0)
        beam((x, -w / 2, z), (x, w / 2, z), .14, .2, MATS["steel_dark"], root, "rack_beam", 0)
        beam((x, -w / 2, 1.0), (x, w / 2, z - .4), .06, .06, MATS["steel_dark"], root, "rack_brace", 0)


def pipe_rack_6m():
    out("industry"); dmat(); r = empty("pipe_rack_6m"); rack_supports(r, (-2.9, 0, 2.9))
    for y, rad, m in ((-.5, .3, "pipe_orange"), (0, .22, "pipe_steel"), (.5, .16, "pipe_rust")):
        tube((-3, y, 3.7), (3, y, 3.7), rad, MATS[m], r, "pipe", 12)
        for x in (-1.5, 1.5): cyl(rad + .03, .1, MATS["steel_dark"], loc=(x, y, 3.7), seg=12, rot=(0, math.pi / 2, 0), parent=r, name="flange")
    box((6.0, 1.7, 1.0), None, loc=(0, 0, 3.7), bev=0, name="pipe_rack_6m-convcol"); empty("ip_hand", (0, -.5, 4.05), size=.08); empty("ip_hit", (0, -1.5, 0), size=.1); empty("ip_use", (0, -.5, 4.1), size=.12)
    done("pipe_rack_6m")
    out("industry"); dmat(); r = empty("pipe_rack_corner"); rack_supports(r, (-2.9, 0))
    for sx in (-.8, .8): beam((0 + sx, -.8, 0), (0 + sx, -.8, 3.4), .16, .16, MATS["steel_dark"], r, "rack_leg", 0); beam((sx, .8, 0), (sx, .8, 3.4), .16, .16, MATS["steel_dark"], r, "rack_leg", 0)
    for z0 in (3.4,): beam((-.8, -.8, z0), (-.8, .8, z0), .14, .2, MATS["steel_dark"], r, "rack_beam", 0); beam((.8, -.8, z0), (.8, .8, z0), .14, .2, MATS["steel_dark"], r, "rack_beam", 0)
    for rad, m, off in ((.3, "pipe_orange", -.5), (.22, "pipe_steel", 0), (.16, "pipe_rust", .5)):
        tube((-3, off, 3.7), (-off, off, 3.7), rad, MATS[m], r, "pipe_a", 12); sphere(rad * 1.02, MATS[m], loc=(-off, off, 3.7), seg=12, rings=8, parent=r, name="elbow"); tube((-off, off, 3.7), (-off, 3, 3.7), rad, MATS[m], r, "pipe_b", 12)
    box((3.5, 3.5, 1.0), None, loc=(-1.0, 1.0, 3.7), bev=0, name="pipe_rack_corner-convcol"); empty("ip_hand", (-1.0, -.5, 4.05), size=.08); empty("ip_use", (-1.0, -.5, 4.1), size=.12)
    done("pipe_rack_corner")


def pipe_bridge_12m():
    out("industry"); dmat(); r = empty("pipe_bridge_12m"); H = 5.2
    for sx in (-6, 6):
        for dx in (-.5, .5):
            for dy in (-.7, .7): beam((sx + dx, dy, 0), (sx + dx, dy, H), .18, .18, MATS["steel_dark"], r, "tower_leg", 0)
        for z in (1.6, 3.4): box((1.2, 1.6, .1), MATS["steel_dark"], loc=(sx, 0, z), bev=0, parent=r, name="tower_ring")
        beam((sx - .5, -.7, 0), (sx + .5, .7, 3.4), .06, .06, MATS["steel_dark"], r, "tower_brace", 0); beam((sx + .5, -.7, 0), (sx - .5, .7, 3.4), .06, .06, MATS["steel_dark"], r, "tower_brace", 0)
    for sy in (-.7, .7): beam((-6, sy, H), (6, sy, H), .25, .3, MATS["steel_dark"], r, "main_girder", 0)
    for k in range(13): box((.14, 1.6, .12), MATS["steel_dark"], loc=(-6 + k, 0, H + .05), bev=0, parent=r, name="cross_beam")
    for y, rad, m in ((-.4, .28, "pipe_orange"), (.1, .2, "pipe_steel"), (.5, .14, "pipe_rust")): tube((-6.5, y, H + .4), (6.5, y, H + .4), rad, MATS[m], r, "pipe", 12)
    box((12, 1.1, .05), MATS["grating"], loc=(0, -.0, H + .95), bev=0, parent=r, name="catwalk")
    for k in range(7):
        x = -6 + k * 2
        for sy in (-.55, .55): box((.05, .05, 1.0), MATS["steel_dark"], loc=(x, sy, H + 1.5), bev=0, parent=r, name="rail_post")
    for sy in (-.55, .55):
        for z in (H + 1.5, H + 2.0): box((12, .04, .04), MATS["steel_dark"], loc=(0, sy, z), bev=0, parent=r, name="rail")
    for k in range(18): box((.5, .04, .04), MATS["steel"], loc=(-6.7, -.3 + 0, .3 + k * .3), bev=0, parent=r, name="ladder_rung")
    for sx in (-.28, .28): beam((-6.7 + sx * 0, sx, 0), (-6.7, sx, H + 1.0), .05, .04, MATS["steel"], r, "ladder_rail", 0) if False else None
    for sy in (-.25, .25): box((.05, .05, H + 1.0), MATS["steel"], loc=(-6.7, sy - .1, (H + 1.0) / 2), bev=0, parent=r, name="ladder_rail")
    box((.9, 1.7, H), None, loc=(-6, 0, H / 2), bev=0, name="pipe_bridge_12m-convcol"); box((13, 1.4, .5), None, loc=(0, 0, H + .3), bev=0, name="pipe_bridge_deck-convcol")
    empty("ip_use", (-6.7, -1.0, 0), size=.15); empty("ip_hand", (-6.7, -.3, 1.2), size=.08); empty("ip_hit", (0, -2, 0), size=.1)
    done("pipe_bridge_12m")


def pipe_valve_station():
    out("industry"); dmat(); r = empty("pipe_valve_station")
    tube((-2, 0, 1.0), (2, 0, 1.0), .2, MATS["pipe_steel"], r, "pipe", 12)
    for sx in (-1.4, 1.4): box((.3, .6, 1.0), MATS["concrete_gray"], loc=(sx, 0, .5), bev=0, parent=r, name="saddle")
    for x in (-.6, .8):
        cyl(.28, .5, MATS["pipe_orange"], loc=(x, 0, 1.0), seg=12, parent=r, name="valve_body"); cyl(.04, .6, MATS["steel"], loc=(x, 0, 1.55), seg=8, parent=r, name="valve_stem")
        cyl(.25, .04, MATS["paint_red"], loc=(x, 0, 1.85), seg=14, parent=r, name="handwheel")
        for a in range(4): box((.5, .03, .03), MATS["paint_red"], loc=(x, 0, 1.85), bev=0, parent=r, name="wheel_spoke").rotation_euler = (0, 0, a * math.pi / 4)
    cyl(.09, .05, MATS["steel"], loc=(0, -.0, 1.25), seg=12, parent=r, name="gauge_stub"); cyl(.11, .06, MATS["paint_white"], loc=(0, -.0, 1.32), seg=14, parent=r, name="gauge")
    box((4.0, .9, 1.2), None, loc=(0, 0, .8), bev=0, name="pipe_valve_station-convcol"); empty("ip_use", (-.6, -.5, 1.2), size=.12); empty("ip_hand", (.8, -.4, 1.85), size=.08); empty("ip_hit", (0, -1.2, 0), size=.1)
    done("pipe_valve_station")


# ============================================================== chimney
def chimney():
    out("industry"); dmat(); r = empty("chimney_brick_30m"); H = 30.0
    lathe([(0, 0), (2.0, 0), (1.9, 1.0), (1.55, 8), (1.3, 18), (1.05, 26), (.95, 29.4), (1.05, 29.6), (1.05, 30.0), (0, 30.0)], MATS["brick_chimney"], seg=18, parent=r, name="shaft")
    for z0 in (22.0, 25.0, 28.0): lathe([(0, z0), (1.14, z0), (1.14, z0 + 1.3), (0, z0 + 1.3)], MATS["paint_white"], seg=18, parent=r, name="band_white") if z0 < 28 else None
    for z0 in (23.3, 26.3): lathe([(0, z0), (1.1, z0), (1.1, z0 + 1.0), (0, z0 + 1.0)], MATS["paint_red"], seg=18, parent=r, name="band_red")
    box((4.4, 4.4, .6), MATS["concrete_gray"], loc=(0, 0, .3), bev=0, parent=r, name="plinth")
    box((.9, .12, 1.8), MATS["door_steel"], loc=(0, -1.9, 1.5), bev=0, parent=r, name="service_door")
    ok = empty("state_ok")
    for k in range(int(27.5 / .35)):                                  # climbing staples (U-brackets) up the front, bottom at 1.5 m
        z = 1.5 + k * .35; rad = 1.95 - (z / H) * .95 if z < 29 else 1.0
        box((.32, .03, .03), MATS["steel_dark"], loc=(0, -rad - .15, z), bev=0, parent=ok, name="staple_rung")
        for sx in (-.16, .16): box((.03, .15, .03), MATS["steel_dark"], loc=(sx, -rad - .075, z), bev=0, parent=ok, name="staple_leg")
    lo = empty("state_loose")
    for k in range(int(27.5 / .35)):
        z = 1.5 + k * .35; rad = 1.95 - (z / H) * .95 if z < 29 else 1.0
        if k in (14, 15): continue
        box((.32, .03, .03), MATS["steel_dark"], loc=(0, -rad - .15, z), bev=0, parent=lo, name="staple_rung")
        for sx in (-.16, .16): box((.03, .15, .03), MATS["steel_dark"], loc=(sx, -rad - .075, z), bev=0, parent=lo, name="staple_leg")
    z = 1.5 + 14 * .35; rad = 1.95 - (z / H) * .95
    box((.32, .03, .03), MATS["rusty"], loc=(0, -rad - .3, z - .04), bev=0, rot=(.5, 0, 0), parent=lo, name="staple_hanging")
    merge(ok, "staples_ok"); merge(lo, "staples_loose")
    tube((0, 0, 30), (0, 0, 33), .03, MATS["steel"], r, "lightning_rod", 6); sphere(.1, MATS["steel"], loc=(0, 0, 33), seg=8, rings=5, parent=r, name="rod_tip")
    merge(r, "chimney_mesh")
    cyl(2.0, H, None, loc=(0, 0, H / 2), seg=16, name="chimney_brick_30m-convcol")
    empty("ip_use", (0, -2.6, 0), size=.15); empty("ip_hand", (0, -2.2, 1.9), size=.08); empty("ip_hit", (0, -3.2, 0), size=.1)
    done("chimney_brick_30m")


# ============================================================== tower crane
def lattice_mast(root, x, y, z0, n, sec=2.4, w=1.6, name="mast"):
    for k in range(n):
        z = z0 + k * sec
        for sx in (-w / 2, w / 2):
            for sy in (-w / 2, w / 2): beam((x + sx, y + sy, z), (x + sx, y + sy, z + sec), .1, .1, MATS["crane_yellow"], root, name + "_leg", 0)
        for (a, b) in (((-1, -1), (1, -1)), ((1, -1), (1, 1)), ((1, 1), (-1, 1)), ((-1, 1), (-1, -1))):
            beam((x + a[0] * w / 2, y + a[1] * w / 2, z + sec), (x + b[0] * w / 2, y + b[1] * w / 2, z + sec), .06, .06, MATS["crane_yellow"], root, name + "_ring", 0)
            beam((x + a[0] * w / 2, y + a[1] * w / 2, z), (x + b[0] * w / 2, y + b[1] * w / 2, z + sec), .05, .05, MATS["crane_yellow"], root, name + "_diag", 0)


def tower_crane():
    out("industry"); dmat(); r = empty("tower_crane_big"); m = empty("mast_static", parent=r); MH = 38.4
    box((6.0, 6.0, 1.2), MATS["concrete_gray"], loc=(0, 0, .6), bev=0, parent=m, name="base_slab")
    for sx in (-2.2, 2.2):
        for sy in (-2.2, 2.2): box((1.2, 1.2, 1.0), MATS["concrete_gray"], loc=(sx, sy, 1.7), bev=0, parent=m, name="ballast_block")
    lattice_mast(m, 0, 0, 1.2, 16)
    for k in range(int(MH / .32)): box((.5, .03, .03), MATS["steel"], loc=(0, -.8 + .02, 1.5 + k * .32), bev=0, parent=m, name="mast_rung")   # climbing ladder on the front face
    for sx in (-.2, .2): box((.03, .03, MH), MATS["steel"], loc=(sx * 1.25, -.8, 1.5 + MH / 2), bev=0, parent=m, name="mast_ladder_rail")
    for z in (14, 26, 39): box((1.8, 1.8, .06), MATS["grating"], loc=(0, 0, z + 1.2), bev=0, parent=m, name="rest_platform")
    sl = empty("slew", (0, 0, MH + 1.2), parent=r, size=.5); jg = empty("jib_group", (0, 0, 0), parent=sl, size=.3)
    cyl(1.1, .5, MATS["steel_dark"], loc=(0, 0, .25), seg=16, parent=jg, name="slew_ring")
    cab = box((1.5, 1.5, 1.7), MATS["crane_yellow"], loc=(0, -1.3, 1.35), bev=.01, parent=jg, name="cab"); box((1.2, .04, .9), MATS["glass_dark"] if "glass_dark" in MATS else mat("glass_dark", (.04, .06, .08), .1), loc=(0, -2.07, 1.5), bev=0, parent=jg, name="cab_window")
    JL = 40.0; Wj = 1.2; Hj = 1.3
    # jib: triangular truss pointing +X at z = 1.2
    for k in range(int(JL / 2.0)):
        x0, x1 = 1.5 + k * 2.0, 1.5 + (k + 1) * 2.0
        top0, top1 = (x0, 0, 1.2 + Hj), (x1, 0, 1.2 + Hj)
        bl0, bl1 = (x0, -Wj / 2, 1.2), (x1, -Wj / 2, 1.2); br0, br1 = (x0, Wj / 2, 1.2), (x1, Wj / 2, 1.2)
        beam(top0, top1, .08, .08, MATS["crane_yellow"], jg, "jib_top", 0); beam(bl0, bl1, .09, .09, MATS["crane_yellow"], jg, "jib_bl", 0); beam(br0, br1, .09, .09, MATS["crane_yellow"], jg, "jib_br", 0)
        beam(bl0, top1, .05, .05, MATS["crane_yellow"], jg, "jib_diag", 0); beam(br0, top1, .05, .05, MATS["crane_yellow"], jg, "jib_diag", 0)
        beam(bl1, br1, .05, .05, MATS["crane_yellow"], jg, "jib_cross", 0)
    box((.3, .3, 1.0), MATS["steel_dark"], loc=(1.6 + JL / 2, 0, 1.0), bev=0, parent=jg, name="trolley_rail_dummy") if False else None
    # counter-jib (-X)
    for k in range(6):
        x0, x1 = -.5 - k * 2.0, -.5 - (k + 1) * 2.0
        beam((x0, 0, 2.2), (x1, 0, 2.2 - .05 * k), .07, .07, MATS["crane_yellow"], jg, "cj_top", 0)
        for sy in (-Wj / 2, Wj / 2): beam((x0, sy, 1.2), (x1, sy, 1.2), .09, .09, MATS["crane_yellow"], jg, "cj_bottom", 0)
        beam((x0, -Wj / 2, 1.2), (x1, 0, 2.2), .05, .05, MATS["crane_yellow"], jg, "cj_diag", 0)
    for k in range(5): box((1.2, 1.0, .7), MATS["concrete_gray"], loc=(-11.5 + k * 1.3, 0, 1.5), bev=0, parent=jg, name="counterweight")
    # A-frame + tie rods
    for sy in (-.5, .5): beam((.5, sy, 2.2), (0, 0, 8.5), .1, .1, MATS["crane_yellow"], jg, "a_frame", 0); beam((-.5, sy, 2.2), (0, 0, 8.5), .1, .1, MATS["crane_yellow"], jg, "a_frame", 0)
    tube((0, 0, 8.5), (24, 0, 2.5), .02, MATS["steel_dark"], jg, "tie_jib", 5); tube((0, 0, 8.5), (-11, 0, 2.2), .02, MATS["steel_dark"], jg, "tie_counter", 5)
    box((.5, .5, .5), MATS["pipe_orange"], loc=(0, 0, 8.6), bev=0, parent=jg, name="beacon_base"); sphere(.2, mat("beacon_red", (.4, .02, .02), .3, 0.0, emit=(1, .05, .03), emit_strength=3), loc=(0, 0, 9.0), seg=10, rings=6, parent=jg, name="beacon")
    merge(m, "mast_mesh"); merge(jg, "jib_mesh")
    # trolley + hook
    tr = empty("trolley", (14.0, 0, 1.2), parent=sl, size=.3)
    box((1.0, 1.0, .35), MATS["steel_dark"], loc=(0, 0, -.18), bev=.01, parent=tr, name="trolley_body")
    cp = empty("cable_pivot", (0, 0, -.35), parent=tr, size=.2); cable = box((.04, .04, 1.0), MATS["steel"], loc=(0, 0, -.5), bev=0, parent=cp, name="cable"); cp.scale = (1, 1, 6)
    hk = empty("hook", (0, 0, -6.35), parent=tr, size=.2)
    box((.5, .35, .4), MATS["crane_yellow"], loc=(0, 0, .0), bev=.01, parent=hk, name="hook_block"); beam((0, 0, -.2), (0, 0, -.55), .06, .06, MATS["steel_dark"], hk, "hook_shank", 0); beam((-.12, 0, -.55), (.12, 0, -.55), .05, .05, MATS["steel_dark"], hk, "hook_bar", 0)
    box((.2, .04, .5), MATS["steel_dark"], loc=(.12, 0, -.65), bev=0, parent=hk, name="hook_tip")
    box((1.6, 1.6, MH), None, loc=(0, 0, 1.2 + MH / 2), bev=0, name="tower_crane_big-convcol"); box((6, 6, 2.0), None, loc=(0, 0, 1.0), bev=0, name="tower_crane_base-convcol")
    empty("ip_use", (0, -1.4, 1.2), size=.15); empty("ip_hand", (0, -.9, 2.0), size=.08); empty("ip_hit", (0, -3.5, 0), size=.1)
    animate(sl, "slew_loop", [(1, dict(rot=(0, 0, 0))), (361, dict(rot=(0, 0, math.pi))), (721, dict(rot=(0, 0, 2 * math.pi)))])
    animate(tr, "trolley_loop", [(1, dict(loc=(6, 0, 1.2))), (241, dict(loc=(36, 0, 1.2))), (481, dict(loc=(6, 0, 1.2)))])
    animate(cp, "hook_up_down_loop", [(1, dict(scale=(1, 1, 6))), (121, dict(scale=(1, 1, 22))), (241, dict(scale=(1, 1, 6)))])
    animate(hk, "hook_up_down_loop", [(1, dict(loc=(0, 0, -6.35))), (121, dict(loc=(0, 0, -22.35))), (241, dict(loc=(0, 0, -6.35)))])
    done("tower_crane_big", anims=True)


# ============================================================== construction site kit
def site():
    out("construction"); dmat(); r = empty("site_fence_panel")
    for sx in (-1.5, 1.5): box((.1, .1, 2.4), MATS["steel_dark"], loc=(sx, 0, 1.2), bev=0, parent=r, name="post")
    box((3.0, .04, 2.0), MATS["sheet_green"], loc=(0, 0, 1.3), bev=0, parent=r, name="sheet")
    for k in range(10): box((.03, .06, 2.0), MATS["sheet_green"], loc=(-1.35 + k * .3, -.01, 1.3), bev=0, parent=r, name="rib")
    box((3.0, .08, .08), MATS["steel_dark"], loc=(0, 0, 2.3), bev=0, parent=r, name="top_rail"); box((3.0, .08, .08), MATS["steel_dark"], loc=(0, 0, .35), bev=0, parent=r, name="bottom_rail")
    box((3.0, .15, 2.4), None, loc=(0, 0, 1.2), bev=0, name="site_fence_panel-convcol"); empty("ip_hand", (0, 0, 2.35), size=.08); empty("ip_hit", (0, -1, 0), size=.1)
    done("site_fence_panel")
    out("construction"); dmat(); r = empty("site_gate")
    for sx in (-3.3, 3.3): box((.2, .2, 2.5), MATS["steel_dark"], loc=(sx, 0, 1.25), bev=0, parent=r, name="gate_post")
    lf = empty("gate_leaf", (-3.0, 0, 0), parent=r, size=.2)
    box((6.0, .05, 2.0), MATS["sheet_green"], loc=(3.0, 0, 1.15), bev=0, parent=lf, name="sheet")
    for z in (.2, 1.0, 2.15): box((6.0, .08, .08), MATS["steel_dark"], loc=(3.0, 0, z), bev=0, parent=lf, name="gate_rail")
    box((.3, .1, .08), MATS["steel"], loc=(5.8, -.08, 1.0), bev=0, parent=lf, name="latch")
    box((6.6, .3, 2.5), None, loc=(0, 0, 1.25), bev=0, name="site_gate-convcol"); empty("ip_use", (5.8 - 3.0, -.5, 1.0), size=.12)
    animate(lf, "open", [(1, dict(loc=(-3.0, 0, 0))), (30, dict(loc=(-8.5, 0, 0)))]); animate(lf, "close", [(1, dict(loc=(-8.5, 0, 0))), (30, dict(loc=(-3.0, 0, 0)))])
    done("site_gate", anims=True)
    out("construction"); dmat(); r = empty("site_trailer")
    box((6.0, 2.4, 2.4), MATS["cabin_blue"], loc=(0, 0, 1.5), bev=.02, parent=r, name="cabin"); box((6.2, 2.6, .12), MATS["steel_dark"], loc=(0, 0, 2.76), bev=0, parent=r, name="roof")
    for sx in (-2.4, 2.4): box((.3, 2.4, .3), MATS["steel_dark"], loc=(sx, 0, .15), bev=0, parent=r, name="skid")
    d_ = empty("door", (-2.0 - .5, -1.22, 1.0), parent=r, size=.1); box((.9, .06, 2.0), MATS["steel_dark"], loc=(.45, 0, 1.0), bev=0, parent=d_, name="door_leaf")
    for sx in (.2, 1.8): box((.9, .06, .9), MATS["building_window"], loc=(sx + .0, -1.21, 1.9), bev=0, parent=r, name="window"); box((1.0, .08, .08), MATS["steel_dark"], loc=(sx, -1.22, 1.43), bev=0, parent=r, name="sill")
    for k in range(3): box((1.0, .35, .22), MATS["wood_pale"], loc=(-2.5, -1.55 - k * .35, .22 * (3 - k) * .5 + .11), bev=0, parent=r, name="step")
    box((.9, .3, .1), MATS["wood_pale"], loc=(-2.5, -1.5, .35), bev=0, parent=r, name="landing") if False else None
    box((6.2, 2.6, 2.9), None, loc=(0, 0, 1.45), bev=0, name="site_trailer-convcol"); empty("ip_use", (-2.0, -2.3, 0), size=.15); empty("ip_hand", (-2.0, -1.4, 1.2), size=.08)
    animate(d_, "open", [(1, dict(rot=(0, 0, 0))), (16, dict(rot=(0, 0, 1.6)))]); animate(d_, "close", [(1, dict(rot=(0, 0, 1.6))), (16, dict(rot=(0, 0, 0)))])
    done("site_trailer", anims=True)
    out("construction"); dmat(); r = empty("concrete_blocks_stack")
    for row, n in enumerate((4, 3, 2)):
        for k in range(n): box((2.4, 1.2, .58), MATS["concrete_gray"], loc=(-(n - 1) * 1.25 / 2 * 0 + (k - (n - 1) / 2) * 1.3, 0, .3 + row * .6), bev=.02, parent=r, name="fbs_block", seg=1) if False else box((2.4, 1.2, .58), MATS["concrete_gray"], loc=(0, (k - (n - 1) / 2) * 1.25, .3 + row * .6), bev=.02, parent=r, name="fbs_block", seg=1)
    box((2.4, 5.2, 1.8), None, loc=(0, 0, .9), bev=0, name="concrete_blocks_stack-convcol"); empty("ip_hand", (0, 0, 1.85), size=.08); empty("ip_hit", (-1.8, 0, 0), size=.1)
    done("concrete_blocks_stack")
    out("construction"); dmat(); r = empty("rebar_pile")
    for k in range(18):
        a = k / 18 * 2 * math.pi; rr = .12 * (k % 3); tube((-1.5, math.cos(a) * rr, .12 + (k % 3) * .06 + math.sin(a) * .05), (1.5, math.cos(a) * rr, .12 + (k % 3) * .06 + math.sin(a) * .05), .008, MATS["rebar"], r, "rebar", 5)
    for sx in (-1.2, 1.2): box((.1, .5, .12), MATS["wood_pale"], loc=(sx, 0, .06), bev=0, parent=r, name="bearer")
    box((3.2, .6, .4), None, loc=(0, 0, .2), bev=0, name="rebar_pile-convcol"); empty("ip_hit", (0, -1, 0), size=.1)
    done("rebar_pile")
    out("construction"); dmat(); r = empty("brick_pallet")
    box((1.2, 1.0, .14), MATS["wood_pale"], loc=(0, 0, .07), bev=0, parent=r, name="pallet")
    for i in range(3):
        for j in range(2): box((.5, .55, .85), MATS["brick_wall"], loc=(-.5 + i * .5, -.28 + j * .56, .57), bev=.01, parent=r, name="brick_stack", seg=1)
    box((1.2, 1.0, 1.0), None, loc=(0, 0, .5), bev=0, name="brick_pallet-convcol"); empty("ip_hand", (0, 0, 1.02), size=.08); empty("ip_hit", (-1, 0, 0), size=.1)
    done("brick_pallet")
    out("construction"); dmat(); r = empty("scaffold_section_6m")
    for sx in (-1.25, 1.25):
        for sy in (-.5, .5): tube((sx, sy, 0), (sx, sy, 6.0), .025, MATS["steel"], r, "standard", 8)
    for z in (.3, 2.3, 4.3, 6.0):
        for sy in (-.5, .5): tube((-1.25, sy, z), (1.25, sy, z), .02, MATS["steel"], r, "ledger", 6)
        for sx in (-1.25, 1.25): tube((sx, -.5, z), (sx, .5, z), .02, MATS["steel"], r, "transom", 6)
    for z in (2.3, 4.3, 6.0): box((2.5, 1.0, .05), MATS["wood_pale"], loc=(0, 0, z + .03), bev=0, parent=r, name="deck_plank")
    for z in (2.3, 4.3, 6.0):
        for zz in (z + .5, z + 1.0):
            if z < 6.0 or True: tube((-1.25, -.5, zz), (1.25, -.5, zz), .02, MATS["steel"], r, "guard_rail", 6)
    for (z0, z1) in ((.3, 2.3), (2.3, 4.3)): tube((-1.25, -.5, z0), (1.25, -.5, z1), .015, MATS["steel"], r, "x_brace", 6); tube((1.25, -.5, z0), (-1.25, -.5, z1), .015, MATS["steel"], r, "x_brace", 6)
    for k in range(20): box((.4, .03, .03), MATS["steel"], loc=(.9, -.58, .5 + k * .3), bev=0, parent=r, name="ladder_rung")
    for sx in (.7, 1.1): box((.03, .03, 6.2), MATS["steel"], loc=(sx, -.58, 3.1), bev=0, parent=r, name="ladder_rail")
    for z in (2.3, 4.3): box((.5, .5, .04), MATS["steel_dark"], loc=(.9, -.5, z + .01), bev=0, parent=r, name="hatch_frame") if False else None
    box((2.6, 1.1, .12), None, loc=(0, 0, 2.35), bev=0, name="scaffold_deck1-convcol"); box((2.6, 1.1, .12), None, loc=(0, 0, 4.35), bev=0, name="scaffold_deck2-convcol"); box((2.6, 1.1, .12), None, loc=(0, 0, 6.05), bev=0, name="scaffold_deck3-convcol")
    empty("ip_use", (.9, -1.0, 0), size=.15); empty("ip_hand", (.9, -.6, 1.2), size=.08); empty("ip_hit", (0, -2, 0), size=.1)
    done("scaffold_section_6m")
    out("construction"); dmat(); r = empty("foundation_pit_8x6")
    for sx in (-5.5, 5.5): box((3.0, 10.0, .3), MATS["clay"], loc=(sx, 0, -.15 + .15), bev=0, parent=r, name="rim_x") if False else None
    box((4.0, 12.0, .3), MATS["clay"], loc=(-6.0, 0, .0), bev=0, parent=r, name="rim_w"); box((4.0, 12.0, .3), MATS["clay"], loc=(6.0, 0, .0), bev=0, parent=r, name="rim_e")
    box((8.0, 3.0, .3), MATS["clay"], loc=(0, -4.5, .0), bev=0, parent=r, name="rim_s"); box((8.0, 3.0, .3), MATS["clay"], loc=(0, 4.5, .0), bev=0, parent=r, name="rim_n")
    box((8.0, 6.0, .2), MATS["clay"], loc=(0, 0, -3.0), bev=0, parent=r, name="pit_floor")
    for sx in (-4, 4): box((.2, 6.0, 3.0), MATS["clay"], loc=(sx, 0, -1.5), bev=0, parent=r, name="pit_wall")
    for sy in (-3, 3): box((8.0, .2, 3.0), MATS["clay"], loc=(0, sy, -1.5), bev=0, parent=r, name="pit_wall")
    for sx in (-.2, .2): box((.05, .08, 3.6), MATS["wood_pale"], loc=(sx + 3.4, -2.9, -1.2), bev=0, parent=r, name="ladder_rail").rotation_euler = (-.12, 0, 0)
    for k in range(10): box((.45, .04, .04), MATS["wood_pale"], loc=(3.4, -2.9 + .0, -2.85 + k * .33), bev=0, parent=r, name="ladder_rung")
    for k in range(8): box((.9, .2, .04), MATS["wood_pale"], loc=(-1.0, 0, .12), bev=0, parent=r, name="plank") if False else None
    box((.6, 6.8, .06), MATS["wood_pale"], loc=(-1.0, 0, .16), bev=0, parent=r, name="plank_bridge")
    for sy in (-3.3, 3.3): box((.1, .1, .3), MATS["wood_pale"], loc=(-1.0, sy, .12), bev=0, parent=r, name="plank_bearer")
    box((4.0, 12.0, .6), None, loc=(-6.0, 0, -.1), bev=0, name="rim_w-convcol"); box((4.0, 12.0, .6), None, loc=(6.0, 0, -.1), bev=0, name="rim_e-convcol")
    box((8.0, 3.0, .6), None, loc=(0, -4.5, -.1), bev=0, name="rim_s-convcol"); box((8.0, 3.0, .6), None, loc=(0, 4.5, -.1), bev=0, name="rim_n-convcol"); box((8.0, 6.0, .4), None, loc=(0, 0, -3.1), bev=0, name="pit_floor-convcol")
    empty("ip_use", (3.4, -3.3, 0), size=.15); empty("ip_hand", (3.4, -3.0, .1), size=.08); empty("ip_hit", (0, -6.5, 0), size=.1)
    done("foundation_pit_8x6")
    out("construction"); dmat(); r = empty("concrete_frame_2f")
    for sx in (-4.5, 0, 4.5):
        for sy in (-3, 3): box((.4, .4, 5.8), MATS["concrete_gray"], loc=(sx, sy, 2.9), bev=0, parent=r, name="column")
    for z in (2.8, 5.6): box((10.0, 7.0, .25), MATS["concrete_gray"], loc=(0, 0, z), bev=0, parent=r, name="slab")
    for sx in (-4.5, 0, 4.5):
        for sy in (-3, 3): box((.4, .4, 1.2), MATS["concrete_gray"], loc=(sx, sy, 6.3), bev=0, parent=r, name="rebar_stub")
    for sx in (-5.0, 5.0):
        for k in range(1): box((.05, 7.0, .05), MATS["pipe_orange"], loc=(sx, 0, 6.3), bev=0, parent=r, name="edge_rail"); box((.05, 7.0, .05), MATS["pipe_orange"], loc=(sx, 0, 5.9), bev=0, parent=r, name="edge_rail")
    for k in range(20): box((.4, .03, .03), MATS["steel"], loc=(5.0, -2.0, 2.9 + .3 + k * .13), bev=0, parent=r, name="ladder_rung") if False else None
    for k in range(18): box((.45, .04, .04), MATS["wood_pale"], loc=(2.2, -3.6, .3 + k * .3), bev=0, parent=r, name="ladder_rung")
    for sx in (1.95, 2.45): box((.05, .06, 5.6), MATS["wood_pale"], loc=(sx, -3.6, 2.9), bev=0, parent=r, name="ladder_rail")
    box((10.0, 7.0, .4), None, loc=(0, 0, 2.8), bev=0, name="slab1-convcol"); box((10.0, 7.0, .4), None, loc=(0, 0, 5.6), bev=0, name="slab2-convcol")
    empty("ip_use", (2.2, -4.2, 0), size=.15); empty("ip_hand", (2.2, -3.65, 1.2), size=.08); empty("ip_hit", (0, -5, 0), size=.1)
    done("concrete_frame_2f")
    out("construction"); dmat(); r = empty("cement_mixer")
    for sx in (-.45, .45): tube((sx, -.5, .15), (sx, .5, .15), .03, MATS["steel_dark"], r, "leg_bar", 6); beam((sx, -.5, .15), (sx * .6, 0, .75), .05, .05, MATS["steel_dark"], r, "leg", 0); beam((sx, .5, .15), (sx * .6, 0, .75), .05, .05, MATS["steel_dark"], r, "leg", 0)
    for sx in (-.45, .45): cyl(.15, .06, MATS["rubber"], loc=(sx, 0, .15), seg=12, rot=(0, math.pi / 2, 0), parent=r, name="wheel")
    d_ = cyl(.5, .9, MATS["mixer_orange"], loc=(0, 0, 1.0), seg=16, r2=.3, rot=(.5, 0, 0), parent=r, name="drum")
    cyl(.32, .08, MATS["steel_dark"], loc=(0, .38, 1.35), seg=16, rot=(.5, 0, 0), parent=r, name="drum_mouth")
    box((1.2, 1.4, 1.5), None, loc=(0, 0, .75), bev=0, name="cement_mixer-convcol"); empty("ip_use", (0, -.9, .5), size=.12); empty("ip_hit", (0, -1.3, 0), size=.1)
    done("cement_mixer")


# ============================================================== janitor cart
def cart():
    global OUTDIR
    OUTDIR = "D:/Faceless/models/city/props"; dmat(); r = empty("janitor_cart")
    for sx in (-.3, .3):
        for sy in (-.45, .45): tube((sx, sy, .15), (sx, sy, .85), .015, MATS["steel"], r, "frame_post", 6)
    for z in (.3, .85):
        for sy in (-.45, .45): tube((-.3, sy, z), (.3, sy, z), .015, MATS["steel"], r, "frame_rail", 6)
        for sx in (-.3, .3): tube((sx, -.45, z), (sx, .45, z), .015, MATS["steel"], r, "frame_rail", 6)
    box((.7, 1.0, .03), MATS["steel"], loc=(0, 0, .3), bev=0, parent=r, name="shelf")
    box((.5, .35, .55), MATS["vinyl_blue"], loc=(0, .2, .6), bev=.02, parent=r, name="bag", taper=.9)
    box((.5, .4, .3), MATS["bucket_yellow"], loc=(0, -.22, .47), bev=.02, parent=r, name="mop_bucket", taper=.85)
    box((.2, .2, .12), MATS["steel_dark"], loc=(0, -.22, .67), bev=0, parent=r, name="wringer")
    for sx in (-.3, .3):
        for sy in (-.4, .4): cyl(.08, .04, MATS["rubber"], loc=(sx, sy, .08), seg=12, rot=(0, math.pi / 2, 0), parent=r, name="wheel")
    tube((.0, .5, .85), (0, .62, 1.05), .015, MATS["steel"], r, "handle_arm", 6); tube((-.25, .62, 1.05), (.25, .62, 1.05), .018, MATS["steel"], r, "handle_bar", 6)
    tube((-.22, -.18, .62), (-.34, .3, 1.55), .012, MATS["wood_pale"], r, "mop_stick", 6); sphere(.07, mat("mop_head", (.5, .5, .48), .95), loc=(-.22, -.18, .6), seg=8, rings=5, scale=(1, 1, .7), parent=r, name="mop_head")
    tube((.22, -.18, .62), (.34, .3, 1.5), .012, MATS["wood_pale"], r, "broom_stick", 6); box((.28, .06, .1), MATS["wood_pale"], loc=(.22, -.18, .6), bev=0, parent=r, name="broom_head")
    box((.3, .02, .4), MATS["wet_floor"], loc=(0, -.5, .75), bev=0, parent=r, name="wet_sign").rotation_euler = (.3, 0, 0) if False else (0, 0, 0)
    box((.8, 1.2, 1.0), None, loc=(0, 0, .5), bev=0, name="janitor_cart-convcol"); empty("ip_hand", (0, .62, 1.05), size=.08); empty("ip_use", (0, 1.0, .5), size=.12)
    done("janitor_cart")


GRP = os.environ.get("GRP", "all")
for k, f in (("pipes", lambda: (pipe_rack_6m(), pipe_bridge_12m(), pipe_valve_station())), ("chimney", chimney), ("crane", tower_crane), ("site", site), ("cart", cart)):
    if GRP in ("all", k): f()
