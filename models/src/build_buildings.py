"""Buildings (stage 4): perforated facades with recessed windows (separate material `building_window` for night glow), balconies, entrances, roofs.
Run: BLD=<name|all> D:\\Cosmoteer\\blender.exe -b -P build_buildings.py -> models/city/buildings/<name>.glb
Conventions: metres, floor height 2.8, front facade towards -Y in Blender (+Z in glTF), origin at ground centre of the footprint. Collision `<name>-col`. ip_use at the main entrance.
Modules (src: `module_*`): wall_row (one bay, 3 floors), wall_corner, entrance_bay, end_wall, roof_cap: built from the same functions, bay width 3.0 m."""
import os
exec(open("D:/Faceless/models/src/lib_props.py", encoding="utf-8").read())
OUT = "D:/Faceless/models/city/buildings"; os.makedirs(OUT, exist_ok=True)
FH = 2.8

def bmats():
    fresh(); palette()
    mat("building_window", (.03, .045, .06), .1, 0.0); mat("window_frame", (.3, .3, .28), .6); mat("panel_wall", (.34, .33, .3), .95); mat("panel_wall_b", (.3, .31, .32), .95)
    mat("brick_wall", (.24, .11, .08), .95); mat("stalin_wall", (.4, .34, .24), .95); mat("stucco", (.42, .4, .34), .95); mat("glass_curtain", (.07, .11, .13), .1, .4)
    mat("roof_tar", (.05, .05, .055), .95); mat("balcony_slab", (.28, .28, .26), .95); mat("balcony_rail", (.12, .13, .14), .7); mat("loggia_glass", (.2, .28, .3), .15)
    mat("door_steel", (.1, .12, .11), .6); mat("sign_red_glow", (.4, .03, .03), .5, 0.0, emit=(1, .1, .05), emit_strength=2.0); mat("column_white", (.5, .5, .46), .9)
    mat("metal_roof", (.2, .22, .23), .6, .6); mat("insulator", (.4, .45, .4), .4); mat("granite", (.12, .12, .13), .35); mat("awning_a", (.4, .08, .06), .8); mat("awning_b", (.5, .45, .35), .8); mat("cafe_sign", (.55, .4, .1), .5, 0.0, emit=(1, .6, .2), emit_strength=1.5)

def perforated(name, nx, ny, cw, ch, ww, wh, sill, wall_m, glass_m, frame_m, depth=.22, skip=None, x0=0.0, z0=0.0, parent=None, window_fn=None, frame_w=.05):
    """Facade plane in XZ facing -Y; each cell has a recessed window with reveal and frame. window_fn(i,j)->(ww,wh,sill) overrides sizes."""
    me = bpy.data.meshes.new(name); bm = bmesh.new()
    def quad(pts, mi, want):
        vs = [bm.verts.new(p) for p in pts]; f = bm.faces.new(vs); f.material_index = mi; f.normal_update()
        if f.normal.dot(want) < 0: f.normal_flip()
        return f
    for j in range(ny):
        for i in range(nx):
            X0, X1, Z0, Z1 = x0 + i * cw, x0 + (i + 1) * cw, z0 + j * ch, z0 + (j + 1) * ch
            if skip and skip(i, j): quad([(X0, 0, Z0), (X1, 0, Z0), (X1, 0, Z1), (X0, 0, Z1)], 0, Vector((0, -1, 0))); continue
            w_, h_, s_ = window_fn(i, j) if window_fn else (ww, wh, sill)
            wx0 = X0 + (cw - w_) / 2; wx1 = wx0 + w_; wz0 = Z0 + s_; wz1 = wz0 + h_
            quad([(X0, 0, Z0), (X1, 0, Z0), (X1, 0, wz0), (X0, 0, wz0)], 0, Vector((0, -1, 0)))
            quad([(X0, 0, wz1), (X1, 0, wz1), (X1, 0, Z1), (X0, 0, Z1)], 0, Vector((0, -1, 0)))
            quad([(X0, 0, wz0), (wx0, 0, wz0), (wx0, 0, wz1), (X0, 0, wz1)], 0, Vector((0, -1, 0)))
            quad([(wx1, 0, wz0), (X1, 0, wz0), (X1, 0, wz1), (wx1, 0, wz1)], 0, Vector((0, -1, 0)))
            c = Vector(((wx0 + wx1) / 2, depth, (wz0 + wz1) / 2))
            for (a, b) in (((wx0, wz0), (wx1, wz0)), ((wx1, wz0), (wx1, wz1)), ((wx1, wz1), (wx0, wz1)), ((wx0, wz1), (wx0, wz0))):
                mid = Vector(((a[0] + b[0]) / 2, depth / 2, (a[1] + b[1]) / 2)); quad([(a[0], 0, a[1]), (b[0], 0, b[1]), (b[0], depth, b[1]), (a[0], depth, a[1])], 0, c - mid)
            fw = frame_w
            quad([(wx0, depth, wz0), (wx1, depth, wz0), (wx1 - fw, depth, wz0 + fw), (wx0 + fw, depth, wz0 + fw)], 2, Vector((0, -1, 0)))
            quad([(wx1, depth, wz0), (wx1, depth, wz1), (wx1 - fw, depth, wz1 - fw), (wx1 - fw, depth, wz0 + fw)], 2, Vector((0, -1, 0)))
            quad([(wx1, depth, wz1), (wx0, depth, wz1), (wx0 + fw, depth, wz1 - fw), (wx1 - fw, depth, wz1 - fw)], 2, Vector((0, -1, 0)))
            quad([(wx0, depth, wz1), (wx0, depth, wz0), (wx0 + fw, depth, wz0 + fw), (wx0 + fw, depth, wz1 - fw)], 2, Vector((0, -1, 0)))
            quad([(wx0 + fw, depth, wz0 + fw), (wx1 - fw, depth, wz0 + fw), (wx1 - fw, depth, wz1 - fw), (wx0 + fw, depth, wz1 - fw)], 1, Vector((0, -1, 0)))
    bm.to_mesh(me); bm.free()
    for m in (wall_m, glass_m, frame_m): me.materials.append(m)
    o = bpy.data.objects.new(name, me); collection().objects.link(o); o.parent = parent
    for p in me.polygons: p.use_smooth = False
    return o

def place_facade(o, side, W, D):
    """rotate/move a facade built facing -Y at x in [0,w] to the building side: 'front' (-Y), 'back' (+Y), 'left' (-X), 'right' (+X)"""
    if side == "front": o.location = (-W / 2, -D / 2, 0)
    elif side == "back": o.rotation_euler = (0, 0, math.pi); o.location = (W / 2, D / 2, 0)
    elif side == "left": o.rotation_euler = (0, 0, -math.pi / 2); o.location = (-W / 2, D / 2, 0)
    elif side == "right": o.rotation_euler = (0, 0, math.pi / 2); o.location = (W / 2, -D / 2, 0)

def balcony(parent, x, y, z, w=1.4, d=.85, glazed=False, wall_m=None):
    box((w, d, .14), MATS["balcony_slab"], loc=(x, y - d / 2, z), bev=0, parent=parent, name="balcony_slab")
    if glazed:
        box((w, .04, 1.05), MATS["loggia_glass"], loc=(x, y - d + .02, z + .6), bev=0, parent=parent, name="loggia_front")
        for sx in (-w / 2, w / 2): box((.04, d, 1.05), MATS["loggia_glass"], loc=(x + sx, y - d / 2, z + .6), bev=0, parent=parent, name="loggia_side")
        box((w + .04, .06, .08), MATS["balcony_rail"], loc=(x, y - d + .02, z + 1.14), bev=0, parent=parent, name="loggia_top")
    else:
        box((w, .05, .95), MATS["balcony_rail"], loc=(x, y - d + .025, z + .55), bev=0, parent=parent, name="balcony_panel")
        for sx in (-w / 2, w / 2): box((.05, d, .95), MATS["balcony_rail"], loc=(x + sx, y - d / 2, z + .55), bev=0, parent=parent, name="balcony_side")

def roof(parent, W, D, top, tech=True, parapet=.5, mat_=None):
    box((W + .3, D + .3, .25), MATS["roof_tar"], loc=(0, 0, top + .1), bev=0, parent=parent, name="roof_slab")
    for sx in (-1, 1): box((.25, D + .3, parapet), mat_ or MATS["panel_wall"], loc=(sx * (W / 2 + .05), 0, top + .22 + parapet / 2), bev=0, parent=parent, name="parapet_x")
    for sy in (-1, 1): box((W + .3, .25, parapet), mat_ or MATS["panel_wall"], loc=(0, sy * (D / 2 + .05), top + .22 + parapet / 2), bev=0, parent=parent, name="parapet_y")
    if tech:
        box((W * .35, D * .5, 2.0), mat_ or MATS["panel_wall"], loc=(W * .15, 0, top + 1.3), bev=0, parent=parent, name="tech_floor")
        box((1.6, 1.6, 1.3), MATS["brick_wall"], loc=(-W * .3, D * .15, top + .9), bev=0, parent=parent, name="vent_stack")
        for k in range(3):
            tube((-W * .4 + k * .6, -D * .3, top + .2), (-W * .4 + k * .6, -D * .3, top + 4.5 + k * .6), .02, MATS["steel_dark"], parent, "antenna", 5)

def entrance(parent, x, y_front, w=2.2):
    box((w, .9, .12), MATS["concrete_dark"], loc=(x, y_front - .45, 2.45), bev=0, parent=parent, name="canopy")
    for sx in (-w / 2 + .1, w / 2 - .1): box((.1, .1, 2.4), MATS["concrete_dark"], loc=(x + sx, y_front - .8, 1.2), bev=0, parent=parent, name="canopy_post")
    box((1.1, .12, 2.0), MATS["door_steel"], loc=(x, y_front + .06, 1.0), bev=.01, parent=parent, name="door")
    box((.12, .1, .3), MATS["steel"], loc=(x + .38, y_front - .02, 1.0), bev=0, parent=parent, name="door_handle")
    for k in range(3): box((w + .4, .3, .17), MATS["concrete"], loc=(x, y_front - 1.0 - k * .3, .085 + .17 * (2 - k) * 0 + k * 0), bev=0, parent=parent, name="step") if False else None
    for k in range(3): box((w + .2 + k * .0, .35, .16), MATS["concrete"], loc=(x, y_front - .45 - k * .35, .08 + (2 - k) * .0 + (2 - k) * .0), bev=0, parent=parent, name="step") if False else None
    for k in range(3): box((w + .1, .35, .17 * (3 - k)), MATS["concrete"], loc=(x, y_front - .22 - k * .35, .085 * (3 - k)), bev=0, parent=parent, name="step")

def panel_building(name, floors, bays, bay_w=3.0, depth=11.5, wall="panel_wall", balcony_mode="none", entrances=(), tech=True, ground_h=None, pitched=False, win=(1.5, 1.3, .9)):
    bmats(); root = empty("building", size=.5)
    W = bays * bay_w; H = floors * FH; wall_m = MATS[wall]
    box((W - .5, depth - .5, H), wall_m, loc=(0, 0, H / 2), bev=0, parent=root, name="mass")
    ww, wh, sill = win
    def skip_ground(i, j): return False
    for side, nx_, wid in (("front", bays, bay_w), ("back", bays, bay_w)):
        o = perforated("facade_" + side, nx_, floors, wid, FH, ww, wh, sill, wall_m, MATS["building_window"], MATS["window_frame"], parent=root, skip=lambda i, j, side=side: (j == 0 and (i in entrances) and side == "front"))
        place_facade(o, side, W, depth)
    nd = max(1, int(depth // 3.0))
    for side in ("left", "right"):                                   # gable ends: mostly blank with a few small windows
        o = perforated("facade_" + side, 1, floors, depth, FH, 1.0, 1.2, .9, wall_m, MATS["building_window"], MATS["window_frame"], parent=root, skip=lambda i, j: (j % 3 != 1))
        place_facade(o, side, W, depth)
    # balconies
    if balcony_mode != "none":
        for j in range(1, floors):
            for i in range(bays):
                if i % 2 == 1: balcony(root, -W / 2 + (i + .5) * bay_w, -depth / 2 + .05, j * FH + .0, glazed=(balcony_mode == "loggia"))
    for e in entrances: entrance(root, -W / 2 + (e + .5) * bay_w, -depth / 2 + .1)
    roof(root, W, depth, H, tech)
    # ground floor band
    box((W + .1, .1, .5), MATS["concrete_dark"], loc=(0, -depth / 2 - .02, .25), bev=0, parent=root, name="plinth")
    box((W, depth, H + .5), None, loc=(0, 0, (H + .5) / 2), bev=0, name=name + "-col")
    empty("ip_use", (-W / 2 + (entrances[0] + .5) * bay_w if entrances else 0, -depth / 2 - 1.6, 0), size=.3)
    return finish(name, W, depth, H)

def finish(name, W, D, H):
    for o in bpy.data.objects:
        if o.type == 'MESH' and not (name in ('chp_plant', 'factory') and o.name in ('chimney', 'stack')):
            for p in o.data.polygons: p.use_smooth = False
    tris, dims = export(name, out_dir=OUT)
    return tris

def stalin():
    bmats(); root = empty("building", size=.5); name = "stalin_house"
    W, D, floors = 48.0, 14.0, 7; H = floors * FH; wm = MATS["stalin_wall"]
    box((W - .5, D - .5, H), wm, loc=(0, 0, H / 2), bev=0, parent=root, name="mass")
    for side in ("front", "back"):
        o = perforated("facade_" + side, 16, floors, 3.0, FH, 1.2, 1.7, .6, wm, MATS["building_window"], MATS["window_frame"], parent=root, skip=lambda i, j, side=side: (side == "front" and j == 0 and i in (7, 8)))
        place_facade(o, side, W, D)
    for side in ("left", "right"):
        o = perforated("facade_" + side, 4, floors, 3.5, FH, 1.2, 1.7, .6, wm, MATS["building_window"], MATS["window_frame"], parent=root)
        place_facade(o, side, W, D)
    # cornice, rustication, columns at the centre, tower
    box((W + .6, D + .6, .5), MATS["column_white"], loc=(0, 0, H + .25), bev=0, parent=root, name="cornice"); box((W + .3, D + .3, .8), MATS["column_white"], loc=(0, 0, H - .4), bev=0, parent=root, name="cornice_low") if False else None
    for k in range(6): cyl(.4, 5.6, MATS["column_white"], loc=(-3.75 + k * 1.5, -D / 2 - .7, 2.8), seg=14, parent=root, name="column")
    box((9.5, 1.8, .5), MATS["column_white"], loc=(0, -D / 2 - .7, 5.8), bev=0, parent=root, name="architrave")
    box((9.5, 1.8, .5), MATS["column_white"], loc=(0, -D / 2 - .7, .25), bev=0, parent=root, name="stylobate")
    box((1.6, .15, 2.6), MATS["door_steel"], loc=(-.9, -D / 2 + .08, 1.3), bev=0, parent=root, name="door_l"); box((1.6, .15, 2.6), MATS["door_steel"], loc=(.9, -D / 2 + .08, 1.3), bev=0, parent=root, name="door_r")
    t = [(10.0, 9.0, 6.0), (7.0, 6.6, 6.0), (4.6, 4.2, 4.0)]; z = H + .5
    for w_, d_, h_ in t:
        box((w_, d_, h_), wm, loc=(0, 0, z + h_ / 2), bev=0, parent=root, name="tower_tier"); box((w_ + .5, d_ + .5, .3), MATS["column_white"], loc=(0, 0, z + h_), bev=0, parent=root, name="tower_cornice"); z += h_
    for k in range(3):
        o = perforated("tower_win", 4, 2, 2.2 - k * .3, 2.2, .9, 1.3, .5, wm, MATS["building_window"], MATS["window_frame"], parent=root, skip=lambda i, j: False)
    cyl_ = lathe([(0, 0), (1.3, 0), (.9, 3.0), (.3, 8.0), (.08, 13.0), (0, 13.5)], MATS["metal_roof"], loc=(0, 0, z + .1), seg=8, parent=root, name="spire")
    box((.7, .7, .7), MATS["gold_glow"], loc=(0, 0, z + 13.9), bev=0, parent=root, name="star")
    box((W, D, H + 28), None, loc=(0, 0, (H + 28) / 2), bev=0, name=name + "-col")
    empty("ip_use", (0, -D / 2 - 3.0, 0), size=.3)
    return finish(name, W, D, H + 28)

def office_glass():
    bmats(); root = empty("building", size=.5); name = "office_glass"
    W, D, floors = 30.0, 20.0, 10; H = floors * 3.6
    box((W - .5, D - .5, H), MATS["glass_curtain"], loc=(0, 0, H / 2), bev=0, parent=root, name="mass")
    for side, nx, wid in (("front", 12, 2.5), ("back", 12, 2.5)):
        o = perforated("curtain_" + side, nx, floors, wid, 3.6, 2.3, 3.0, .35, MATS["window_frame"], MATS["building_window"], MATS["metal_roof"], depth=.12, parent=root, frame_w=.08)
        place_facade(o, side, W, D)
    for side in ("left", "right"):
        o = perforated("curtain_" + side, 8, floors, 2.5, 3.6, 2.3, 3.0, .35, MATS["window_frame"], MATS["building_window"], MATS["metal_roof"], depth=.12, parent=root, frame_w=.08); place_facade(o, side, W, D)
    box((W + .3, D + .3, .4), MATS["concrete"], loc=(0, 0, H + .2), bev=0, parent=root, name="roof_edge"); box((8, 6, 3), MATS["concrete"], loc=(3, 2, H + 1.9), bev=0, parent=root, name="roof_unit")
    box((8, 3, .25), MATS["concrete_dark"], loc=(0, -D / 2 - 1.5, 3.6), bev=0, parent=root, name="entrance_canopy"); box((3.5, .2, 3.2), MATS["building_window"], loc=(0, -D / 2 + .05, 1.7), bev=0, parent=root, name="entrance_glass")
    for sx in (-3.4, 3.4): cyl(.15, 3.5, MATS["steel_dark"], loc=(sx, -D / 2 - 2.6, 1.75), seg=10, parent=root, name="canopy_column")
    box((W, D, H + 4), None, loc=(0, 0, (H + 4) / 2), bev=0, name=name + "-col"); empty("ip_use", (0, -D / 2 - 3, 0), size=.3)
    return finish(name, W, D, H)

def pavilion(name, W, D, H, kind):
    bmats(); root = empty("building", size=.5)
    wm = MATS["panel_wall"] if kind != "granite" else MATS["granite"]
    box((W - .5, D - .5, H), wm, loc=(0, 0, H / 2), bev=0, parent=root, name="mass")
    o = perforated("shopfront", max(1, int(W // 3)), 1, W / max(1, int(W // 3)), H, W / max(1, int(W // 3)) - .5, H - 1.2, .8, wm, MATS["building_window"], MATS["window_frame"], parent=root, depth=.15); place_facade(o, "front", W, D)
    box((W + .6, D + .6, .3), MATS["roof_tar"], loc=(0, 0, H + .15), bev=0, parent=root, name="roof")
    box((W * .5, .1, 1.0), MATS["sign_red_glow"] if kind == "metro" else MATS["cafe_sign"], loc=(0, -D / 2 - .12, H + .85), bev=0, parent=root, name="sign_board") if kind != "metro" else None
    box((1.4, .12, 2.1), MATS["door_steel"], loc=(0, -D / 2 + .04, 1.05), bev=.01, parent=root, name="door")
    if kind == "metro":
        # big M on a pylon + canopy
        pts = [(-.9, 0), (-.9, 1.8), (-.45, 1.8), (0, .9), (.45, 1.8), (.9, 1.8), (.9, 0), (.55, 0), (.55, 1.0), (0, .2), (-.55, 1.0), (-.55, 0)]
        m_ = poly_prism(pts, .25, MATS["sign_red_glow"], loc=(0, -D / 2 - .2, H + .35), parent=root, name="letter_M"); m_.rotation_euler = (math.pi / 2, 0, 0); m_.location = (0, -D / 2 - .15 + .12, H + 2.3 - .9)
        m_.scale = (1.0, 1.0, 1.0)
        box((W * .8, 2.5, .25), MATS["concrete_dark"], loc=(0, -D / 2 - 1.25, 3.6), bev=0, parent=root, name="canopy")
        for sx in (-W * .35, W * .35): cyl(.15, 3.5, MATS["steel_dark"], loc=(sx, -D / 2 - 2.3, 1.75), seg=10, parent=root, name="canopy_post")
    if kind == "cafe":
        for k in range(3): box((.9, .02, .8), MATS["cafe_sign"], loc=(-W * .25 + k * W * .25, -D / 2 - .1, 2.6), bev=0, parent=root, name="menu_board")
        box((W * .9, .9, .08), MATS["awning_a"], loc=(0, -D / 2 - .45, 3.0), bev=0, parent=root, name="awning")
    if kind == "granite":
        for k in range(4): cyl(.25, H, MATS["column_white"], loc=(-W * .3 + k * W * .2, -D / 2 - .5, H / 2), seg=12, parent=root, name="column")
        box((W * .8, 1.2, .35), MATS["column_white"], loc=(0, -D / 2 - .5, H + .1), bev=0, parent=root, name="pediment")
    box((W, D, H + 1), None, loc=(0, 0, (H + 1) / 2), bev=0, name=name + "-col"); empty("ip_use", (0, -D / 2 - 1.8, 0), size=.3)
    return finish(name, W, D, H)

def school():
    bmats(); root = empty("building", size=.5); name = "school"
    W, D, floors = 54.0, 15.0, 3; H = floors * 3.8; wm = MATS["stucco"]
    box((W - .5, D - .5, H), wm, loc=(0, 0, H / 2), bev=0, parent=root, name="mass")
    for side in ("front", "back"):
        o = perforated("facade_" + side, 18, floors, 3.0, 3.8, 2.0, 2.0, .9, wm, MATS["building_window"], MATS["window_frame"], parent=root, skip=lambda i, j, side=side: (side == "front" and j == 0 and i in (8, 9))); place_facade(o, side, W, D)
    for side in ("left", "right"):
        o = perforated("facade_" + side, 5, floors, 3.0, 3.8, 1.6, 2.0, .9, wm, MATS["building_window"], MATS["window_frame"], parent=root); place_facade(o, side, W, D)
    box((W + .4, D + .4, .4), MATS["roof_tar"], loc=(0, 0, H + .2), bev=0, parent=root, name="roof")
    for k in range(4): cyl(.28, 3.6, MATS["column_white"], loc=(-2.4 + k * 1.6, -D / 2 - 1.0, 1.8), seg=12, parent=root, name="column")
    box((7.6, 2.6, .35), MATS["column_white"], loc=(0, -D / 2 - .8, 3.75), bev=0, parent=root, name="portico_roof"); box((2.2, .12, 2.6), MATS["door_steel"], loc=(0, -D / 2 + .05, 1.3), bev=0, parent=root, name="door")
    box((4.0, .3, .6), MATS["cafe_sign"], loc=(0, -D / 2 - 1.2, 4.3), bev=0, parent=root, name="school_sign")
    box((W, D, H + 1), None, loc=(0, 0, (H + 1) / 2), bev=0, name=name + "-col"); empty("ip_use", (0, -D / 2 - 3, 0), size=.3)
    return finish(name, W, D, H)

def market():
    bmats(); root = empty("building", size=.5); name = "market"
    box((22, 14, .2), MATS["concrete_dark"], loc=(0, 0, .1), bev=0, parent=root, name="floor")
    cols = [MATS["awning_a"], MATS["awning_b"]]
    for row in (-1, 1):
        for k in range(5):
            x = -8.4 + k * 4.2; y = row * 4.2
            box((3.4, 2.2, .1), MATS["wood"], loc=(x, y, .95), bev=0, parent=root, name="counter_top"); box((3.2, 2.0, .85), MATS["wood"], loc=(x, y, .5), bev=0, parent=root, name="counter")
            for sx in (-1.6, 1.6):
                for sy in (-1.0, 1.0): cyl(.04, 2.4, MATS["steel_dark"], loc=(x + sx, y + sy, 1.4), seg=6, parent=root, name="awning_post")
            t = box((3.8, 2.8, .06), cols[(k + (row > 0)) % 2], loc=(x, y, 2.55), bev=0, parent=root, name="awning"); t.rotation_euler = (row * .12, 0, 0)
            for q in range(5): box((.5, .4, .3), mat(f"goods_{q}", (.2 + q * .08, .15 + q * .05, .08), .9), loc=(x - 1.2 + q * .6, y, 1.15), bev=.02, parent=root, name="goods")
    box((22, 14, 3.0), None, loc=(0, 0, 1.5), bev=0, name=name + "-col"); empty("ip_use", (0, -8, 0), size=.3)
    return finish(name, 22, 14, 3.0)

def industrial(kind):
    bmats(); root = empty("building", size=.5); name = "factory" if kind == "factory" else "chp_plant" if kind == "chp" else "warehouse"
    if kind == "factory":
        W, D, H = 36.0, 20.0, 9.0
    elif kind == "chp":
        W, D, H = 44.0, 24.0, 16.0
    else:
        W, D, H = 26.0, 14.0, 6.5
    wm = MATS["panel_wall"] if kind != "factory" else MATS["brick_wall"]
    box((W - .5, D - .5, H), wm, loc=(0, 0, H / 2), bev=0, parent=root, name="mass")
    nx = int(W // 4)
    o = perforated("facade_front", nx, 1, W / nx, H - 2.0, W / nx - 1.6, 2.0, H - 5.0 if kind != "warehouse" else 3.5, wm, MATS["building_window"], MATS["window_frame"], parent=root, depth=.2, skip=lambda i, j: False); place_facade(o, "front", W, D)
    o = perforated("facade_back", nx, 1, W / nx, H - 2.0, W / nx - 1.6, 2.0, H - 5.0 if kind != "warehouse" else 3.5, wm, MATS["building_window"], MATS["window_frame"], parent=root, depth=.2); place_facade(o, "back", W, D)
    box((6.0, .3, 5.0), MATS["door_steel"], loc=(0, -D / 2 + .05, 2.5), bev=0, parent=root, name="gate")
    for k in range(3): box((6.0, .32, .1), MATS["steel_dark"], loc=(0, -D / 2 + .03, 1.2 + k * 1.4), bev=0, parent=root, name="gate_rib")
    if kind == "factory":
        for k in range(4):                                         # sawtooth roof
            p = poly_prism([(-W / 2 + k * 9.0, 0), (-W / 2 + k * 9.0 + 9.0, 0), (-W / 2 + k * 9.0 + 9.0, 3.2)] if False else [(0, 0), (9.0, 0), (9.0, 3.2)], D - .4, MATS["metal_roof"], loc=(0, 0, 0), parent=root, name="saw")
            p.rotation_euler = (math.pi / 2, 0, 0); p.location = (-W / 2 + k * 9.0, D / 2 - .2, H)
        lathe([(0, 0), (1.9, 0), (1.5, 20), (1.2, 38), (0, 38.5)], MATS["brick_wall"], loc=(-W / 2 + 4, -3, 0), seg=14, parent=root, name="chimney") if False else lathe([(0, 0), (1.9, 0), (1.5, 20), (1.2, 38), (0, 38.5)], MATS["brick_wall"], loc=(-W / 2 + 4, 4, H), seg=14, parent=root, name="chimney")
        for z in (14, 28, 36): cyl(1.35 - (z - 14) * .01, .5, MATS["steel_dark"], loc=(-W / 2 + 4, 4, H + z), seg=14, parent=root, name="chimney_band")
        tube((-W / 2 + 6, 4, H + 4), (W / 2 - 4, 4, H + 4), .5, MATS["steel_dark"], root, "pipe", 10); tube((-W / 2 + 6, 4, H), (-W / 2 + 6, 4, H + 4), .5, MATS["steel_dark"], root, "pipe_riser", 10)
    elif kind == "chp":
        box((W * .5, D * .6, 8.0), MATS["panel_wall_b"], loc=(-W * .2, 0, H + 4.0), bev=0, parent=root, name="boiler_hall")
        lathe([(0, 0), (4.0, 0), (3.0, 30), (2.4, 60), (2.2, 70), (0, 71)], MATS["panel_wall"], loc=(W * .3, 4, H), seg=18, parent=root, name="stack")
        for z in (20, 40, 60): cyl(2.9 - z * .013, .8, MATS["sign_red_glow"] if z == 60 else MATS["concrete_dark"], loc=(W * .3, 4, H + z), seg=18, parent=root, name="stack_band")
        for k in range(3): tube((-W * .3 + k * 3.0, -D / 2 - 2.0, 1.0), (-W * .3 + k * 3.0, -D / 2 - 2.0, 13.0), .6, MATS["steel_dark"], root, "pipe", 10)
        tube((-W * .3, -D / 2 - 2.0, 13.0), (W * .3, -D / 2 - 2.0, 13.0), .6, MATS["steel_dark"], root, "pipe_h", 10)
    else:
        pass
    box((W + .3, D + .3, .4), MATS["roof_tar"], loc=(0, 0, H + .2), bev=0, parent=root, name="roof")
    box((W, D, H + 2), None, loc=(0, 0, (H + 2) / 2), bev=0, name=name + "-col"); empty("ip_use", (0, -D / 2 - 3, 0), size=.3)
    return finish(name, W, D, H)

def substation():
    bmats(); root = empty("building", size=.5); name = "substation"; W, D, H = 10.0, 6.0, 4.2
    box((W, D, H), MATS["brick_wall"], loc=(0, 0, H / 2), bev=0, parent=root, name="mass"); box((W + .4, D + .4, .3), MATS["roof_tar"], loc=(0, 0, H + .15), bev=0, parent=root, name="roof")
    box((1.6, .15, 2.4), MATS["door_steel"], loc=(0, -D / 2 + .05, 1.2), bev=0, parent=root, name="door"); box((.5, .04, .5), MATS["paint_yellow"], loc=(2.0, -D / 2 - .02, 2.0), bev=0, parent=root, name="warning_sign")
    for k in range(3): box((.7, .04, 1.0), MATS["steel_dark"], loc=(-3.0 + k * .9, -D / 2 - .02, 1.5), bev=0, parent=root, name="vent")
    for k in range(4): cyl(.08, .5, MATS["insulator"], loc=(-3.6 + k * 2.4, 0, H + .55), seg=8, parent=root, name="insulator")
    box((W, D, H + .5), None, loc=(0, 0, (H + .5) / 2), bev=0, name=name + "-col"); empty("ip_use", (0, -D / 2 - 1.5, 0), size=.3); empty("ip_spark", (-3.6, 0, H + .8), size=.15)
    return finish(name, W, D, H)

def tower():
    return panel_building("residential_tower", 20, 6, 3.0, 18.0, "panel_wall_b", "loggia", (2, 3), tech=True, win=(1.4, 1.3, .9))

def modules():
    for nm, bays, floors, ent in (("module_wall_row", 1, 3, ()), ("module_entrance_bay", 1, 3, (0,))):
        bmats(); root = empty("module", size=.3); W = bays * 3.0; D = 11.5; H = floors * FH
        box((W - .5, D - .5, H), MATS["panel_wall"], loc=(0, 0, H / 2), bev=0, parent=root, name="mass")
        o = perforated("facade", bays, floors, 3.0, FH, 1.5, 1.3, .9, MATS["panel_wall"], MATS["building_window"], MATS["window_frame"], parent=root, skip=lambda i, j: (j == 0 and bool(ent))); place_facade(o, "front", W, D)
        if ent: entrance(root, 0, -D / 2 + .1)
        box((W, D, H), None, loc=(0, 0, H / 2), bev=0, name=nm + "-col"); finish(nm, W, D, H)
    bmats(); root = empty("module", size=.3); W, D, H = 3.0, 11.5, 3 * FH
    box((W - .5, D - .5, H), MATS["panel_wall"], loc=(0, 0, H / 2), bev=0, parent=root, name="mass")
    for side in ("front", "right"):
        o = perforated("facade_" + side, 1, 3, 3.0, FH, 1.5, 1.3, .9, MATS["panel_wall"], MATS["building_window"], MATS["window_frame"], parent=root); place_facade(o, side, W, D)
    box((W, D, H), None, loc=(0, 0, H / 2), bev=0, name="module_corner-col"); finish("module_corner", W, D, H)
    bmats(); root = empty("module", size=.3); W, D = 3.0, 11.5
    roof(root, W, D, 0.0, tech=False); box((W, D, .5), None, loc=(0, 0, .25), bev=0, name="module_roof_cap-col"); finish("module_roof_cap", W, D, 1.0)

BUILD = {
 "panel9_a": lambda: panel_building("panel9_a", 9, 12, 3.0, 11.5, "panel_wall", "none", (2, 6, 10)),
 "panel9_b": lambda: panel_building("panel9_b", 9, 12, 3.0, 11.5, "panel_wall_b", "loggia", (1, 5, 9)),
 "panel5_khrushchev": lambda: panel_building("panel5_khrushchev", 5, 10, 3.0, 10.0, "panel_wall", "open", (1, 4, 7), tech=False, win=(1.3, 1.3, .9)),
 "brick5": lambda: panel_building("brick5", 5, 8, 3.0, 11.0, "brick_wall", "none", (1, 5), tech=False, win=(1.2, 1.6, .8)),
 "stalin_house": stalin,
 "office_glass": office_glass,
 "residential_tower": tower,
 "shop_pavilion": lambda: pavilion("shop_pavilion", 12.0, 8.0, 4.0, "shop"),
 "metro_entrance": lambda: pavilion("metro_entrance", 10.0, 8.0, 4.6, "metro"),
 "cafe_vstrecha": lambda: pavilion("cafe_vstrecha", 10.0, 8.0, 4.0, "cafe"),
 "lobby_granit": lambda: pavilion("lobby_granit", 14.0, 9.0, 5.0, "granite"),
 "school": school,
 "market": market,
 "factory": lambda: industrial("factory"),
 "chp_plant": lambda: industrial("chp"),
 "warehouse": lambda: industrial("warehouse"),
 "substation": substation,
 "modules": modules,
}
which = os.environ.get("BLD", "all")
for k, f in BUILD.items():
    if which == "all" or which == k:
        t = f(); print("BUILT", k, t)
