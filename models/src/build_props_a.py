"""Street furniture, stage 3 (part A): street lamp, bench, urn, dumpster, bus stop, billboard, ad column, phone booth, traffic lights, power pole, street/road signs.
Run: D:\\Cosmoteer\\blender.exe -b -P build_props_a.py -> models/city/props/*.glb"""
_s = open("D:/Faceless/models/src/build_p2.py", encoding="utf-8").read()
exec(_s[:_s.index("# ======================================================================= stepladder")])
import os
OUTDIR = "D:/Faceless/models/city/props"; os.makedirs(OUTDIR, exist_ok=True)
def pnew():
    new(); mat("lamp_red", (.4, .02, .02), .3, 0.0, emit=(1, .05, .03), emit_strength=2.5); mat("lamp_amber", (.5, .25, .02), .3, 0.0, emit=(1, .55, .05), emit_strength=2.5)
    mat("lamp_green", (.02, .4, .1), .3, 0.0, emit=(.1, 1, .25), emit_strength=2.5); mat("lamp_head", (.6, .55, .4), .2, 0.0, emit=(1, .9, .6), emit_strength=2.5)
    mat("sign_blue", (.03, .1, .3), .5); mat("sign_red", (.4, .03, .03), .5); mat("sign_white", (.55, .55, .5), .5); mat("poster", (.5, .45, .35), .9)
    mat("billboard_panel", (.45, .45, .45), .8); mat("green_paint", (.08, .16, .1), .7); mat("blue_paint", (.06, .1, .2), .7); mat("glass_light", (.5, .6, .62), .1)
    mat("pole_concrete", (.33, .33, .31), .95); mat("insulator", (.4, .45, .4), .4)

# ------------------------------------------------------------------ street lamp (ok / broken)
def street_lamp():
    pnew(); ST = MATS["steel_dark"]
    base = empty("lamp_base")
    cyl(.14, .15, ST, loc=(0, 0, .075), seg=10, parent=base, name="foot"); cyl(.09, 5.4, MATS["paint_gray"], loc=(0, 0, 2.85), seg=10, parent=base, name="pole", r2=.055)
    merge(base, "pole_mesh")
    so = empty("state_ok")
    tube((0, 0, 5.5), (-.55, 0, 5.75), .04, ST, so, "arm"); tube((-.55, 0, 5.75), (-1.0, 0, 5.7), .035, ST, so, "arm2")
    box((.55, .26, .12), ST, loc=(-1.05, 0, 5.62), bev=.02, parent=so, name="lamp_housing"); box((.48, .2, .04), MATS["lamp_head"], loc=(-1.05, 0, 5.55), bev=.004, parent=so, name="lamp_glass")
    merge(so, "ok_mesh")
    sb = empty("state_broken")
    tube((0, 0, 5.5), (-.55, 0, 5.6), .04, ST, sb, "arm_bent"); beam((-.55, 0, 5.6), (-.9, 0, 4.6), .05, .05, ST, sb, "arm_hanging"); box((.5, .24, .1), ST, loc=(-.95, 0, 4.5), bev=.02, parent=sb, name="lamp_housing_fallen").rotation_euler = (0, .6, 0)
    merge(sb, "broken_mesh")
    box((.4, .4, 5.8), None, loc=(0, 0, 2.9), bev=0, name="street_lamp-col")
    empty("ip_use", (.8, 0, 0), size=.15); empty("ip_hit", (-1.0, 0, 0), size=.15); empty("ip_spark", (-1.05, 0, 5.55), size=.1)
    done("street_lamp")

def bench():
    pnew(); ST = MATS["steel_dark"]; W_ = MATS["wood"]
    ok = empty("state_ok")
    for sx in (-.7, .7):
        box((.05, .5, .05), ST, loc=(sx, 0, .22), bev=.004, parent=ok, name="frame_leg_a"); beam((sx, -.2, .2), (sx, -.28, .85), .05, .04, ST, ok, "frame_back", .004); beam((sx, .2, .2), (sx, .26, .45), .05, .04, ST, ok, "arm_rest", .004)
    for i in range(4): box((1.6, .09, .04), W_, loc=(0, -.17 + i * .11, .45), bev=.006, parent=ok, name="seat_slat")
    for i in range(3): box((1.6, .035, .1), W_, loc=(0, -.27, .62 + i * .13), bev=.006, parent=ok, name="back_slat")
    merge(ok, "ok_mesh")
    br = empty("state_broken")
    for sx in (-.7, .7): box((.05, .5, .05), ST, loc=(sx, 0, .22), bev=.004, parent=br, name="frame_leg_a"); beam((sx, -.2, .2), (sx, -.28, .85), .05, .04, ST, br, "frame_back", .004)
    for i in (0, 2, 3): box((1.6, .09, .04), W_, loc=(0, -.17 + i * .11, .45), bev=.006, parent=br, name="seat_slat")
    box((.9, .09, .04), W_, loc=(-.3, -.08, .25), bev=.006, parent=br, name="seat_slat_broken").rotation_euler = (.0, .5, .3)
    for i in (0, 2): box((1.6, .035, .1), W_, loc=(0, -.27, .62 + i * .13), bev=.006, parent=br, name="back_slat")
    merge(br, "broken_mesh")
    box((1.7, .7, .9), None, loc=(0, 0, .45), bev=0, name="bench-convcol"); empty("ip_use", (0, -.9, 0), size=.15); empty("ip_hand", (0, 0, .5), size=.08)
    done("bench")

def urn():
    pnew(); ST = MATS["steel_dark"]
    b = empty("urn")
    lathe([(0, 0), (.2, 0), (.22, .02), (.2, .6), (.0, .6)], MATS["concrete_dark"], parent=b, seg=14, name="body")
    lathe([(.0, .6), (.23, .6), (.24, .66), (.1, .7), (0, .7)], ST, parent=b, seg=14, name="rim")
    for k in range(4): box((.02, .2, .3), ST, loc=(math.cos(k * 1.57) * .2, math.sin(k * 1.57) * .2, .3), bev=0, parent=b, name="band") if False else None
    merge(b, "urn_mesh")
    box((.5, .5, .7), None, loc=(0, 0, .35), bev=0, name="urn-convcol"); empty("ip_use", (0, -.6, 0), size=.12); empty("ip_hand", (0, 0, .7), size=.08)
    done("urn_street")

def dumpster():
    pnew(); G = MATS["green_paint"]
    ok = empty("state_ok")
    box((1.8, 1.1, 1.05), G, loc=(0, 0, .72), bev=.02, parent=ok, name="body", seg=2, taper=.9)
    box((1.82, 1.12, .12), MATS["steel_dark"], loc=(0, 0, 1.25), bev=.01, parent=ok, name="rim")
    for sx in (-.85, 0, .85): box((.06, 1.14, .08), MATS["steel_dark"], loc=(sx, 0, .7), bev=0, parent=ok, name="rib")
    for sx in (-.75, .75):
        cyl(.075, .05, ST := MATS["rubber"], loc=(sx, .45, .1), seg=10, rot=(0, math.pi / 2, 0), parent=ok, name="wheel")
        cyl(.075, .05, ST, loc=(sx, -.45, .1), seg=10, rot=(0, math.pi / 2, 0), parent=ok, name="wheel")
    lid = empty("lid", (0, .55, 1.31), parent=ok, size=.1)
    box((1.8, 1.12, .05), MATS["steel_dark"], loc=(0, -.56, 0), bev=.01, parent=lid, name="lid_plate")
    merge(ok, "ok_mesh")
    # animation: lid opens
    lid2 = empty("lid_anim", (0, .55, 1.31), size=.1); box((1.8, 1.12, .05), MATS["steel_dark"], loc=(0, -.56, 0), bev=.01, parent=lid2, name="lid_plate2"); merge(lid2, "lid_mesh")
    animate(lid2, "open", [(1, dict(rot=(0, 0, 0))), (14, dict(rot=(1.6, 0, 0)))]); animate(lid2, "close", [(1, dict(rot=(1.6, 0, 0))), (14, dict(rot=(0, 0, 0)))])
    box((1.9, 1.2, 1.35), None, loc=(0, 0, .68), bev=0, name="dumpster-convcol"); empty("ip_use", (0, -1.0, 0), size=.15); empty("ip_hand", (0, -.6, 1.3), size=.08)
    done("dumpster", anims=True)

def bus_stop():
    pnew(); ST = MATS["steel_dark"]
    r = empty("bus_stop")
    for sx in (-1.3, 1.3): box((.07, .07, 2.5), ST, loc=(sx, .5, 1.25), bev=.005, parent=r, name="post"); box((.07, .07, 2.5), ST, loc=(sx, -.5, 1.25), bev=.005, parent=r, name="post")
    box((3.1, 1.3, .08), MATS["blue_paint"], loc=(0, 0, 2.55), bev=.01, parent=r, name="roof"); box((3.1, .04, 1.9), MATS["glass_light"], loc=(0, .62, 1.4), bev=0, parent=r, name="back_glass")
    for sx in (-1.3, 1.3): box((.04, 1.2, 1.5), MATS["glass_light"], loc=(sx, 0, 1.45), bev=0, parent=r, name="side_glass")
    box((2.4, .4, .06), MATS["wood"], loc=(0, .38, .5), bev=.01, parent=r, name="seat"); box((.06, .35, .5), ST, loc=(-1.0, .38, .25), bev=.004, parent=r, name="seat_leg"); box((.06, .35, .5), ST, loc=(1.0, .38, .25), bev=.004, parent=r, name="seat_leg")
    cyl(.03, 3.4, ST, loc=(1.9, -.7, 1.7), seg=8, parent=r, name="sign_pole"); cyl(.28, .03, MATS["sign_blue"], loc=(1.9, -.7, 3.2), seg=16, rot=(math.pi / 2, 0, 0), parent=r, name="sign_disc"); box((.04, .02, .3), MATS["sign_white"], loc=(1.9, -.72, 3.2), bev=0, parent=r, name="sign_letter")
    box((.6, .02, .9), MATS["poster"], loc=(-1.0, .6, 1.4), bev=0, parent=r, name="timetable")
    merge(r, "stop_mesh")
    box((3.2, 1.4, 2.6), None, loc=(0, 0, 1.3), bev=0, name="bus_stop-convcol"); empty("ip_use", (0, -1.2, 0), size=.15)
    done("bus_stop")

def billboard():
    pnew(); ST = MATS["steel_dark"]
    r = empty("billboard")
    for sx in (-1.8, 1.8): box((.2, .2, 4.0), MATS["paint_gray"], loc=(sx, 0, 2.0), bev=.01, parent=r, name="post")
    box((5.2, .14, .12), ST, loc=(0, 0, 3.0), bev=.005, parent=r, name="brace"); box((6.0, .14, 3.0), ST, loc=(0, -.12, 4.6), bev=.01, parent=r, name="frame")
    box((5.7, .06, 2.7), MATS["billboard_panel"], loc=(0, -.2, 4.6), bev=0, parent=r, name="panel")
    for sx in (-2.0, 0, 2.0): box((.06, .3, .06), ST, loc=(sx, -.3, 6.2), bev=0, parent=r, name="lamp_arm"); sphere(.06, MATS["lamp_head"], loc=(sx, -.45, 6.2), seg=8, rings=5, parent=r, name="floodlight")
    merge(r, "billboard_mesh")
    box((.5, .5, 4.0), None, loc=(-1.8, 0, 2.0), bev=0, name="billboard-col"); box((.5, .5, 4.0), None, loc=(1.8, 0, 2.0), bev=0, name="billboard_b-col"); empty("ip_use", (0, -1.0, 0), size=.15)
    done("billboard")

def ad_column():
    pnew()
    r = empty("ad_column")
    lathe([(0, 0), (.62, 0), (.6, .1), (.58, .3), (.58, 2.55), (.62, 2.6), (.58, 2.75), (.3, 2.95), (.0, 3.05)], MATS["paint_green"] if "paint_green" in MATS else MATS["paint_gray"], parent=r, seg=20, name="column")
    lathe([(.585, .45), (.59, .45), (.59, 2.4), (.585, 2.4)], MATS["poster"], parent=r, seg=20, name="posters")
    lathe([(0, 3.05), (.06, 3.05), (.06, 3.2), (0, 3.2)], MATS["steel_dark"], parent=r, seg=8, name="finial")
    merge(r, "ad_mesh")
    box((1.3, 1.3, 3.0), None, loc=(0, 0, 1.5), bev=0, name="ad_column-convcol"); empty("ip_use", (0, -1.0, 0), size=.15)
    done("ad_column")

def phone_booth():
    pnew(); ST = MATS["steel_dark"]; RD = mat("booth_red", (.35, .04, .04), .6)
    r = empty("phone_booth")
    for sx in (-.4, .4):
        for sy in (-.4, .4): box((.05, .05, 2.2), RD, loc=(sx, sy, 1.1), bev=.004, parent=r, name="post")
    box((.9, .9, .1), RD, loc=(0, 0, 2.25), bev=.01, parent=r, name="roof"); box((.9, .9, .08), MATS["concrete_dark"], loc=(0, 0, .04), bev=.004, parent=r, name="floor")
    for sx in (-.4, .4): box((.02, .8, 1.5), MATS["glass_light"], loc=(sx, 0, 1.3), bev=0, parent=r, name="side_glass")
    box((.8, .02, 1.5), MATS["glass_light"], loc=(0, .4, 1.3), bev=0, parent=r, name="back_glass")
    box((.5, .16, .5), MATS["paint_gray"], loc=(0, .32, 1.3), bev=.02, parent=r, name="phone_box"); box((.3, .02, .12), MATS["lamp_green"], loc=(0, .24, 1.45), bev=0, parent=r, name="phone_display")
    box((.06, .04, .22), ST, loc=(-.24, .26, 1.3), bev=.01, parent=r, name="handset"); tube((.2, .24, 1.1), (.3, .24, .9), .006, ST, r, "cord", 4)
    merge(r, "booth_mesh")
    box((.9, .9, 2.3), None, loc=(0, 0, 1.15), bev=0, name="phone_booth-convcol"); empty("ip_use", (0, -.8, 0), size=.15); empty("ip_hand", (0, .22, 1.2), size=.08)
    done("phone_booth")

def traffic_light(kind):
    pnew(); ST = MATS["paint_gray"]; H_ = 3.6 if kind == "car" else 2.7
    r = empty("traffic_light")
    cyl(.07, H_, ST, loc=(0, 0, H_ / 2), seg=10, parent=r, name="pole"); cyl(.15, .1, MATS["steel_dark"], loc=(0, 0, .05), seg=10, parent=r, name="foot")
    n = 3 if kind == "car" else 2
    box((.34, .26, .34 * n * .82 + .1), MATS["black_paint"], loc=(0, -.17, H_ - .1 - (.34 * n * .82 + .1) / 2 + .1), bev=.02, parent=r, name="head")
    colors = ("lamp_red", "lamp_amber", "lamp_green") if kind == "car" else ("lamp_red", "lamp_green")
    for i, cm in enumerate(colors):
        z = H_ - .08 - i * .3
        cyl(.1, .03, MATS[cm], loc=(0, -.31, z), seg=14, rot=(math.pi / 2, 0, 0), parent=r, name="lamp_" + cm[5:])
        box((.24, .08, .1), MATS["black_paint"], loc=(0, -.33, z + .1), bev=.01, parent=r, name="visor")
    if kind == "car": box((.7, .02, .1), MATS["sign_white"], loc=(0, .0, 2.5), bev=0, parent=r, name="id_plate")
    merge(r, "light_mesh")
    box((.4, .4, H_), None, loc=(0, 0, H_ / 2), bev=0, name="traffic_light-col"); empty("ip_use", (.8, 0, 0), size=.15); empty("ip_spark", (0, -.31, H_ - .08), size=.1)
    done("traffic_light_car" if kind == "car" else "traffic_light_ped")

def power_pole():
    pnew(); ST = MATS["steel_dark"]
    r = empty("power_pole")
    cyl(.17, 9.0, MATS["pole_concrete"], loc=(0, 0, 4.5), seg=12, r2=.13, parent=r, name="pole")
    box((2.2, .12, .14), MATS["wood"], loc=(0, 0, 8.4), bev=.01, parent=r, name="crossarm"); box((1.5, .1, .12), MATS["wood"], loc=(0, 0, 7.4), bev=.01, parent=r, name="crossarm_low")
    for x in (-.95, -.4, .4, .95):
        cyl(.04, .2, MATS["insulator"], loc=(x, 0, 8.55), seg=8, parent=r, name="insulator")
    for x in (-.6, 0, .6): cyl(.04, .2, MATS["insulator"], loc=(x, 0, 7.55), seg=8, parent=r, name="insulator_low")
    for k in range(3): beam((0, .1, 8.3 - k * .3), (0, .3, 7.6 - k * .35), .05, .02, ST, r, "climb_step", .002)
    merge(r, "pole_mesh")
    box((.4, .4, 9.0), None, loc=(0, 0, 4.5), bev=0, name="power_pole-col"); empty("ip_use", (.7, 0, 0), size=.15); empty("ip_hit", (0, 0, 8.4), size=.15); empty("ip_spark", (-.95, 0, 8.55), size=.1)
    done("power_pole")

def signs():
    for nm, shape, border, fill in (("sign_stop", 8, "sign_red", "sign_red"), ("sign_yield", 3, "sign_red", "sign_white"), ("sign_noentry", 16, "sign_red", "sign_red"), ("sign_crossing", 4, "sign_white", "sign_blue"), ("sign_speed", 16, "sign_red", "sign_white"), ("sign_street", 4, "sign_white", "sign_blue")):
        pnew(); r = empty(nm)
        cyl(.03, 2.6, MATS["steel_dark"], loc=(0, 0, 1.3), seg=8, parent=r, name="pole")
        if shape == 4 and nm == "sign_street": box((.6, .02, .22), MATS[fill], loc=(0, -.04, 2.45), bev=.003, parent=r, name="plate"); box((.55, .02, .03), MATS["sign_white"], loc=(0, -.05, 2.45), bev=0, parent=r, name="text_line")
        elif shape == 4: box((.5, .02, .5), MATS[fill], loc=(0, -.04, 2.35), bev=.005, parent=r, name="plate").rotation_euler = (0, 0, 0); poly_prism([(-.08, -.12), (.08, -.12), (0, .1)], .01, MATS["black_paint"], loc=(0, -.05, 2.35), parent=r, name="glyph").rotation_euler = (math.pi / 2, 0, 0)
        elif shape == 3:
            tri = poly_prism([(-.38, -.22), (.38, -.22), (0, .44)], .02, MATS["sign_red"], loc=(0, -.04, 2.32), parent=r, name="plate_red"); tri.rotation_euler = (math.pi / 2, 0, 0)
            tri2 = poly_prism([(-.28, -.16), (.28, -.16), (0, .31)], .02, MATS["sign_white"], loc=(0, -.055, 2.34), parent=r, name="plate_white"); tri2.rotation_euler = (math.pi / 2, 0, 0)
        else:
            cyl(.3, .02, MATS[border], loc=(0, -.04, 2.35), seg=shape if shape == 8 else 20, rot=(math.pi / 2, 0, 0), parent=r, name="plate_border")
            cyl(.22, .02, MATS[fill], loc=(0, -.055, 2.35), seg=shape if shape == 8 else 20, rot=(math.pi / 2, 0, 0), parent=r, name="plate_fill")
            if nm == "sign_noentry": box((.36, .01, .07), MATS["sign_white"], loc=(0, -.066, 2.35), bev=0, parent=r, name="bar")
        merge(r, nm + "_mesh")
        box((.2, .2, 2.6), None, loc=(0, 0, 1.3), bev=0, name=nm + "-col"); empty("ip_use", (.6, 0, 0), size=.12)
        done(nm)

street_lamp(); bench(); urn(); dumpster(); bus_stop(); billboard(); ad_column(); phone_booth(); traffic_light("car"); traffic_light("ped"); power_pole(); signs()
