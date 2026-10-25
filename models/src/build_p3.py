"""Stage 7: security (barrier gate, door with lock states) and VFX blanks (rings, discs, camera cone, marker sphere, shockwave, smoke, sparks, rain plane).
Run: D:\\Cosmoteer\\blender.exe -b -P D:\\Faceless\\models\\src\\build_p3.py"""
_s = open("D:/Faceless/models/src/build_p2.py", encoding="utf-8").read()
exec(_s[:_s.index("# ======================================================================= stepladder")])

# ======================================================================= barrier gate
def barrier():
    new(); RD, WH = mat("barrier_red", (.45, .03, .03), .6), mat("barrier_white", (.6, .6, .58), .6)
    base = empty("barrier_post")
    box((.34, .34, 1.0), MATS["paint_gray"], loc=(0, 0, .5), bev=.01, parent=base, name="cabinet", seg=2)
    box((.4, .4, .06), MATS["concrete_dark"], loc=(0, 0, .03), bev=.006, parent=base, name="plinth")
    box((.2, .02, .12), MATS["steel_dark"], loc=(0, -.17, .8), bev=.003, parent=base, name="hatch")
    cyl(.06, .08, MATS["steel_dark"], loc=(-.19, 0, 1.0), seg=12, rot=(0, math.pi / 2, 0), parent=base, name="pivot_housing")
    merge(base, "post_mesh")
    arm = empty("arm", (-.19, 0, 1.0), size=.1)
    for i in range(8):
        x = .3 + i * .5
        box((.5, .07, .1), RD if i % 2 == 0 else WH, loc=(x, 0, 0), bev=.004, parent=arm, name="segment")
    box((.12, .06, .12), MATS["steel_dark"], loc=(-.1, 0, 0), bev=.005, parent=arm, name="hub")
    box((.18, .08, .1), MATS["steel_dark"], loc=(-.28, 0, -.02), bev=.004, parent=arm, name="counterweight")
    merge(arm, "arm_mesh")
    animate(arm, "open", [(1, dict(rot=(0, 0, 0))), (30, dict(rot=(0, -1.45, 0)))])
    animate(arm, "close", [(1, dict(rot=(0, -1.45, 0))), (30, dict(rot=(0, 0, 0)))])
    so = empty("state_ok"); box((.08, .02, .04), emissive("led_green", (.1, 1, .2), 3), loc=(0, -.185, .93), bev=0, parent=so, name="lamp_g")
    sl = empty("state_loose"); box((.08, .02, .04), emissive("led_red", (1, .1, .05), 3), loc=(0, -.185, .93), bev=0, parent=sl, name="lamp_r")
    box((.4, .4, 1.06), None, loc=(0, 0, .53), bev=0, name="barrier_post-col"); box((4.0, .1, .12), None, loc=(2.2 - .19, 0, 1.0), bev=0, name="barrier_arm-col")
    empty("ip_use", (0, -.8, 0), size=.15); empty("ip_hand", (.2, -.17, .8), size=.08)
    done("barrier_gate", anims=True)

# ======================================================================= door with lock states
def door():
    new(); BR = mat("door_brown", (.14, .09, .06), .6); FR = MATS["paint_gray"]
    fr = empty("frame")
    for sx in (-.52, .52): box((.1, .16, 2.2), FR, loc=(sx, 0, 1.1), bev=.004, parent=fr, name="jamb")
    box((1.14, .16, .1), FR, loc=(0, 0, 2.15), bev=.004, parent=fr, name="head_jamb")
    box((1.14, .2, .08), MATS["concrete_dark"], loc=(0, 0, .04), bev=.004, parent=fr, name="threshold")
    merge(fr, "frame_mesh")
    def leaf(name, parent, angle=0.0, forced=False):
        hinge = empty(name, (-.46, -.02, 1.05), parent=parent, size=.06); hinge.rotation_euler = (0, 0, angle)
        box((.9, .045, 2.05), BR, loc=(.46, 0, 0), bev=.006, parent=hinge, name="leaf", seg=2)
        for z in (-.5, .5): box((.6, .005, .7), MATS["wood"], loc=(.46, -.025, z), bev=.003, parent=hinge, name="panel_rel")
        box((.12, .03, .035), MATS["steel"], loc=(.82, -.04, -.05), bev=.004, parent=hinge, name="handle")
        cyl(.022, .02, MATS["steel"], loc=(.82, -.03, .12), seg=10, rot=(math.pi / 2, 0, 0), parent=hinge, name="lock_cyl")
        box((.05, .006, .12), MATS["steel_dark"], loc=(.84, -.025, .12), bev=0, parent=hinge, name="lock_plate")
        if forced:
            box((.05, .04, .14), MATS["soot"], loc=(.84, -.03, .14), bev=0, parent=hinge, name="splinter_hole")
            for k in range(3): box((.012, .03, .06), MATS["wood"], loc=(.84 + .02 * k, -.05, .08 - .03 * k), bev=0, parent=hinge, name="splinter").rotation_euler = (0, .5 * k, .4)
        merge(hinge, name + "_mesh")
        return hinge
    so = empty("state_ok"); leaf("door_closed", so, 0.0)
    sl = empty("state_loose"); leaf("door_open", sl, 1.7)
    sb = empty("state_broken"); leaf("door_forced", sb, .35, True)
    d = leaf("door_anim", None, 0.0)
    animate(d, "open", [(1, dict(rot=(0, 0, 0))), (8, dict(rot=(0, 0, .12))), (24, dict(rot=(0, 0, 1.7)))])
    animate(d, "close", [(1, dict(rot=(0, 0, 1.7))), (18, dict(rot=(0, 0, .1))), (24, dict(rot=(0, 0, 0)))])
    animate(d, "kick", [(1, dict(rot=(0, 0, 0))), (3, dict(rot=(0, 0, .16))), (6, dict(rot=(0, 0, .03))), (9, dict(rot=(0, 0, .35)))])
    box((1.2, .2, 2.25), None, loc=(0, 0, 1.12), bev=0, name="door_frame-col")
    empty("ip_use", (0, -.9, 0), size=.15); empty("ip_hand", (.36, -.06, 1.0), size=.08)
    done("door_lockable", anims=True)

# ======================================================================= VFX blanks
def vfx_material(name, color=(1, 1, 1), strength=1.0): return mat(name, color, .9, 0.0, emit=color, emit_strength=strength)
def annulus(name, r_in, r_out, material, seg=48, z=.003, parent=None):
    bm = bmesh.new(); uv = bm.loops.layers.uv.new("UVMap")
    for i in range(seg):
        a0, a1 = 2 * math.pi * i / seg, 2 * math.pi * (i + 1) / seg
        v = [bm.verts.new((math.cos(a0) * r_in, math.sin(a0) * r_in, z)), bm.verts.new((math.cos(a0) * r_out, math.sin(a0) * r_out, z)),
             bm.verts.new((math.cos(a1) * r_out, math.sin(a1) * r_out, z)), bm.verts.new((math.cos(a1) * r_in, math.sin(a1) * r_in, z))]
        f = bm.faces.new(v)
        for l, (u_, v_) in zip(f.loops, ((0, i / seg), (1, i / seg), (1, (i + 1) / seg), (0, (i + 1) / seg))): l[uv].uv = (u_, v_)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    for f in bm.faces:
        if f.normal.z < 0: f.normal_flip()
    return mesh_obj(name, bm, material, parent=parent, smooth=False)
def card(name, w, h, material, flare=1.0, uvs=((0, 0), (1, 0), (1, 1), (0, 1))):
    bm = bmesh.new(); uv = bm.loops.layers.uv.new("UVMap")
    vs = [bm.verts.new((-w / 2, 0, 0)), bm.verts.new((w / 2, 0, 0)), bm.verts.new((w / 2 * flare, 0, h)), bm.verts.new((-w / 2 * flare, 0, h))]
    f = bm.faces.new(vs)
    for l, uvv in zip(f.loops, uvs): l[uv].uv = uvv
    return mesh_obj(name, bm, material, smooth=False)
def vfx_all():
    for r in (.5, 1.0, 2.0, 4.0):
        new(); m = vfx_material("vfx_ring", (1, 1, 1), 1.0)
        annulus("ring_soft", r * .86, r, m); annulus("ring_inner", r * .55, r * .58, m); annulus("disc_fill", .0001, r * .54, vfx_material("vfx_disc", (1, 1, 1), .5))
        empty("ip_hit", (0, 0, 0), size=.1); export(f"vfx_circle_{str(r).replace('.', '_')}")
    new(); m = vfx_material("vfx_beam", (1, .95, .8), .7)
    bm = bmesh.new(); uv = bm.loops.layers.uv.new("UVMap"); seg = 24; L_, R_ = 8.0, 2.4
    ap = bm.verts.new((0, 0, 0))
    ring = [bm.verts.new((math.cos(2 * math.pi * i / seg) * R_, -L_, math.sin(2 * math.pi * i / seg) * R_)) for i in range(seg)]
    for i in range(seg):
        f = bm.faces.new((ap, ring[(i + 1) % seg], ring[i]))
        for l, uvv in zip(f.loops, ((.5, 0), ((i + 1) / seg, 1), (i / seg, 1))): l[uv].uv = uvv
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    mesh_obj("beam_cone", bm, m, smooth=False); empty("ip_hand", (0, 0, 0), size=.1); export("vfx_camera_cone")
    new(); m = vfx_material("vfx_marker", (1, .75, .2), 3.0); sphere(.12, m, loc=(0, 0, 0), seg=16, rings=10, name="marker"); empty("ip_hand", (0, 0, 0), size=.1); export("vfx_marker_sphere")
    new(); annulus("shock_ring", .88, 1.0, vfx_material("vfx_shock", (1, 1, 1), 1.5), seg=64); annulus("shock_inner", .7, .88, vfx_material("vfx_shock_soft", (1, 1, 1), .5), seg=64, z=.0025)
    empty("ip_hit", (0, 0, 0), size=.1); export("vfx_shockwave")
    for vi, (h, w) in enumerate(((1.6, 1.0), (2.4, 1.4), (3.4, 1.8))):
        new(); m = mat("vfx_smoke", (.35, .35, .36), 1.0)
        for k in range(3):
            o = card(f"smoke_card_{k}", w, h, m, 1.4); o.rotation_euler = (0, 0, k * math.pi / 3 + vi * .4)
        empty("ip_spark", (0, 0, 0), size=.1); export(f"vfx_smoke_plume_{vi + 1}")
    new(); m = mat("vfx_smoke", (.3, .3, .31), 1.0); rnd = random.Random(8)
    for i in range(9):
        r = .26 + .05 * math.sin(i * 1.3) + i * .03
        s_ = bmesh.new(); bmesh.ops.create_icosphere(s_, subdivisions=2, radius=r)
        mesh_obj(f"smoke_puff_{i}", s_, m, loc=(rnd.uniform(-.12, .12) + i * .03, rnd.uniform(-.12, .12), i * .22), smooth=True)
    empty("ip_spark", (0, 0, 0), size=.1); export("vfx_smoke_puffs")
    new(); m = vfx_material("vfx_spark", (1, .8, .3), 6.0)
    for k in range(10):
        a = k * 2 * math.pi / 10 + (k % 2) * .2; ln = .22 + .1 * (k % 3)
        d_ = Vector((math.cos(a), 0, math.sin(a))); n_ = Vector((0, 1, 0)).cross(d_) * .012
        for tag_, (p0, p1) in (("a", (n_, -n_)), ("b", (-n_, n_))):
            bm = bmesh.new(); bm.faces.new([bm.verts.new(p0), bm.verts.new(p1), bm.verts.new(d_ * ln)]); mesh_obj(f"spark_{k}_{tag_}", bm, m, smooth=False)
    empty("ip_spark", (0, 0, 0), size=.1); export("vfx_spark_flash")
    new(); m = mat("vfx_rain", (.7, .75, .85), .5, 0.0, emit=(.7, .75, .85), emit_strength=.3)
    o = card("rain_plane", 6, 6, m, 1.0, ((0, 0), (4, 0), (4, 4), (0, 4))); empty("ip_hit", (0, 0, 0), size=.1); export("vfx_rain_plane")

barrier(); door(); vfx_all()
