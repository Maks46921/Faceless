"""blender -b -P build_scene.py -- [shots...]   demo city scene: street + 2 blocks, day / noir night renders -> D:/Faceless/renders/city/scene/*.png
Blender coords (Z up); street runs along X, road y -5..5, sidewalks 5..9, buildings front at |y|=9. Glb front (+Z gltf) = -Y in Blender."""
import bpy, math, sys, os, random
from mathutils import Vector, Euler

R = "D:/Faceless/models"
OUT = "D:/Faceless/renders/city/scene"
os.makedirs(OUT, exist_ok=True)
random.seed(7)
bpy.ops.wm.read_factory_settings(use_empty=True)
sc = bpy.context.scene
sc.render.engine = 'BLENDER_EEVEE'
sc.render.resolution_x, sc.render.resolution_y = 1600, 900
try: sc.eevee.taa_render_samples = 48
except Exception: pass
sc.view_settings.view_transform = 'AgX' if 'AgX' in bpy.types.ColorManagedViewSettings.bl_rna.properties['view_transform'].enum_items.keys() else 'Standard'

LIB = {}
libcoll = bpy.data.collections.new("LIB"); sc.collection.children.link(libcoll)
world_coll = bpy.data.collections.new("WORLD"); sc.collection.children.link(world_coll)


def hide_junk(o):
    n = o.name.lower()
    if "col" in n.split("-")[-1] or n.endswith("-col") or n.endswith("-convcol") or n.startswith("ip_"):
        o.hide_render = True; o.hide_viewport = True
    elif n.startswith("state_") and not n.startswith("state_ok"):
        o.hide_render = True; o.hide_viewport = True
    elif n.startswith("icosphere"):
        o.hide_render = True; o.hide_viewport = True
    elif o.type == 'ARMATURE':
        o.hide_render = True


def import_glb(path):
    before = set(bpy.data.objects)
    bpy.ops.import_scene.gltf(filepath=path)
    new = [o for o in bpy.data.objects if o not in before]
    for o in new: hide_junk(o)
    return new


def lib(sub, name):
    key = f"{sub}/{name}"
    if key in LIB: return LIB[key]
    new = import_glb(f"{R}/{sub}/{name}.glb")
    c = bpy.data.collections.new(name); bpy.data.collections.new
    sc.collection.children.link(c)
    for o in new:
        for cc in o.users_collection: cc.objects.unlink(o)
        c.objects.link(o)
    bpy.context.view_layer.layer_collection.children[c.name].exclude = True
    LIB[key] = c
    return c


def put(sub, name, x, y, rot=0, z=0.15, s=1.0):
    c = lib(sub, name)
    e = bpy.data.objects.new(name, None); e.instance_type = 'COLLECTION'; e.instance_collection = c
    e.location = (x, y, z); e.rotation_euler = (0, 0, math.radians(rot)); e.scale = (s, s, s)
    world_coll.objects.link(e)
    return e


def person(name, x, y, rot, action, off=0, z=0.15, far=False):
    new = import_glb(f"{R}/city/people/{name}{'_far' if far else ''}.glb")
    arm = [o for o in new if o.type == 'ARMATURE'][0]
    roots = [o for o in new if o.parent is None]
    holder = bpy.data.objects.new("h_" + name, None); world_coll.objects.link(holder)
    holder.location = (x, y, z); holder.rotation_euler = (0, 0, math.radians(rot))
    for o in roots: o.parent = holder
    for o in new:
        for cc in list(o.users_collection): cc.objects.unlink(o)
        world_coll.objects.link(o)
    act = [a for a in bpy.data.actions if a.name == action or a.name.startswith(action + "_")]
    act = [a for a in bpy.data.actions if a.name == action][0] if any(a.name == action for a in bpy.data.actions) else act[0]
    arm.animation_data_create()
    arm.animation_data.action = act
    if hasattr(act, "slots") and act.slots: arm.animation_data.action_slot = act.slots[0]
    f0, f1 = act.frame_range
    pose_frame = f0 + (off % max(1.0, f1 - f0)) if action.endswith("loop") else f0 + (f1 - f0) * 0.45
    return arm, pose_frame


def animal(name, x, y, rot, action, z=0.15):
    return person_like("animals", name, x, y, rot, action, z)


def person_like(sub, name, x, y, rot, action, z):
    new = import_glb(f"{R}/city/{sub}/{name}.glb")
    arm = [o for o in new if o.type == 'ARMATURE'][0]
    holder = bpy.data.objects.new("h_" + name, None); world_coll.objects.link(holder)
    holder.location = (x, y, z); holder.rotation_euler = (0, 0, math.radians(rot))
    for o in [o for o in new if o.parent is None]: o.parent = holder
    for o in new:
        for cc in list(o.users_collection): cc.objects.unlink(o)
        world_coll.objects.link(o)
    act = [a for a in bpy.data.actions if a.name == action and a.users == 0 or a.name == action][0]
    arm.animation_data_create(); arm.animation_data.action = act
    if hasattr(act, "slots") and act.slots: arm.animation_data.action_slot = act.slots[0]
    return arm, act.frame_range[0] + 6


POSES = []  # (armature, frame)


def mat(name, col, rough=.9, emit=None, strength=0):
    m = bpy.data.materials.new(name); m.use_nodes = True
    b = m.node_tree.nodes["Principled BSDF"]
    b.inputs["Base Color"].default_value = (*col, 1); b.inputs["Roughness"].default_value = rough
    if emit:
        b.inputs["Emission Color"].default_value = (*emit, 1); b.inputs["Emission Strength"].default_value = strength
    return m


def slab(name, x0, x1, y0, y1, z0, z1, m):
    bpy.ops.mesh.primitive_cube_add(); o = bpy.context.object; o.name = name
    o.scale = ((x1 - x0) / 2, (y1 - y0) / 2, (z1 - z0) / 2); o.location = ((x0 + x1) / 2, (y0 + y1) / 2, (z0 + z1) / 2)
    o.data.materials.append(m)
    for cc in list(o.users_collection): cc.objects.unlink(o)
    world_coll.objects.link(o); return o


M_ROAD = mat("asphalt", (.07, .07, .075), .95)
M_WALK = mat("sidewalk", (.34, .33, .31), .9)
M_CURB = mat("curb", (.5, .5, .48), .9)
M_PAINT = mat("paint", (.85, .85, .8), .8)
M_GRASS = mat("grass", (.13, .2, .09), 1)
M_DIRT = mat("dirt", (.2, .15, .1), 1)
M_YARD = mat("yard_asph", (.12, .12, .125), .95)

X0, X1 = -95, 95
slab("road", X0, X1, -5, 5, -.02, 0.0, M_ROAD)
slab("walk_n", X0, X1, 5, 9, 0, .15, M_WALK); slab("walk_s", X0, X1, -9, -5, 0, .15, M_WALK)
slab("curb_n", X0, X1, 4.85, 5.0, 0, .17, M_CURB); slab("curb_s", X0, X1, -5.0, -4.85, 0, .17, M_CURB)
slab("ground_n", X0, X1, 9, 90, -.05, .1, M_GRASS); slab("ground_s", X0, X1, -70, -9, -.05, .1, M_GRASS)
slab("yard_n", -66, -2, 22, 50, .1, .12, M_YARD)
slab("yard_path", -34, -20, 9, 24, .1, .12, M_YARD)
slab("dirt_s", 40, 80, -30, -9, .1, .11, M_DIRT)
for i in range(-15, 16):
    slab("dash", i * 6 - 1.5, i * 6 + 1.5, -.08, .08, 0, .012, M_PAINT)
for k in range(8):  # crosswalk at x=-6
    slab("zebra", -7.5 + k * .9, -6.9 + k * .9, -4.8, 4.8, 0, .012, M_PAINT)
for k in range(6):  # crosswalk x=36
    slab("zebra", 34.5 + k * 1.0, 35.2 + k * 1.0, -4.8, 4.8, 0, .012, M_PAINT)

B = "city/buildings"; V = "city/vehicles"; P = "city/props"
# north side (front toward -Y), front face at y=9 -> origin y = 9 + 6.5..
def north(name, cx, front_off): put(B, name, cx, 9 + front_off, 0, z=0.15)
def south(name, cx, front_off): put(B, name, cx, -9 - front_off, 180, z=0.15)

north("panel9_a", -52, 6.75)
north("brick5", -7.8, 6.5)
north("panel5_khrushchev", 22, 6.0)
north("residential_tower", 47, 9.99)
north("lobby_granit", 65.5, 5.6)
south("stalin_house", -42, 8.6)
south("cafe_vstrecha", -9, 4.9)
south("shop_pavilion", 6, 4.3)
south("metro_entrance", 20, 6.5)
south("office_glass", 52, 13.0)
# rear row & industry
put(B, "warehouse", -35, 60, 0, z=0.1); put(B, "school", 25, 62, 0, z=0.1)
put(B, "factory", 85, 75, 0, z=0.1); put(B, "chp_plant", 30, 95, 0, z=0.1)
put(B, "substation", -75, 38, 90, z=0.1)
put(B, "panel9_b", 80, -45, 180, z=0.1)
put(P, "garage_row", -45, 44, 0, z=0.12); put(P, "garage_row", -29, 44, 0, z=0.12)

# lamps (arm toward street) + ELEC poles + trees
LAMPS = []
for x in range(-85, 90, 18):
    put(P, "street_lamp", x, 5.6, 90); LAMPS.append((x - .0, 5.6 - 1.2, 5.75))
    if x + 9 != -22:
        put(P, "street_lamp", x + 9, -5.6, -90); LAMPS.append((x + 9, -5.6 + 1.2, 5.75))
for x in range(-80, 95, 24):
    put(P, "power_pole", x, -8.3, 90)
tree_cycle = ["tree_poplar", "tree_maple", "tree_birch", "tree_bare"]
for i, x in enumerate(range(-80, 92, 15)):
    if -14 < x < 40 and False: continue
    put(P, tree_cycle[i % 4], x + 3, 8.0 + (i % 2) * .3, random.uniform(0, 360), s=random.uniform(.9, 1.1))
for i, x in enumerate(range(-60, 85, 18)):
    put(P, tree_cycle[(i + 1) % 3], x, -8.3, random.uniform(0, 360))
# wires between poles
def wire(p0, p1, sag=0.7):
    cu = bpy.data.curves.new("w", 'CURVE'); cu.dimensions = '3D'; cu.bevel_depth = .015
    sp = cu.splines.new('BEZIER'); sp.bezier_points.add(2)
    mid = [(p0[i] + p1[i]) / 2 for i in range(3)]; mid[2] -= sag
    for bp, p in zip(sp.bezier_points, (p0, mid, p1)):
        bp.co = p; bp.handle_left_type = bp.handle_right_type = 'AUTO'
    o = bpy.data.objects.new("wire", cu); o.data.materials.append(mat("wire", (.02, .02, .02))); world_coll.objects.link(o)
for x in range(-80, 71, 24):
    for dy in (-1.0, 0.0, 1.0):
        wire((x, -8.3 + dy, 8.7), (x + 24, -8.3 + dy, 8.7))

# street furniture
put(P, "bus_stop", -14, 7.0, 0)
put(P, "bench", -17, 8.4, 0); put(P, "kiosk", 28, 7.2, 0); put(P, "ad_column", 3, 6.5, 0)
put(P, "traffic_light_car", -8.5, 5.5, 90); put(P, "traffic_light_ped", -8.5, 7.4, 90)
put(P, "traffic_light_car", -5.0, -5.5, -90); put(P, "traffic_light_ped", -5.0, -7.4, -90)
put(P, "sign_crossing", -5.3, 6.0, 0); put(P, "sign_street", 12, -6.5, 180); put(P, "sign_speed", 40, 6.0, 0)
put(P, "phone_booth", 37, 7.6, 0); put(P, "urn_street", 12, 5.8, 0); put(P, "urn_street", -26, 5.8, 0)
put(P, "shop_sign", -9, -9.2, 180, z=2.6); put(P, "shop_sign", 6, -9.2, 180, z=2.6)
put(P, "billboard", 75, 14, 0)
put(P, "transformer_booth", -63, 27, 0, z=.1); put(P, "antenna_tower", 61, 30, 0, z=.1)
put(P, "tower_crane", 70, -22, 0, z=.1)
# courtyards
put(P, "dumpster", -30, 12, 90); put(P, "dumpster", -22, 12, 90); put(P, "crate_stack", -26, 16, 0)
put(P, "swing", -50, 30, 0, z=.12); put(P, "slide", -56, 33, 0, z=.12); put(P, "sandbox", -45, 36, 0, z=.12)
put(P, "bench", -40, 30, 180, z=.12); put(P, "pullup_bar", -60, 38, 0, z=.12); put(P, "carpet_beater", -52, 40, 0, z=.12)
put(P, "laundry_line", -35, 38, 0, z=.12); put(P, "fire_escape", -30.5, 21.7, 0)
for i in range(6):
    put(P, "fence_mesh", -66 + i * 3.2, 49, 0, z=.12)
for i in range(4):
    put(P, "fence_picket", -33 + i * 3.1, 23, 0, z=.12); put(P, "fence_concrete", -22 + i * 3.2 + 10, 23, 0, z=.12)
put(P, "bush_a", -48, 26, 0, z=.12); put(P, "bush_b", -58, 26, 30, z=.12); put(P, "tree_birch", -41, 44, 0, z=.12)
put(P, "tree_maple", -62, 44, 0, z=.12); put(P, "tree_poplar", -33, 48, 0, z=.12)

# vehicles: heading +X rot=90, heading -X rot=-90 (glb heads -Y)
put(V, "car_militia", -20, -3.9, 90); put(V, "car_sedan", -34, -3.9, 90); put(V, "van_gazelle", -50, -3.9, 90)
put(V, "ambulance", 8, 3.9, -90); put(V, "car_moskvich", 24, -3.9, 90); put(V, "car_wagon", 46, -3.9, 90)
put(V, "car_sedan_green", 60, 3.9, -90); put(V, "truck_zil", -70, 3.9, -90); put(V, "car_sedan_roofrack", 70, -3.9, 90)
put(V, "trolleybus", -40, 1.7, -90); put(V, "car_sedan", 14, -1.7, 90); put(V, "tow_truck", 82, 1.7, -90)
put(V, "bus_city", -14, 3.6, 90) if False else None

# people
PEOPLE = [
    ("militia_patrol", -21.5, -6.4, 0, "idle_loop", 0), ("militia_inspector", -18.2, -6.6, 190, "talk_loop", 5),
    ("resident_old_f", -17, 8.3, 180, "sit_idle_loop", 0), ("resident_man", -12.3, 7.6, 20, "smoke_loop", 3),
    ("courier", 2, 3.0, 0, "run_loop", 4), ("schoolchild", -2.5, 6.2, 180, "walk_loop", 2),
    ("barista_f", -9, -7.7, 0, "idle_loop", 0), ("resident_young_f", 4, 6.8, 180, "phone_loop", 2),
    ("janitor", -28, -7.5, 90, "idle_look_loop", 0), ("kiosk_seller_f", 28.1, 8.2, 0, "idle_loop", 0),
    ("medic_f", 6.7, 5.5, 170, "talk_loop", 0), ("medic_m", 9.8, 5.6, 200, "idle_cold_loop", 0),
    ("guard_black", 62, 6.2, 180, "idle_loop", 0), ("bodyguard", 66.2, 6.2, 180, "idle_look_loop", 2),
    ("resident_old_m", 16, -7.0, 90, "walk_old_loop", 3), ("cleaner_f", 40, -7.4, 270, "walk_loop", 0),
    ("electrician", -62, 30, 90, "idle_loop", 0), ("resident_man", -4.0, -6.2, 0, "walk_loop", 6),
    ("resident_young_f", 33, 6.5, 0, "walk_loop", 9), ("schoolchild", -46, 34, 140, "idle_loop", 4),
    ("resident_old_f", -37, 31, 180, "idle_look_loop", 0),
]
for (n, x, y, r, a, off) in PEOPLE:
    arm, f = person(n, x, y, r, a, off, z=.15 if abs(y) > 5 else .12, far=(abs(x) > 50))
    POSES.append((arm, f))
for (n, x, y, r, a) in (("dog_shepherd", -45, 32, 120, "idle_loop"), ("dog_mutt", 24, 6.5, 300, "walk_loop"), ("cat", -31, 14, 90, "sit_idle_loop"),
                        ("pigeon", 1, 6.5, 10, "idle_loop"), ("pigeon", 1.8, 7.0, 80, "peck"), ("crow", -13, 8.3, 0, "idle_loop")):
    try:
        arm, f = animal(n, x, y, r, a); POSES.append((arm, f))
    except Exception as e:
        print("animal fail", n, e)

# pose all armatures at a common frame via NLA-free trick: scene frame = 1, per-armature set action frame offset by keyframe shift
sc.frame_start, sc.frame_end = 1, 1
for arm, f in POSES:
    ad = arm.animation_data; act = ad.action
    tr = ad.nla_tracks.new(); st = tr.strips.new("s", 1, act)
    if hasattr(act, "slots") and act.slots: st.action_slot = act.slots[0]
    st.frame_start_ui = 1 - (f - act.frame_range[0]); st.use_sync_length = False
    ad.action = None
    st.extrapolation = 'HOLD'

# ---------- lighting rigs ----------
day, night = [], []
sun = bpy.data.lights.new("sun", 'SUN'); sun.energy = 4.0; sun.angle = .02
so = bpy.data.objects.new("sun", sun); world_coll.objects.link(so); so.rotation_euler = (math.radians(55), math.radians(10), math.radians(30)); day.append(so)
moon = bpy.data.lights.new("moon", 'SUN'); moon.energy = .5; moon.color = (.55, .65, 1.0)
mo = bpy.data.objects.new("moon", moon); world_coll.objects.link(mo); mo.rotation_euler = (math.radians(50), 0, math.radians(-40)); night.append(mo)
for (lx, ly, lz) in LAMPS:
    l = bpy.data.lights.new("lamp", 'POINT'); l.energy = 900; l.color = (1, .72, .4); l.shadow_soft_size = .15; l.use_shadow = abs(lx) < 45
    o = bpy.data.objects.new("lamp", l); world_coll.objects.link(o); o.location = (lx, ly, lz - .3); night.append(o)
for (hx, hy, rot) in ((-20, -3.9, 90), (14, -1.7, 90), (-40, 1.7, -90), (8, 3.9, -90)):
    for dy in (-.6, .6):
        s = bpy.data.lights.new("hl", 'SPOT'); s.energy = 700; s.spot_size = math.radians(60); s.color = (1, .95, .8)
        o = bpy.data.objects.new("hl", s); world_coll.objects.link(o)
        d = 1 if rot == 90 else -1
        o.location = (hx + d * 2.0, hy + dy, .7)
        o.rotation_euler = (Vector((d, 0, -.04))).to_track_quat('-Z', 'Y').to_euler(); night.append(o)

w = bpy.data.worlds.new("w"); w.use_nodes = True; sc.world = w
bg = w.node_tree.nodes["Background"]
def set_mode(mode):
    for m in bpy.data.materials:
        if not m.use_nodes: continue
        b = m.node_tree.nodes.get("Principled BSDF")
        if b is None: continue
        n = m.name.split(".")[0]
        if n in ("building_window", "building_window_b", "glass_car", "glass_curtain"): b.inputs["Emission Strength"].default_value = (.55 if mode == "day" else .04)
        elif n == "building_window_lit": b.inputs["Emission Strength"].default_value = 1.6 if mode == "day" else 5.0
    for o in day: o.hide_render = mode != "day"
    for o in night: o.hide_render = mode != "night"
    if mode == "day":
        bg.inputs[0].default_value = (.55, .68, .9, 1); bg.inputs[1].default_value = 1.1
    else:
        bg.inputs[0].default_value = (.025, .035, .07, 1); bg.inputs[1].default_value = .5


def cam(name, loc, target, lens=30, ortho=None):
    c = bpy.data.cameras.new(name); c.lens = lens; c.clip_end = 600
    if ortho: c.type = 'ORTHO'; c.ortho_scale = ortho
    o = bpy.data.objects.new(name, c); world_coll.objects.link(o); o.location = loc
    o.rotation_euler = (Vector(target) - Vector(loc)).to_track_quat('-Z', 'Y').to_euler()
    return o

SHOTS = {
    "aerial": cam("aerial", (-40, -75, 120), (0, 12, 0), 32),
    "aerial_east": cam("aerial_east", (120, 60, 70), (0, 5, 2), 30),
    "plan": cam("plan", (0, 15, 250), (0, 15, 0), 30, ortho=230),
    "eye_street": cam("eye_street", (-92, -6.6, 1.65), (30, -2, 3.5), 28),
    "eye_busstop": cam("eye_busstop", (-6, 6.5, 1.65), (-14, -9, 3), 30),
    "eye_courtyard": cam("eye_courtyard", (-27, 12, 1.65), (-45, 33, 2.5), 24),
    "eye_militia": cam("eye_militia", (-25.5, -5.3, 1.65), (-18, -5.8, 1.3), 35),
    "eye_kiosk": cam("eye_kiosk", (14, 6.2, 1.65), (30, 7.5, 2), 32),
    "eye_crossing": cam("eye_crossing", (2.5, 7.8, 1.65), (-8, 0, 1.6), 32),
}

want = [a for a in sys.argv[sys.argv.index("--") + 1:]] if "--" in sys.argv else list(SHOTS)
modes = [m for m in want if m in ("day", "night")] or ["day", "night"]
shots = [a for a in want if a in SHOTS] or list(SHOTS)
for mode in modes:
    set_mode(mode)
    for s in shots:
        sc.camera = SHOTS[s]; sc.render.filepath = f"{OUT}/{s}_{mode}.png"
        bpy.ops.render.render(write_still=True); print("rendered", s, mode)
