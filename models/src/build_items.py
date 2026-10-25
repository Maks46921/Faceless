"""Hand-held / ground items: knife, syringe, crowbar, pistol, holster, throwing rock.
Run: D:\\Cosmoteer\\blender.exe -b -P D:\\Faceless\\models\\src\\build_items.py
For every item two files: item_<name>_hand.glb (origin = grip point, ip_hand at origin, blade/muzzle points to +Z of glTF) and
item_<name>_ground.glb (lying on the floor, origin at floor centre, ip_hand at the grip, a -convcol box for collision)."""
import sys
sys.path.insert(0, "D:/Faceless/models/src")
exec(open("D:/Faceless/models/src/lib_props.py", encoding="utf-8").read())

def sides_to_floor(o):
    set_active(o); bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
    zs = [v.co.z for v in o.data.vertices]; xs = [v.co.x for v in o.data.vertices]; ys = [v.co.y for v in o.data.vertices]
    cx, cy = (max(xs) + min(xs)) / 2, (max(ys) + min(ys)) / 2
    for v in o.data.vertices: v.co.x -= cx; v.co.y -= cy; v.co.z -= min(zs)
    return cx, cy, min(zs)

def build_item(name, builder, ground_rot=(math.pi / 2, 0, 0), ground_yaw=.5, grip=(0, 0, 0)):
    """builder() returns list of mesh objects modelled along +X with the grip centre at the origin."""
    # ---- hand variant: join, point along -Y (glTF +Z)
    fresh(); palette(); parts = builder(); m = join(parts, name); smooth_angle([m], 45)
    m.rotation_euler = (0, 0, -math.pi / 2); set_active(m); bpy.ops.object.transform_apply(rotation=True)
    empty("ip_hand", (0, 0, 0), size=.03)
    export(f"item_{name}_hand")
    # ---- ground variant
    fresh(); palette(); parts = builder(); m = join(parts, name + "_ground"); smooth_angle([m], 45)
    m.rotation_euler = ground_rot; set_active(m); bpy.ops.object.transform_apply(rotation=True)
    gx = Vector(grip); m.location = (0, 0, 0)
    # lie on the floor: grip point after rotation
    g = Matrix.Rotation(ground_rot[0], 3, 'X') @ gx
    set_active(m); zs = [v.co.z for v in m.data.vertices]
    for v in m.data.vertices: v.co.z -= min(zs)
    g.z -= min(zs)
    m.rotation_euler = (0, 0, ground_yaw); bpy.ops.object.transform_apply(rotation=True)
    g = Matrix.Rotation(ground_yaw, 3, 'Z') @ g
    bb = [v.co.copy() for v in m.data.vertices]
    mn = Vector((min(v.x for v in bb), min(v.y for v in bb), 0)); mx = Vector((max(v.x for v in bb), max(v.y for v in bb), max(v.z for v in bb)))
    col = box(((mx.x - mn.x), (mx.y - mn.y), max(.01, mx.z)), None, ((mx.x + mn.x) / 2, (mx.y + mn.y) / 2, max(.01, mx.z) / 2), bev=0, name=name + "_ground-convcol")
    empty("ip_hand", tuple(g), size=.03)
    export(f"item_{name}_ground")

# ---------------- knife (kitchen) ----------------
def knife():
    P = []
    P.append(extrude_profile([(0, 0), (.10, -.004), (.16, .004), (.198, .030), (.17, .0365), (0, .0365)], .0022, MATS["steel"], loc=(0, 0, -.018), name="blade", bev=.0004))
    P.append(box((.118, .0165, .030), MATS["plastic_black"], loc=(-.059, 0, 0), bev=.0045, name="handle"))
    P.append(box((.012, .0185, .034), MATS["steel"], loc=(.002, 0, 0), bev=.002, name="bolster"))
    for x in (-.03, -.085): P.append(cyl(.0034, .0195, MATS["steel"], loc=(x, 0, 0), seg=8, rot=(math.pi / 2, 0, 0), name="rivet"))
    return P
# ---------------- syringe ----------------
def syringe():
    P = []
    P.append(cyl(.0088, .10, MATS["glass"], loc=(0, 0, 0), seg=14, rot=(0, math.pi / 2, 0), name="barrel"))
    P.append(cyl(.0075, .062, MATS["liquid_amber"], loc=(.0, 0, 0), seg=12, rot=(0, math.pi / 2, 0), name="liquid"))
    P.append(cyl(.0040, .012, MATS["plastic_black"], loc=(.056, 0, 0), seg=10, rot=(0, math.pi / 2, 0), r2=.0022, name="hub"))
    P.append(cyl(.0011, .036, MATS["steel"], loc=(.080, 0, 0), seg=6, rot=(0, math.pi / 2, 0), r2=.0006, name="needle"))
    P.append(box((.003, .034, .013), MATS["plastic_black"], loc=(-.052, 0, 0), bev=.0012, name="flange"))
    P.append(cyl(.0028, .075, MATS["plastic_black"], loc=(-.092, 0, 0), seg=8, rot=(0, math.pi / 2, 0), name="plunger"))
    P.append(cyl(.0078, .007, MATS["rubber"], loc=(-.030, 0, 0), seg=12, rot=(0, math.pi / 2, 0), name="stopper"))
    P.append(cyl(.0115, .003, MATS["plastic_black"], loc=(-.131, 0, 0), seg=14, rot=(0, math.pi / 2, 0), name="thumbpad"))
    return P
# ---------------- crowbar ----------------
def crowbar():
    pts = [(.30, .075), (.31, .045), (.298, .018), (.265, .002), (.2, 0), (-.2, 0), (-.265, -.002), (-.30, -.015), (-.318, -.04)]
    cu = bpy.data.curves.new("cb", 'CURVE'); cu.dimensions = '3D'; cu.bevel_depth = .0115; cu.bevel_resolution = 3; cu.resolution_u = 8; cu.use_fill_caps = True
    sp = cu.splines.new('NURBS'); sp.points.add(len(pts) - 1)
    for p, (x, z) in zip(sp.points, pts): p.co = (x, 0, z, 1)
    sp.use_endpoint_u = True; sp.order_u = 4
    o = bpy.data.objects.new("bar", cu); collection().objects.link(o); set_active(o)
    bpy.ops.object.convert(target='MESH'); o = bpy.context.object; o.data.materials.append(MATS["steel_dark"])
    P = [o]
    P.append(box((.045, .026, .008), MATS["steel_dark"], loc=(-.325, 0, -.046), bev=.0015, rot=(0, .9, 0), name="claw"))
    P.append(box((.012, .014, .012), MATS["steel"], loc=(.318, 0, .082), bev=.002, name="tip"))
    return P
# ---------------- service pistol (PM-like) ----------------
def pistol():
    P = []
    s = MATS["gun_metal"]
    P.append(box((.158, .0255, .031), s, loc=(.0, 0, .0225), bev=.0025, name="slide"))
    P.append(box((.13, .023, .018), s, loc=(-.004, 0, -.001), bev=.002, name="frame"))
    P.append(cyl(.0055, .028, s, loc=(.092, 0, .0185), seg=10, rot=(0, math.pi / 2, 0), name="muzzle"))
    P.append(box((.044, .0245, .088), s, loc=(-.062, 0, -.052), bev=.003, rot=(0, .34, 0), name="grip_frame"))
    P.append(box((.040, .0285, .082), MATS["grip_brown"], loc=(-.062, 0, -.053), bev=.003, rot=(0, .34, 0), name="grip_panel"))
    P.append(box((.028, .0125, .004), s, loc=(.022, 0, -.015), bev=.001, name="guard_bottom"))
    P.append(box((.004, .0125, .02), s, loc=(.036, 0, -.007), bev=.001, name="guard_front"))
    P.append(box((.006, .0045, .014), s, loc=(.012, 0, -.006), bev=.001, name="trigger", rot=(0, .3, 0)))
    P.append(box((.006, .004, .005), s, loc=(.078, 0, .0405), bev=.0008, name="front_sight"))
    P.append(box((.01, .012, .004), s, loc=(-.068, 0, .0402), bev=.0008, name="rear_sight"))
    P.append(box((.006, .005, .008), s, loc=(-.082, 0, .028), bev=.001, name="hammer"))
    for i in range(5): P.append(box((.0016, .0265, .026), s, loc=(-.062 + i * .006, 0, .0235), bev=.0004, seg=1, name="serration"))
    P.append(cyl(.003, .0015, MATS["steel"], loc=(-.062, .0148, -.052), seg=8, rot=(math.pi / 2, 0, 0), name="grip_screw"))
    return P
def holster():
    P = []
    L_ = MATS["leather"]
    P.append(box((.062, .042, .15), L_, loc=(0, 0, 0), bev=.008, seg=3, name="pouch", taper=.9))
    P.append(box((.07, .046, .05), L_, loc=(0, 0, .06), bev=.007, seg=3, name="flap"))
    P.append(box((.03, .012, .1), L_, loc=(0, .027, .0), bev=.003, name="belt_loop"))
    P.append(cyl(.006, .004, MATS["steel"], loc=(0, -.024, .075), seg=10, rot=(math.pi / 2, 0, 0), name="snap"))
    P.append(box((.03, .024, .05), MATS["grip_brown"], loc=(0, 0, .098), bev=.004, name="grip_peek"))
    for i in range(6): P.append(box((.052, .0015, .002), MATS["steel_dark"], loc=(0, -.0225, -.05 + i * .018), bev=0, seg=1, name="stitch"))
    return P
def rock():
    return [rock_blob(.052, MATS["stone"], seed=7, flat=.78, subdiv=2, rough=.22, name="rock")]

if __name__ == "__main__" or True:
    build_item("knife", knife, ground_rot=(math.pi / 2, 0, 0), ground_yaw=.6)
    build_item("syringe", syringe, ground_rot=(math.pi / 2, 0, 0), ground_yaw=-.4)
    build_item("crowbar", crowbar, ground_rot=(math.pi / 2, 0, 0), ground_yaw=.25)
    build_item("pistol", pistol, ground_rot=(math.pi / 2, 0, 0), ground_yaw=.8, grip=(-.06, 0, -.04))
    # holster: standing on a surface, ip_hand at the pistol grip
    fresh(); palette(); parts = holster(); m = join(parts, "holster"); smooth_angle([m], 45)
    zs = [v.co.z for v in m.data.vertices]
    for v in m.data.vertices: v.co.z -= min(zs)
    empty("ip_hand", (0, 0, .17), size=.03); export("item_holster")
    fresh(); palette(); parts = rock(); m = join(parts, "rock_throw"); smooth_angle([m], 60)
    empty("ip_hand", (0, 0, 0), size=.03); export("rock_throw")
    fresh(); palette(); parts = rock(); m = join(parts, "rock_throw_ground")
    zs = [v.co.z for v in m.data.vertices]
    for v in m.data.vertices: v.co.z -= min(zs)
    box((.1, .1, .045), None, (0, 0, .0225), bev=0, name="rock_throw_ground-convcol"); empty("ip_hand", (0, 0, .03), size=.03); export("rock_throw_ground")
