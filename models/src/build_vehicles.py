"""Vehicles of the 90s city: VAZ-like sedan, wagon, Moskvich-like, roof-rack sedan, van (Gazelle-like), truck, bus, trolleybus, ambulance, police car, tow truck.
Run: VEH=<name|all> D:\\Cosmoteer\\blender.exe -b -P build_vehicles.py -> models/city/vehicles/<name>.glb
Conventions: metres, front = -Y in Blender (+Z in glTF), origin at ground centre, left side = +X (Blender). Wheels are separate nodes (wheel_fl/fr/rl/rr...) with the origin at the hub, animation drive_loop spins them.
Lights: emissive materials lamp_head / lamp_tail / lamp_amber / lamp_beacon (game toggles emission). Collision: <name>-convcol."""
import os
exec(open("D:/Faceless/models/src/lib_props.py", encoding="utf-8").read())
OUT = "D:/Faceless/models/city/vehicles"; os.makedirs(OUT, exist_ok=True)
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


def veh_mats(body=(.12, .14, .17), body2=None):
    palette()
    mat("paint_body", body, .45, .25); mat("paint_body2", body2 or (.5, .5, .48), .45, .25)
    mat("glass_car", (.03, .045, .055), .08, 0.0); mat("chrome", (.5, .52, .55), .25, .95); mat("trim_black", (.015, .015, .018), .7)
    mat("tire", (.012, .012, .014), .9); mat("rim_steel", (.28, .3, .32), .4, .8); mat("plate_white", (.55, .55, .5), .5); mat("seat_cloth", (.1, .07, .05), .9)
    mat("lamp_head", (.6, .55, .4), .2, 0.0, emit=(1.0, .9, .6), emit_strength=2.0); mat("lamp_tail", (.4, .02, .02), .3, 0.0, emit=(1.0, .05, .03), emit_strength=2.0)
    mat("lamp_amber", (.5, .25, .02), .3, 0.0, emit=(1.0, .55, .05), emit_strength=2.0); mat("lamp_white", (.5, .5, .5), .3, 0.0, emit=(1, 1, 1), emit_strength=1.5)
    mat("lamp_beacon_blue", (.02, .05, .4), .3, 0.0, emit=(.1, .25, 1.0), emit_strength=4.0); mat("lamp_beacon_red", (.4, .02, .02), .3, 0.0, emit=(1.0, .05, .03), emit_strength=4.0)
    mat("stripe_blue", (.04, .08, .3), .5); mat("stripe_yellow", (.5, .38, .03), .5); mat("stripe_red", (.4, .03, .03), .5); mat("body_white", (.55, .55, .52), .45, .2)
    mat("wood_deck", (.2, .13, .07), .85); mat("rubber_black", (.02, .02, .02), .9)

def side_prism(profile, xh, taper=1.0, material=None, name="prism", bev=.02, loc=(0, 0, 0), z0=None, z1=None, parent=None):
    """profile: [(y, z)] polygon in the YZ plane, extruded over x in [-xh, xh]; vertices above z0 narrow towards `taper` at z1 (tumblehome)."""
    bm = bmesh.new(); vs = [bm.verts.new((-xh, y, z)) for y, z in profile]; f = bm.faces.new(vs)
    r = bmesh.ops.extrude_face_region(bm, geom=[f]); vv = [e for e in r['geom'] if isinstance(e, bmesh.types.BMVert)]
    bmesh.ops.translate(bm, verts=vv, vec=(2 * xh, 0, 0))
    zs = [p[1] for p in profile]; z0 = min(zs) if z0 is None else z0; z1 = max(zs) if z1 is None else z1
    for v in bm.verts: v.co.x *= 1 + (taper - 1) * max(0.0, min(1.0, (v.co.z - z0) / max(1e-6, (z1 - z0))))
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    if bev: bevel(bm, bev, 2)
    return mesh_obj(name, bm, material, loc, parent=parent)

def wheel(name, r, w, x, y, z, parent=None, dual=False):
    hub = empty(name, (x, y, z), parent=parent, size=.1)
    lathe([(r * .55, -w / 2), (r * .95, -w / 2 + .02), (r, -w * .35), (r, w * .35), (r * .95, w / 2 - .02), (r * .55, w / 2), (r * .55, -w / 2)], MATS["tire"], parent=hub, seg=18, name=name + "_tire", rot=(0, math.pi / 2, 0))
    lathe([(0, -w * .38), (r * .56, -w * .38), (r * .56, w * .4), (r * .2, w * .44), (0, w * .44)], MATS["rim_steel"], parent=hub, seg=14, name=name + "_rim", rot=(0, math.pi / 2, 0))
    lathe([(0, w * .44), (r * .16, w * .44), (r * .16, w * .5), (0, w * .52)], MATS["chrome"], parent=hub, seg=10, name=name + "_cap", rot=(0, math.pi / 2, 0))
    box((.02, r * .3, r * .1), MATS["rim_steel"], loc=(0, 0, 0), bev=0, parent=hub, name=name + "_nut") if False else None
    return hub

def plate(parent, loc, front=True):
    box((.52, .012, .12), MATS["plate_white"], loc=loc, bev=.002, parent=parent, name="plate")
    for k in range(5): box((.045, .006, .07), MATS["trim_black"], loc=(loc[0] - .18 + k * .09, loc[1] + (-.008 if front else .008), loc[2]), bev=0, parent=parent, name="plate_char")

def finish_car(name, spin_wheels, size, anims=True):
    # simplified collider: one convex box
    smooth_angle([o for o in bpy.data.objects if o.type == 'MESH'], 40)
    L_, W_, H_ = size
    box((W_, L_, H_ * .85), None, loc=(0, 0, H_ * .5), bev=0, name=f"{name}-convcol")
    if spin_wheels:
        for w in spin_wheels: animate(w, "drive_loop", [(1, dict(rot=(0, 0, 0))), (13, dict(rot=(math.pi, 0, 0))), (25, dict(rot=(2 * math.pi, 0, 0)))])
    empty("ip_use", (W_ / 2 + .5, .1, 0), size=.2)           # driver door (left side, +X)
    empty("ip_hit", (0, -L_ / 2 - .3, .6), size=.2)
    empty("ip_hand", (W_ / 2 + .05, .1, .95), size=.1)      # door handle
    return export(name, anims=bool(spin_wheels), out_dir=OUT)

# ============================================================================= passenger cars
def car(name, kind="sedan", body=(.12, .14, .17), L=4.17, W=1.66, H=1.42, livery=None, roof_rack=False, beacon=None):
    fresh(); veh_mats(body)
    B, G, CH, TR = MATS["paint_body"], MATS["glass_car"], MATS["chrome"], MATS["trim_black"]
    sl, sw, sh = L / 4.17, W / 1.66, H / 1.42
    def P(pts): return [(y * sl, z * sh) for y, z in pts]
    root = empty("car_body", size=.2)
    # lower body (tub + hood + trunk)
    low = P([(-2.04, .32), (2.0, .32), (2.05, .55), (2.02, .9), (1.2, .95), (-.78, .95), (-1.95, .86), (-2.06, .72)])
    side_prism(low, .8 * sw, .93, B, "lower", bev=.03, parent=root)
    # greenhouse
    if kind == "wagon":
        cab = P([(-.78, .94), (-.42, 1.38), (1.25, 1.4), (1.62, .94)]); cabw = .66
    elif kind == "moskvich":
        cab = P([(-.7, .94), (-.35, 1.42), (1.05, 1.44), (1.38, .94)]); cabw = .66
    else:
        cab = P([(-.74, .94), (-.4, 1.38), (.95, 1.39), (1.3, .94)]); cabw = .66
    side_prism(cab, cabw * sw, .9, G, "greenhouse", bev=.01, parent=root)
    # body-colour roof slab, pillars and sill
    y_roof0, y_roof1 = cab[1][0], cab[2][0]
    box((2 * (cabw * .9 + .02) * sw, abs(y_roof1 - y_roof0) + .1, .06), B, loc=(0, (y_roof0 + y_roof1) / 2, cab[1][1] + .01), bev=.02, parent=root, name="roof")
    for sx in (-1, 1):
        a0, a1 = Vector((sx * cabw * sw * .98, cab[0][0], cab[0][1])), Vector((sx * cabw * sw * .9, cab[1][0], cab[1][1]))
        beam((a0.x, a0.y, a0.z), (a1.x, a1.y, a1.z), .05, .05, B, root, "pillar_A", .008)
        c0, c1 = Vector((sx * cabw * sw * .98, cab[3][0], cab[3][1])), Vector((sx * cabw * sw * .9, cab[2][0], cab[2][1]))
        beam((c0.x, c0.y, c0.z), (c1.x, c1.y, c1.z), .06, .05, B, root, "pillar_C", .008)
        ymid = (cab[1][0] + cab[2][0]) * .45
        beam((sx * cabw * sw * .95, ymid, cab[0][1]), (sx * cabw * sw * .9, ymid, cab[1][1] - .02), .05, .04, B, root, "pillar_B", .006)
        box((.02, abs(cab[3][0] - cab[0][0]) * .92, .045), CH, loc=(sx * (.81 * sw), (cab[0][0] + cab[3][0]) / 2, .62 * sh), bev=.004, parent=root, name="side_molding")
        for yy in (-.2 * sl, .6 * sl):                                    # door seams
            box((.012, .01, .5 * sh), TR, loc=(sx * (.815 * sw), yy, .64 * sh), bev=0, parent=root, name="door_seam")
        box((.02, .13, .03), CH, loc=(sx * .82 * sw, -.05 * sl, .8 * sh), bev=.004, parent=root, name="door_handle")
        box((.02, .13, .03), CH, loc=(sx * .82 * sw, .75 * sl, .8 * sh), bev=.004, parent=root, name="door_handle")
        tube((sx * .7 * sw, -.62 * sl, 1.0 * sh), (sx * .9 * sw, -.55 * sl, 1.04 * sh), .008, TR, root, "mirror_arm", 6)
        box((.05, .1, .08), TR, loc=(sx * .93 * sw, -.55 * sl, 1.05 * sh), bev=.012, parent=root, name="mirror")
    # bumpers, grille, lamps, plates
    box((W * .98, .12, .12), CH, loc=(0, -2.09 * sl, .42 * sh), bev=.025, parent=root, name="bumper_f")
    box((W * .98, .12, .12), CH, loc=(0, 2.07 * sl, .42 * sh), bev=.025, parent=root, name="bumper_r")
    box((.76 * sw, .02, .16 * sh), TR, loc=(0, -2.065 * sl, .76 * sh), bev=.006, parent=root, name="grille")
    for k in range(5): box((.7 * sw, .008, .006), CH, loc=(0, -2.078 * sl, .70 * sh + k * .03 * sh), bev=0, parent=root, name="grille_bar")
    for sx in (-1, 1):
        cyl(.075 * sw, .05, MATS["lamp_head"], loc=(sx * .55 * sw, -2.05 * sl, .8 * sh), seg=14, rot=(math.pi / 2, 0, 0), parent=root, name="headlight")
        cyl(.09 * sw, .02, CH, loc=(sx * .55 * sw, -2.07 * sl, .8 * sh), seg=14, rot=(math.pi / 2, 0, 0), parent=root, name="headlight_rim")
        box((.12, .02, .05), MATS["lamp_amber"], loc=(sx * .72 * sw, -2.06 * sl, .66 * sh), bev=.004, parent=root, name="indicator_f")
        box((.2, .02, .12 * sh), MATS["lamp_tail"], loc=(sx * .62 * sw, 2.03 * sl, .83 * sh), bev=.006, parent=root, name="taillight")
        box((.08, .015, .05), MATS["lamp_white"], loc=(sx * .39 * sw, 2.045 * sl, .8 * sh), bev=.004, parent=root, name="reverse_light")
    plate(root, (0, -2.12 * sl, .42 * sh), True); plate(root, (0, 2.1 * sl, .46 * sh), False)
    box((.5 * sw, .01, .06), CH, loc=(0, 2.07 * sl, .9 * sh), bev=0, parent=root, name="trunk_handle")
    tube((.6 * sw, 1.95 * sl, .26 * sh), (.6 * sw, 2.14 * sl, .24 * sh), .022, MATS["rim_steel"], root, "exhaust", 8)
    for sx in (-1, 1): tube((sx * .22 * sw, -.82 * sl, .97 * sh), (sx * .02 * sw, -.82 * sl, 1.15 * sh), .004, TR, root, "wiper", 4)
    box((.35 * sw, .55 * sl, .01), TR, loc=(0, -1.2 * sl, .955 * sh), bev=0, parent=root, name="hood_line") if False else None
    # interior hint: dashboard + seats (visible through the glass)
    box((1.2 * sw, .25, .12), TR, loc=(0, -.55 * sl, 1.02 * sh), bev=.02, parent=root, name="dashboard")
    for sx in (-.36, .36): box((.42 * sw, .5, .12), MATS["seat_cloth"], loc=(sx * sw, .08 * sl, .78 * sh), bev=.03, parent=root, name="seat"); box((.42 * sw, .1, .48 * sh), MATS["seat_cloth"], loc=(sx * sw, .35 * sl, 1.0 * sh), bev=.03, parent=root, name="seatback")
    box((1.3 * sw, .5, .12), MATS["seat_cloth"], loc=(0, .95 * sl, .78 * sh), bev=.03, parent=root, name="rear_seat"); box((1.3 * sw, .1, .45 * sh), MATS["seat_cloth"], loc=(0, 1.18 * sl, .98 * sh), bev=.03, parent=root, name="rear_seatback")
    tube((-.3 * sw, -.1 * sl, 1.0 * sh), (-.3 * sw, -.35 * sl, 1.02 * sh), .01, TR, root, "steering_col", 6)
    cyl(.17 * sw, .02, TR, loc=(.36 * sw, -.4 * sl, 1.01 * sh), seg=14, rot=(.9, 0, 0), parent=root, name="steering_wheel")
    alarm = empty("alarm_lamps", size=.1, parent=root)
    for sx in (-1, 1):
        box((.2, .03, .08), MATS["lamp_amber"], loc=(sx * .72 * sw, -2.1 * sl, .66 * sh), bev=.004, parent=alarm, name="alarm_f"); box((.2, .03, .08), MATS["lamp_amber"], loc=(sx * .78 * sw, 2.1 * sl, .7 * sh), bev=.004, parent=alarm, name="alarm_r")
        box((.03, .12, .06), MATS["lamp_amber"], loc=(sx * .83 * sw, -.9 * sl, .8 * sh), bev=.004, parent=alarm, name="alarm_side")
    animate(alarm, "alarm_loop", [(1, dict(scale=(1, 1, 1))), (6, dict(scale=(1, 1, 1))), (7, dict(scale=(.001, .001, .001))), (12, dict(scale=(.001, .001, .001))), (13, dict(scale=(1, 1, 1)))])
    dh = empty("state_dent_hood", size=.1, parent=root); bm_ = bmesh.new(); bmesh.ops.create_uvsphere(bm_, u_segments=12, v_segments=8, radius=.5)
    for v_ in bm_.verts: v_.co.x *= .85 * sw; v_.co.y *= .7 * sl; v_.co.z *= .05 if v_.co.z < 0 else .006
    mesh_obj("dent_hood", bm_, mat("dent_paint", (.05, .06, .08), .5, .3), loc=(0, -1.35 * sl, .955 * sh), parent=dh)
    dr = empty("state_dent_roof", size=.1, parent=root); bm_ = bmesh.new(); bmesh.ops.create_uvsphere(bm_, u_segments=12, v_segments=8, radius=.5)
    for v_ in bm_.verts: v_.co.x *= .85 * sw; v_.co.y *= .9 * sl; v_.co.z *= .05 if v_.co.z < 0 else .006
    mesh_obj("dent_roof", bm_, MATS["dent_paint"], loc=(0, .25 * sl, cab[1][1] + .06), parent=dr)
    empty("ip_hand_hood", (0, -1.7 * sl, .96 * sh), size=.1)
    if roof_rack:
        for sy in (-.05, .9): box((1.1 * sw, .04, .03), TR, loc=(0, sy * sl, cab[1][1] + .06), bev=.004, parent=root, name="rack_bar")
        for sx in (-.54, .54): box((.03, 1.1 * sl, .03), TR, loc=(sx * sw, .43 * sl, cab[1][1] + .06), bev=.004, parent=root, name="rack_rail")
        box((.7, .6, .38), MATS["wood"], loc=(.15, .43 * sl, cab[1][1] + .27), bev=.02, parent=root, name="luggage_box")
        box((.5, .35, .25), MATS["seat_cloth"], loc=(-.2, .6 * sl, cab[1][1] + .21), bev=.05, parent=root, name="luggage_bag")
    if livery == "militia":
        box((W * .501 * 2 * .5 * sw * 2 / 2, 2.1 * sl, .1 * sh), MATS["stripe_blue"], loc=(0, 0, .62 * sh), bev=0, parent=root, name="stripe_unused").hide_viewport = True
        for sx in (-1, 1):
            box((.012, 3.5 * sl, .11 * sh), MATS["stripe_blue"], loc=(sx * .8 * sw, 0, .66 * sh), bev=0, parent=root, name="livery_blue")
            box((.012, 3.5 * sl, .03 * sh), MATS["stripe_yellow"], loc=(sx * .8 * sw, 0, .56 * sh), bev=0, parent=root, name="livery_yellow")
        box((.5 * sw, .01, .06), MATS["stripe_blue"], loc=(0, -2.07 * sl, 1.0 * sh), bev=0, parent=root, name="hood_marking")
    if beacon:
        bar = empty("beacon", (0, .1 * sl, cab[1][1] + .12), size=.1, parent=root)
        box((.34, .12, .05), MATS["trim_black"], loc=(0, 0, 0), bev=.006, parent=bar, name="beacon_base")
        box((.12, .1, .07), MATS["lamp_beacon_blue"], loc=(-.1, 0, .06), bev=.012, parent=bar, name="beacon_blue")
        box((.12, .1, .07), MATS["lamp_beacon_red"], loc=(.1, 0, .06), bev=.012, parent=bar, name="beacon_red")
        animate(bar, "beacon_loop", [(1, dict(rot=(0, 0, 0))), (13, dict(rot=(0, 0, math.pi))), (25, dict(rot=(0, 0, 2 * math.pi)))])
    # wheels
    R_ = .29 * sh; ws = []
    for nm, (x, y) in dict(wheel_fl=(.78 * sw, -1.21 * sl), wheel_fr=(-.78 * sw, -1.21 * sl), wheel_rl=(.78 * sw, 1.21 * sl), wheel_rr=(-.78 * sw, 1.21 * sl)).items():
        ws.append(wheel(nm, R_, .18, x, y, R_ * 1.0))
    for sx in (-1, 1):
        for yy in (-1.21 * sl, 1.21 * sl): box((.02, .72 * R_ * 2, .72 * R_ * 2), TR, loc=(sx * .78 * sw, yy, R_), bev=0, parent=root, name="wheel_arch") if False else None
    return finish_car(name, ws, (L, W, H))

def van(name, body=(.45, .45, .42), ambulance=False, L=5.5, W=2.0, H=2.2):
    fresh(); veh_mats(body)
    B, G, CH, TR = MATS["paint_body"], MATS["glass_car"], MATS["chrome"], MATS["trim_black"]
    root = empty("van_body", size=.2)
    side_prism([(-2.75, .52), (2.75, .52), (2.78, .7), (2.78, 2.0), (-.6, 2.05), (-1.1, 1.5), (-2.0, 1.1), (-2.75, 1.0)], W * .5, .96, B, "body", bev=.04, parent=root)
    for yy in (-1.75, 1.75): box((W * .9, .12, .12), TR, loc=(0, yy, .38), bev=.01, parent=root, name="axle")
    tube((0, -1.75, .42), (0, 1.75, .42), .045, TR, root, "driveshaft", 8); box((.5, .7, .25), TR, loc=(.55, .6, .6), bev=.02, parent=root, name="fuel_tank"); tube((-.4, -2.4, .3), (-.4, 2.7, .3), .035, MATS["rim_steel"], root, "exhaust_pipe", 6)
    for yy in (-1.75, 1.75):
        for sx in (-.7, .7): box((.1, .9, .06), TR, loc=(sx, yy, .5), bev=.005, parent=root, name="leaf_spring")
    side_prism([(-1.95, 1.1), (-1.1, 1.5), (-.62, 2.0), (-.62, 1.3)], W * .485 + .003, .96, G, "cab_glass_unused", bev=0, parent=root).hide_viewport = True
    # windscreen + side windows (glass boxes)
    box((W * .86, .05, .55), G, loc=(0, -1.62, 1.55), bev=.01, rot=(-.78, 0, 0), parent=root, name="windscreen")
    for sx in (-1, 1):
        box((.02, 1.0, .5), G, loc=(sx * (W / 2 * .96 + .005), -.8, 1.6), bev=.004, parent=root, name="cab_window")
        box((.02, .1, .02), CH, loc=(sx * (W / 2 + .01), -.3, 1.2), bev=0, parent=root, name="door_handle")
        tube((sx * .95, -1.55, 1.3), (sx * 1.18, -1.5, 1.45), .01, TR, root, "mirror_arm", 6); box((.06, .22, .3), TR, loc=(sx * 1.18, -1.5, 1.45), bev=.02, parent=root, name="mirror")
        box((.012, 4.5, .02), TR, loc=(sx * (W / 2 + .01), .6, 1.0), bev=0, parent=root, name="panel_seam")
        cyl(.1, .06, MATS["lamp_head"], loc=(sx * .72, -2.78, .8), seg=14, rot=(math.pi / 2, 0, 0), parent=root, name="headlight")
        box((.12, .02, .06), MATS["lamp_amber"], loc=(sx * .92, -2.78, .66), bev=.004, parent=root, name="indicator_f")
        box((.1, .02, .3), MATS["lamp_tail"], loc=(sx * .9, 2.79, 1.1), bev=.006, parent=root, name="taillight")
    box((W * .95, .14, .16), CH, loc=(0, -2.82, .5), bev=.03, parent=root, name="bumper_f"); box((W * .95, .14, .16), CH, loc=(0, 2.84, .5), bev=.03, parent=root, name="bumper_r")
    box((.9, .02, .22), TR, loc=(0, -2.77, .82), bev=.006, parent=root, name="grille")
    plate(root, (0, -2.86, .5), True); plate(root, (0, 2.88, .54), False)
    box((.02, 1.2, 1.0), TR, loc=(W / 2 + .008, 1.3, 1.5), bev=0, parent=root, name="cargo_window_hint") if False else None
    box((W * .95, .02, 1.6), TR, loc=(0, 2.78, 1.25), bev=0, parent=root, name="rear_door_seam") if False else None
    for sx in (-.45, .45): box((.02, .02, 1.6), TR, loc=(sx * 0.01, 2.8, 1.25), bev=0, parent=root, name="rear_door_split") if False else None
    box((.012, .012, 1.6), TR, loc=(0, 2.795, 1.25), bev=0, parent=root, name="rear_door_split")
    if ambulance:
        for sx in (-1, 1):
            box((.012, 4.0, .35), MATS["stripe_red"], loc=(sx * (W / 2 + .004), .5, 1.1), bev=0, parent=root, name="stripe_red")
            box((.012, .5, .5), MATS["body_white"], loc=(sx * (W / 2 + .006), .3, 1.6), bev=0, parent=root, name="cross_plate")
            box((.014, .38, .1), MATS["stripe_red"], loc=(sx * (W / 2 + .008), .3, 1.6), bev=0, parent=root, name="cross_h"); box((.014, .1, .38), MATS["stripe_red"], loc=(sx * (W / 2 + .008), .3, 1.6), bev=0, parent=root, name="cross_v")
        bar = empty("beacon", (0, -.9, 2.1), size=.1, parent=root)
        box((.9, .22, .08), TR, loc=(0, 0, 0), bev=.01, parent=bar, name="beacon_base")
        box((.25, .2, .12), MATS["lamp_beacon_blue"], loc=(-.28, 0, .1), bev=.02, parent=bar, name="beacon_blue"); box((.25, .2, .12), MATS["lamp_beacon_blue"], loc=(.28, 0, .1), bev=.02, parent=bar, name="beacon_blue_r")
        animate(bar, "beacon_loop", [(1, dict(rot=(0, 0, 0))), (13, dict(rot=(0, 0, math.pi))), (25, dict(rot=(0, 0, 2 * math.pi)))])
    R_ = .38; ws = []
    for nm, (x, y) in dict(wheel_fl=(.9, -1.75), wheel_fr=(-.9, -1.75), wheel_rl=(.9, 1.75), wheel_rr=(-.9, 1.75)).items(): ws.append(wheel(nm, R_, .22, x, y, R_))
    return finish_car(name, ws, (L, W, H))

def truck(name, body=(.1, .22, .15), L=6.8, W=2.4, H=2.5):
    fresh(); veh_mats(body)
    B, G, CH, TR = MATS["paint_body"], MATS["glass_car"], MATS["chrome"], MATS["trim_black"]
    root = empty("truck_body", size=.2)
    side_prism([(-3.4, .62), (-1.3, .62), (-1.3, 1.9), (-1.8, 2.3), (-2.6, 2.3), (-3.0, 1.3), (-3.4, 1.2)], W * .46, .94, B, "cab", bev=.04, parent=root)
    box((W * .86, .05, .7), G, loc=(0, -3.05, 1.8), bev=.01, rot=(-.75, 0, 0), parent=root, name="windscreen")
    box((W * .46 * 2 + .06, 6.0, .3), TR, loc=(0, 0.1, .66), bev=.03, parent=root, name="chassis")
    for yy in (-2.2, 2.0, 2.55): box((W * .85, .14, .14), TR, loc=(0, yy, .5), bev=.01, parent=root, name="axle")
    tube((0, -2.2, .56), (0, 2.0, .56), .05, TR, root, "driveshaft", 8); box((.7, .9, .35), TR, loc=(.8, .2, .62), bev=.02, parent=root, name="fuel_tank")
    box((W, 4.2, .12), MATS["wood_deck"], loc=(0, 1.2, .98), bev=.02, parent=root, name="deck")
    for sx in (-1, 1): box((.06, 4.2, .62), MATS["wood_deck"], loc=(sx * (W / 2 - .03), 1.2, 1.35), bev=.01, parent=root, name="side_board")
    box((W, .06, .62), MATS["wood_deck"], loc=(0, 3.27, 1.35), bev=.01, parent=root, name="tail_board"); box((W, .06, .62), MATS["wood_deck"], loc=(0, -.93, 1.35), bev=.01, parent=root, name="front_board")
    for sx in (-1, 1):
        box((.02, 1.1, .6), G, loc=(sx * (W * .46 + .005), -2.25, 1.85), bev=.004, parent=root, name="cab_window")
        cyl(.1, .06, MATS["lamp_head"], loc=(sx * .8, -3.42, .95), seg=14, rot=(math.pi / 2, 0, 0), parent=root, name="headlight")
        box((.12, .02, .06), MATS["lamp_amber"], loc=(sx * .95, -3.42, .8), bev=.004, parent=root, name="indicator_f")
        box((.14, .02, .08), MATS["lamp_tail"], loc=(sx * (W / 2 - .15), 3.3, .9), bev=.004, parent=root, name="taillight")
    box((W * .85, .14, .18), CH, loc=(0, -3.47, .62), bev=.03, parent=root, name="bumper_f"); box((W * .9, .1, .14), CH, loc=(0, 3.32, .6), bev=.02, parent=root, name="bumper_r")
    box((1.0, .02, .3), TR, loc=(0, -3.42, 1.0), bev=.006, parent=root, name="grille")
    plate(root, (0, -3.5, .6), True); plate(root, (0, 3.35, .7), False)
    ws = []
    for nm, (x, y) in dict(wheel_fl=(1.0, -2.2), wheel_fr=(-1.0, -2.2), wheel_rl=(1.0, 2.0), wheel_rr=(-1.0, 2.0), wheel_rl2=(1.0, 2.55), wheel_rr2=(-1.0, 2.55)).items(): ws.append(wheel(nm, .5, .28, x, y, .5))
    tube((.9, -3.1, 2.55), (.9, -3.1, 2.7), .02, TR, root, "mirror_arm", 6)
    return finish_car(name, ws, (L, W, H))

def bus(name, trolley=False, body=(.45, .28, .08), L=10.8, W=2.5, H=3.05):
    fresh(); veh_mats(body, (.55, .55, .5))
    B, B2, G, CH, TR = MATS["paint_body"], MATS["paint_body2"], MATS["glass_car"], MATS["chrome"], MATS["trim_black"]
    root = empty("bus_body", size=.3)
    side_prism([(-5.4, .45), (5.4, .45), (5.45, .7), (5.4, 3.0), (-5.2, 3.05), (-5.45, 2.85), (-5.45, .7)], W * .5, .97, B, "body", bev=.05, parent=root)
    box((W + .01, L - .3, .1), B2, loc=(0, 0, 1.0), bev=0, parent=root, name="belt_band") if False else None
    for sx in (-1, 1):                                                     # side window band (7 windows) and doors on the right side (-X)
        for k in range(7):
            y = -4.3 + k * 1.35
            if sx == -1 and k in (1, 4): continue
            box((.02, 1.2, .95), G, loc=(sx * (W / 2 * .97 + .01), y, 2.0), bev=.004, parent=root, name="window")
        box((.014, L - .4, .05), B2, loc=(sx * (W / 2 + .004), 0, 1.35), bev=0, parent=root, name="belt_stripe"); box((.014, L - .4, .05), B2, loc=(sx * (W / 2 + .004), 0, 2.62), bev=0, parent=root, name="roof_stripe")
    for k in (1, 4):                                                       # folding doors on the right
        y = -4.3 + k * 1.35 + .67
        for h in (-.31, .31): box((.02, .6, 1.7), G, loc=(-(W / 2 * .97 + .012), y + h, 1.55), bev=.004, parent=root, name="door_leaf")
        box((.03, 1.3, .05), CH, loc=(-(W / 2 + .02), y, .75), bev=.004, parent=root, name="door_step")
    box((W * .9, .06, 1.35), G, loc=(0, -5.43, 2.0), bev=.01, parent=root, name="windscreen")
    box((W * .8, .05, .75), G, loc=(0, 5.42, 2.2), bev=.01, parent=root, name="rear_window")
    box((.9, .03, .28), MATS["lamp_white"], loc=(0, -5.44, 2.82), bev=.004, parent=root, name="route_board"); box((.8, .01, .2), TR, loc=(0, -5.46, 2.82), bev=0, parent=root, name="route_number")
    for sx in (-1, 1):
        cyl(.11, .06, MATS["lamp_head"], loc=(sx * .8, -5.46, .95), seg=14, rot=(math.pi / 2, 0, 0), parent=root, name="headlight")
        box((.12, .02, .07), MATS["lamp_amber"], loc=(sx * 1.0, -5.46, .75), bev=.004, parent=root, name="indicator_f")
        box((.12, .02, .3), MATS["lamp_tail"], loc=(sx * 1.0, 5.46, 1.2), bev=.004, parent=root, name="taillight")
        tube((sx * 1.05, -5.2, 2.2), (sx * 1.3, -5.25, 2.5), .012, TR, root, "mirror_arm", 6); box((.08, .24, .45), TR, loc=(sx * 1.3, -5.25, 2.5), bev=.02, parent=root, name="mirror")
    box((W * .96, .16, .2), CH, loc=(0, -5.5, .6), bev=.03, parent=root, name="bumper_f"); box((W * .96, .16, .2), CH, loc=(0, 5.5, .6), bev=.03, parent=root, name="bumper_r")
    plate(root, (0, -5.54, .62), True); plate(root, (0, 5.54, .62), False)
    box((1.0, .03, .35), TR, loc=(0, 5.43, 1.0), bev=0, parent=root, name="engine_grille")
    if trolley:
        for sx, nm in ((-.4, "pole_a"), (.4, "pole_b")):
            piv = empty(nm, (sx, 2.4, 3.1), size=.1, parent=root)
            beam((0, 0, 0), (0, -3.2, 3.0), .035, .035, TR, piv, "pole_rod", .004)
            box((.1, .22, .06), TR, loc=(0, -3.3, 3.05), bev=.01, parent=piv, name="shoe")
            animate(piv, "pole_sway", [(1, dict(rot=(0, 0, 0))), (25, dict(rot=(0, 0, .03))), (49, dict(rot=(0, 0, -.03))), (73, dict(rot=(0, 0, 0)))])
        box((1.2, 1.4, .06), TR, loc=(0, 2.4, 3.08), bev=.01, parent=root, name="pole_base")
        box((.5, .01, .3), MATS["lamp_white"], loc=(-1.0, -5.44, 2.82), bev=0, parent=root, name="route_board_2") if False else None
    ws = []
    for nm, (x, y) in dict(wheel_fl=(1.05, -3.7), wheel_fr=(-1.05, -3.7), wheel_rl=(1.05, 2.6), wheel_rr=(-1.05, 2.6), wheel_rl2=(1.05, 3.45) if not trolley else (1.05, 2.6), wheel_rr2=(-1.05, 3.45) if not trolley else (-1.05, 2.6)).items():
        if trolley and nm.endswith("2"): continue
        ws.append(wheel(nm, .5, .3, x, y, .5))
    return finish_car(name, ws, (L, W, H))

def tow_truck(name, body=(.45, .12, .08)):
    fresh(); veh_mats(body)
    B, G, CH, TR = MATS["paint_body"], MATS["glass_car"], MATS["chrome"], MATS["trim_black"]
    root = empty("tow_body", size=.2)
    side_prism([(-3.2, .5), (-1.1, .5), (-1.1, 1.9), (-1.6, 2.3), (-2.4, 2.3), (-2.8, 1.3), (-3.2, 1.2)], 1.05, .94, B, "cab", bev=.04, parent=root)
    box((1.75, .05, .65), G, loc=(0, -2.85, 1.8), bev=.01, rot=(-.75, 0, 0), parent=root, name="windscreen")
    box((2.1, 5.2, .3), TR, loc=(0, .3, .6), bev=.03, parent=root, name="chassis")
    box((2.3, 3.6, .14), MATS["steel_dark"], loc=(0, 1.5, 1.0), bev=.02, parent=root, name="flatbed")
    for sx in (-1, 1): box((.08, 3.6, .2), MATS["steel_dark"], loc=(sx * 1.1, 1.5, 1.14), bev=.01, parent=root, name="bed_rail")
    boom = empty("boom", (0, -1.0, 1.1), size=.1, parent=root)
    beam((0, 0, 0), (0, 1.0, 1.6), .12, .12, MATS["paint_yellow"], boom, "boom_arm", .01)
    box((.2, .2, .2), CH, loc=(0, 1.0, 1.65), bev=.02, parent=boom, name="hook")
    animate(boom, "boom_lift", [(1, dict(rot=(0, 0, 0))), (24, dict(rot=(-.5, 0, 0)))])
    for sx in (-1, 1):
        cyl(.1, .06, MATS["lamp_head"], loc=(sx * .8, -3.22, .95), seg=14, rot=(math.pi / 2, 0, 0), parent=root, name="headlight")
        box((.14, .02, .08), MATS["lamp_tail"], loc=(sx * .9, 3.3, .9), bev=.004, parent=root, name="taillight")
    box((2.0, .14, .18), CH, loc=(0, -3.27, .62), bev=.03, parent=root, name="bumper_f"); plate(root, (0, -3.3, .6), True); plate(root, (0, 3.35, .7), False)
    bar = empty("beacon", (0, -2.0, 2.4), size=.1, parent=root); box((.7, .2, .08), TR, loc=(0, 0, 0), bev=.01, parent=bar, name="beacon_base"); box((.25, .18, .1), MATS["lamp_amber"], loc=(-.2, 0, .09), bev=.02, parent=bar, name="beacon_a"); box((.25, .18, .1), MATS["lamp_amber"], loc=(.2, 0, .09), bev=.02, parent=bar, name="beacon_b")
    ws = []
    for nm, (x, y) in dict(wheel_fl=(1.0, -2.1), wheel_fr=(-1.0, -2.1), wheel_rl=(1.0, 2.0), wheel_rr=(-1.0, 2.0)).items(): ws.append(wheel(nm, .5, .28, x, y, .5))
    return finish_car(name, ws, (6.6, 2.3, 2.5))

BUILD = {
 "car_sedan": lambda: car("car_sedan", "sedan", (.1, .12, .15)),
 "car_sedan_green": lambda: car("car_sedan_green", "sedan", (.07, .14, .09)),
 "car_wagon": lambda: car("car_wagon", "wagon", (.3, .27, .2), L=4.15),
 "car_moskvich": lambda: car("car_moskvich", "moskvich", (.35, .14, .08), L=4.1, W=1.58, H=1.5),
 "car_sedan_roofrack": lambda: car("car_sedan_roofrack", "sedan", (.4, .38, .3), roof_rack=True),
 "car_militia": lambda: car("car_militia", "sedan", (.5, .5, .48), livery="militia", beacon=True),
 "van_gazelle": lambda: van("van_gazelle", (.4, .4, .38)),
 "ambulance": lambda: van("ambulance", (.52, .52, .5), ambulance=True),
 "truck_zil": lambda: truck("truck_zil"),
 "bus_city": lambda: bus("bus_city", False, (.45, .25, .07)),
 "trolleybus": lambda: bus("trolleybus", True, (.1, .3, .4)),
 "tow_truck": lambda: tow_truck("tow_truck"),
}
which = os.environ.get("VEH", "all")
for k, f in BUILD.items():
    if which == "all" or which == k: f()
