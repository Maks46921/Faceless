"""Part 3 of build_human_v4.py (exec'd inside build_human_v4_rig.py before the NLA/export step): stage 8 movement animations and abandoned-body poses.
Geometry the IK targets assume: obstacle/wall front face at y=-0.30 (character faces -Y), ledge/edge top heights 0.9 / 1.4 / 1.9 m, window sill 0.95 m,
bar/handle heights 1.0-1.35 m. All loops end with _loop."""
MOVES = []

def kf(f, pose=None, loc=None, iks=None):
    return (f, mixp(S0(), pose or {}), loc or {}, ({k: (0, v[0], v[1]) for k, v in (iks or {}).items()}) if iks else None)
def seq(name, n, keys, loop=False):
    make(name, n, [(f, p, l, i) if i else (f, p, l) for f, p, l, i in keys], loop=loop); MOVES.append(name)
def crouch(k=1.0, spine=22, head=-12):
    return {"spine": (spine * k, 0, 0), "spine2": (spine * .5 * k, 0, 0), "head": (head * k, 0, 0), **L("L", 102 * k, 112 * k, -8 * k), **L("R", 102 * k, 112 * k, -8 * k),
            **A_("L", 40 * k, 14, 70 * k), **A_("R", 40 * k, 14, 70 * k)}, {"pelvis": (0, .1 * k, -.5 * k)}
def lerp_pose(a, b, t): return mixp(a, b, t)

# ---- reaching, hanging, pulling up
HOLD_Y, HOLD_Z = -.32, 2.05
def hands_at(y, z): return {"hand.L": (y, z), "hand.R": (y, z)}
seq("reach_grab", 24, [kf(0), kf(8, {"spine": (10, 0, 0), "head": (-14, 0, 0)}, {"pelvis": (0, -.04, 0)}, {"hand.R": (-.4, 1.95)}), kf(14, {"spine": (14, 0, 0), "head": (-16, 0, 0), **G("R", .95, 0, .7)}, {"pelvis": (0, -.06, 0)}, {"hand.R": (-.4, 2.0)}), kf(24, {**G("R", .95, 0, .7)}, {"pelvis": (0, -.05, 0)}, {"hand.R": (-.4, 2.0)})])
def hang(t, sway=0):
    p = {"spine": (-4, 0, 3 * sway), "head": (-10, 0, 0), **L("L", -8 + 5 * sway, 22), **L("R", -4 - 5 * sway, 28), **G("L", .95, 0, .6), **G("R", .95, 0, .6)}
    return p
seq("hang_idle_loop", 48, [kf(f, hang(0, math.sin(2 * math.pi * f / 48)), {"root": (0, .0, -.14 + .01 * math.sin(2 * math.pi * f / 48))}, hands_at(HOLD_Y, HOLD_Z)) for f in range(0, 49, 6)], loop=True)
seq("pull_up", 48, [kf(0, hang(0), {"root": (0, 0, -.14)}, hands_at(HOLD_Y, HOLD_Z)), kf(14, {**hang(0), "spine": (10, 0, 0)}, {"root": (0, 0, .15)}, hands_at(HOLD_Y, HOLD_Z)),
                    kf(30, {"spine": (18, 0, 0), "head": (-18, 0, 0), **L("L", 20, 60), **L("R", 10, 70), **G("L", .95, 0, .6), **G("R", .95, 0, .6)}, {"root": (0, -.02, .5)}, hands_at(HOLD_Y, HOLD_Z)),
                    kf(48, {"spine": (18, 0, 0), "head": (-18, 0, 0), **L("L", 20, 60), **L("R", 10, 70), **G("L", .95, 0, .6), **G("R", .95, 0, .6)}, {"root": (0, -.02, .52)}, hands_at(HOLD_Y, HOLD_Z))])

# ---- vertical climbing (rope/pipe/bars): copies of the ladder cycle with new names and a tired variant
def climb_gen(f, n, tired):
    u = (f / n) % 1.0; zr = .6 * u; sw = sstep
    hz_R = 1.8 if u < .5 else 1.8 + .6 * sw((u - .5) / .5); hz_L = (1.5 + .6 * sw(u / .5)) if u < .5 else 2.1
    fz_R = .3 if u < .5 else .3 + .6 * sw((u - .5) / .5); fz_L = (0.0 + .6 * sw(u / .5)) if u < .5 else .6
    p = mixp(S0(), {"spine": ((8 if not tired else 16), 0, 2.5 * math.sin(2 * math.pi * u)), "spine2": (6, 0, 0), "head": ((-16 if not tired else 8), 0, 4 * math.sin(4 * math.pi * u) if tired else 0),
                    "pelvis": (4, (3 if tired else 0) * math.sin(2 * math.pi * u), 4 * math.sin(2 * math.pi * u)), **G("L", .9, 0, .6), **G("R", .9, 0, .6)})
    loc = {"root": (0, 0, zr), "pelvis": (0, -.12, -.03 - (.04 if tired else 0))}
    iks = {"hand.R": (0, LADDER_Y + .02, hz_R), "hand.L": (0, LADDER_Y + .02, hz_L), "foot.R": (0, LADDER_Y + .13, fz_R + .09), "foot.L": (0, LADDER_Y + .13, fz_L + .09)}
    return p, loc, iks
make("climb_vertical_loop", 32, lambda f: climb_gen(f, 32, False), 2, True); MOVES.append("climb_vertical_loop")
make("climb_tired_loop", 48, lambda f: climb_gen(f, 48, True), 3, True); MOVES.append("climb_tired_loop")

# ---- climbing over an obstacle (wall/fence) of height H: hands on top, foot on wall, body over, drop on the far side
def over(name, H):
    top = H + .02; foot = min(H * .5, .9)
    pose_g = {**G("L", .95, 0, .6), **G("R", .95, 0, .6)}
    seq(name, 54, [
        kf(0, {}, {}),
        kf(8, {"spine": (14, 0, 0), "head": (-14, 0, 0), **pose_g}, {"pelvis": (0, -.1, -.03)}, {"hand.L": (-.36, top), "hand.R": (-.36, top)}),
        kf(20, {"spine": (24, 0, 0), "head": (-18, 0, 0), **pose_g}, {"root": (0, -.1, H * .22), "pelvis": (0, -.06, -.05)}, {"hand.L": (-.36, top), "hand.R": (-.36, top), "foot.R": (-.3, foot)}),
        kf(32, {"spine": (46, 0, 0), "spine2": (24, 0, 0), "head": (-26, 0, 0), **L("L", 70, 90, 0), **L("R", 20, 70), **pose_g}, {"root": (0, -.3, H * .78), "pelvis": (0, -.04, -.08)}, {"hand.L": (-.4, top), "hand.R": (-.4, top)}),
        kf(42, {"spine": (30, 0, 0), "head": (-12, 0, 0), **L("L", -10, 20), **L("R", 50, 60), **pose_g}, {"root": (0, -.65, H * .74)}, {"hand.L": (-.46, top), "hand.R": (-.46, top), "foot.R": (-.55, top + .05)}),
        kf(54, {"spine": (14, 0, 0), **L("L", 14, 22), **L("R", 6, 18)}, {"root": (0, -.9, 0), "pelvis": (0, 0, -.1)})])
over("climb_over_low", .9); over("climb_over_mid", 1.4); over("climb_over_high", 1.9)

# ---- jumping, crouching, crawling
jl = []
for f, k in ((0, 0), (7, 1), (11, 2), (15, 3), (21, 4), (27, 5), (31, 6), (36, 0)):
    if k == 6: p, l = mixp(S0(), {"spine": (38, 0, 0), "spine2": (20, 0, 0), "head": (-20, 0, 0), **L("L", 100, 120), **L("R", 96, 118), **A_("L", 30, 30, 50), **A_("R", 30, 30, 50)}), {"pelvis": (0, .1, -.44), "root": (0, -.25, 0)}
    else: p, l = jpose(k)
    if k in (1, 2, 3, 4, 5): l = dict(l); l["root"] = (0, l.get("root", (0, 0, 0))[1] - .12 * (k - 1), l.get("root", (0, 0, 0))[2])
    jl.append((f, p, l))
keyed("jump_land", 36, jl); MOVES.append("jump_land")
def crouch_idle(f):
    k = 1.0; p, l = crouch(1.0); u = f / 48; s_ = math.sin(2 * math.pi * u); p["head"] = (-12 + 2 * s_, 0, 6 * math.sin(2 * math.pi * u)); p["spine2"] = (11 + 1.5 * s_, 0, 0); return p, l
make("crouch_idle_loop", 48, crouch_idle, 4, True); MOVES.append("crouch_idle_loop")
def crouch_walk(f):
    u = f / 24; p, loc = gait(u, .55); q, l2 = crouch(.95)
    for k in list(q):
        if k not in ("thigh.L", "thigh.R", "shin.L", "shin.R"): p[k] = q[k]
    p["thigh.L"] = (q["thigh.L"][0] + 22 * math.sin(2 * math.pi * u), 0, 0); p["thigh.R"] = (q["thigh.R"][0] - 22 * math.sin(2 * math.pi * u), 0, 0)
    p["shin.L"] = (-110 + 14 * max(0, math.sin(2 * math.pi * u)), 0, 0); p["shin.R"] = (-110 + 14 * max(0, -math.sin(2 * math.pi * u)), 0, 0)
    loc = dict(l2); loc["pelvis"] = (loc["pelvis"][0], loc["pelvis"][1], loc["pelvis"][2] + .02 * abs(math.sin(2 * math.pi * u))); return p, loc
make("crouch_walk_loop", 24, crouch_walk, 2, True); MOVES.append("crouch_walk_loop")
def crawl(f):
    u = f / 32; s_ = math.sin(2 * math.pi * u); c_ = math.cos(2 * math.pi * u)
    p = mixp(S0(), {"spine": (-4, 0, 3 * s_), "spine2": (-6, 0, -3 * s_), "head": (-30 + 3 * c_, 0, 10 * s_), "neck": (-8, 0, 0),
                    **A_("L", 140 + 24 * s_, 30, 40 + 25 * max(0, -s_)), **A_("R", 140 - 24 * s_, 30, 40 + 25 * max(0, s_)),
                    **L("L", 10 - 25 * s_, 70 + 25 * max(0, s_), -10), **L("R", 10 + 25 * s_, 70 + 25 * max(0, -s_), -10), **G("L", .4), **G("R", .4)})
    return p, {**LY_LOC, "root": (0, -.02, .12 + .01 * abs(s_))}
make("crawl_loop", 32, crawl, 2, True); MOVES.append("crawl_loop")
def window_seq(name, inward):
    # sill at 0.95 m, window plane y=-0.30; inward: outside (y=-1.0) -> inside (y=+0.6)
    sit = {"spine": (14, 0, 0), "head": (-8, 0, 0), **L("L", 70, 70), **L("R", 70, 70), **G("L", .9, 0, .6), **G("R", .9, 0, .6)}
    keys = [kf(0, {"spine": (14, 0, 0)}, {"root": (0, -.9, 0)}),
            kf(14, {"spine": (24, 0, 0), "head": (-14, 0, 0), **L("L", 70, 90), **L("R", 20, 40), **G("L", .9, 0, .6), **G("R", .9, 0, .6)}, {"root": (0, -.6, .45)}, {"hand.L": (-.2, .98), "hand.R": (-.2, .98)}),
            kf(28, sit, {"root": (0, -.28, .98), "pelvis": (0, 0, -.05)}, {"hand.L": (-.18, .98), "hand.R": (-.18, .98)}),
            kf(42, {"spine": (-10, 0, 0), "head": (-6, 0, 0), **L("L", 80, 20), **L("R", 78, 14), **G("L", .9, 0, .6), **G("R", .9, 0, .6)}, {"root": (0, .25, .85)}, {"hand.L": (-.12, .98), "hand.R": (-.12, .98)}),
            kf(60, {"spine": (4, 0, 0), **L("L", 6, 10), **L("R", 4, 8)}, {"root": (0, .6, 0)})]
    if not inward:
        keys = [(f if False else 60 - f, p, l, i) for f, p, l, i in reversed(keys)]
    seq(name, 60, keys)
window_seq("crawl_in_window_feet_first", True); window_seq("crawl_out_window_back", False)

# ---- balance and careful movement
def balance_idle(f):
    u = f / 48; s_ = math.sin(2 * math.pi * u)
    p = mixp(S0(), {"spine": (3, 0, 0), "spine2": (0, 4 * s_, 0), "head": (-6, 0, 6 * math.sin(2 * math.pi * u + 1)), **A_("L", 6, 62 + 6 * s_, 10), **A_("R", 6, 62 - 6 * s_, 10), **L("L", 3, 8, 0, 0, -4), **L("R", 3, 8, 0, 0, -4), "pelvis": (0, 3 * s_, 0)})
    return p, {"pelvis": (0, 0, -.02 + .005 * s_)}
make("balance_idle_loop", 48, balance_idle, 4, True); MOVES.append("balance_idle_loop")
def balance_walk(f):
    u = f / 32; s_ = math.sin(2 * math.pi * u); c_ = math.cos(2 * math.pi * u)
    p = mixp(S0(), {"spine": (3, 0, 0), "spine2": (0, 5 * s_, 0), "head": (-6, 0, 0), **A_("L", 6, 64 + 7 * s_, 10), **A_("R", 6, 64 - 7 * s_, 10), "pelvis": (0, 4 * s_, 0)})
    p.update({"thigh.L": (4, 12 + 16 * max(0, c_), 0), "thigh.R": (4, -(12 + 16 * max(0, -c_)) * -1, 0), "shin.L": (-8 - 22 * max(0, c_), 0, 0), "shin.R": (-8 - 22 * max(0, -c_), 0, 0)})
    return p, {"pelvis": (.06 * s_, 0, -.03)}
make("balance_walk_loop", 32, balance_walk, 2, True); MOVES.append("balance_walk_loop")
def careful(f):
    u = f / 36; p, l = gait(u, .45); p["spine"] = (10, 0, 0); p["head"] = (14, 0, 0); p.update(A_("L", 4, 28, 30)); p.update(A_("R", 4, 28, 30))
    for sd in "LR": p[f"shin.{sd}"] = (p[f"shin.{sd}"][0] - 10, 0, 0)
    l = dict(l); l["pelvis"] = (0, 0, -.06); return p, l
make("careful_step_loop", 36, careful, 3, True); MOVES.append("careful_step_loop")
seq("slip_wet", 30, [kf(0), kf(5, {"spine": (-8, 0, 0), **L("L", 28, 4, 12), **L("R", -6, 10), **A_("L", -20, 40, 20), **A_("R", -20, 40, 20)}, {"pelvis": (0, .03, -.03)}),
                      kf(12, {"spine": (-18, 0, 0), "head": (-12, 0, 0), **L("L", 52, 2, 20), **L("R", -20, 24), **A_("L", -40, 70, 10), **A_("R", -50, 80, 10)}, {"pelvis": (0, .12, -.14)}),
                      kf(22, {"spine": (6, 0, 0), **L("L", 30, 14), **L("R", 6, 16), **A_("L", 20, 30, 30), **A_("R", 20, 30, 30)}, {"pelvis": (0, .02, -.05)}), kf(30)])
seq("creak_flinch", 24, [kf(0), kf(4, {"spine": (14, 0, 0), "head": (-6, 0, 0), **L("L", 30, 50), **L("R", 24, 48), **A_("L", 30, 50, 40), **A_("R", 30, 50, 40), "shoulder.L": (8, 0, 0), "shoulder.R": (8, 0, 0)}, {"pelvis": (0, .02, -.12)}),
                         kf(14, {"spine": (12, 0, 0), "head": (14, 0, 12), **L("L", 28, 46), **L("R", 22, 44), **A_("L", 26, 46, 40), **A_("R", 26, 46, 40)}, {"pelvis": (0, .02, -.11)}), kf(24)])
seq("hand_recoil", 18, [kf(0), kf(3, {**A_("R", 40, 20, 100), **G("R", 0, 0, 0), "shoulder.R": (6, 0, 0), "spine": (-4, 0, 6), "head": (-4, 0, 10)}, {}), kf(8, {**A_("R", 30, 28, 110), **G("R", .1, 0, .1), "spine": (-6, 0, 8)}, {}), kf(18)])
seq("press_bar", 24, [kf(0), kf(8, {"spine": (6, 0, 0)}, {"pelvis": (0, -.05, 0)}, {"hand.L": (-.42, 1.05), "hand.R": (-.42, 1.05)}), kf(14, {"spine": (14, 0, 0), "head": (-6, 0, 0), **L("L", 20, 14), **L("R", -12, 22)}, {"pelvis": (0, -.12, -.02)}, {"hand.L": (-.42, 1.0), "hand.R": (-.42, 1.0)}), kf(24)])
seq("press_intercom", 30, [kf(0), kf(8, {**G("R", .8, 1.0, .5)}, {}, {"hand.R": (-.46, 1.38)}), kf(13, {**G("R", .8, 1.0, .5), "spine": (4, 0, 0)}, {"pelvis": (0, -.03, 0)}, {"hand.R": (-.5, 1.38)}), kf(18, {**G("R", .8, 1.0, .5)}, {}, {"hand.R": (-.46, 1.38)}), kf(30)])
seq("open_latch", 36, [kf(0), kf(10, {**G("R", .6, 1.0, .5)}, {}, {"hand.R": (-.5, 1.02)}), kf(18, {**G("R", .9, 0, .7), "spine": (6, 0, -6)}, {}, {"hand.R": (-.5, 1.02)}), kf(26, {**G("R", .9, 0, .7), "spine": (6, 0, -6)}, {"pelvis": (-.06, 0, 0)}, {"hand.R": (-.5, 1.0)}), kf(36)])
seq("throw_object", 24, [kf(0, {**G("R", .9, 0, .5)}), kf(6, {**A_("R", -50, 40, 100), "spine": (-14, 0, 10), "spine2": (-8, 0, 12), **L("L", 14, 10), **L("R", -14, 18), **G("R", .9, 0, .5)}, {"pelvis": (0, .04, 0)}),
                         kf(11, {**A_("R", 100, 20, 20), "spine": (18, 0, -14), "spine2": (10, 0, -12), **L("L", 24, 14), **L("R", -22, 16), **G("R", .1, 0, .1)}, {"pelvis": (0, -.1, -.03)}), kf(17, {**A_("R", 60, 14, 12), "spine": (12, 0, -6)}, {"pelvis": (0, -.06, -.02)}), kf(24)])
seq("fall_prone", 40, [kf(0), kf(5, {"spine": (14, 0, 0), "head": (-10, 0, 0), **A_("L", 90, 10, 10), **A_("R", 90, 10, 10)}, {"root_rot": (14, 0, 0)}),
                       kf(14, {"spine": (14, 0, 0), "head": (-22, 0, 0), **A_("L", 170, 8, 10), **A_("R", 170, 8, 10), **L("L", 30, 40), **L("R", 20, 70)}, {"root_rot": (58, 0, 0), "root": (0, 0, .03)}),
                       kf(24, {"spine": (-3, 0, 0), "head": (-20, 0, 6), **A_("L", 172, 10, 8), **A_("R", 172, 14, 8), **L("L", 4, 4, -15), **L("R", -5, 12, -20), **G("L", .1), **G("R", .2)}, {**LY_LOC, "root": (0, -.03, .15)}),
                       kf(40, {"spine": (-3, 0, 0), "head": (-22, 0, 6), **A_("L", 172, 10, 8), **A_("R", 172, 14, 8), **L("L", 4, 4, -15), **L("R", -5, 12, -20), **G("L", .1), **G("R", .2)}, LY_LOC)])

# ---- environment locomotion
def wade(f):
    u = f / 32; p, l = gait(u, .9)
    for sd, ph in (("L", u), ("R", u + .5)):
        lift = max(0, math.sin(2 * math.pi * ph)); p[f"thigh.{sd}"] = (p[f"thigh.{sd}"][0] + 24 * lift, 0, 0); p[f"shin.{sd}"] = (p[f"shin.{sd}"][0] - 30 * lift, 0, 0)
    p.update({"spine": (6, 0, 0), "head": (-3, 0, 0)}); p.update(A_("L", 12, 50, 28)); p.update(A_("R", 12, 50, 28))
    l = dict(l); l["pelvis"] = (l["pelvis"][0], 0, l["pelvis"][2] - .05); return p, l
make("wade_loop", 32, wade, 2, True); MOVES.append("wade_loop")
def bush_crouch(f):
    u = f / 48; p, l = crouch(.9); s_ = math.sin(2 * math.pi * u); p["head"] = (-6, 0, 22 * math.sin(2 * math.pi * u)); p["neck"] = (0, 0, 10 * s_); p.update(A_("L", 20, 20, 90)); p.update(A_("R", 55, 20, 100)); return p, l
make("bush_crouch_loop", 48, bush_crouch, 4, True); MOVES.append("bush_crouch_loop")
def squeeze(f):
    u = f / 32; s_ = math.sin(2 * math.pi * u); c_ = math.cos(2 * math.pi * u)
    p = mixp(S0(), {"pelvis": (0, 0, 84), "spine": (0, 0, -20), "spine2": (0, 0, -30), "neck": (0, 0, 20), "head": (-4, 0, 30), **A_("L", 70, 8, 40), **A_("R", 70, 8, 40),
                    "thigh.L": (0, 10 + 14 * max(0, c_), 0), "thigh.R": (0, -(10 + 14 * max(0, -c_)), 0), "shin.L": (-6, 0, 0), "shin.R": (-6, 0, 0), "foot.L": (0, 0, 0)})
    return p, {"pelvis": (0, 0, -.02)}
make("squeeze_side_loop", 32, squeeze, 2, True); MOVES.append("squeeze_side_loop")
def crouch_wind(f):
    u = f / 48; p, l = crouch(1.0, 28, 18); s_ = math.sin(2 * math.pi * u * 6); p.update(A_("R", 120, 20, 120)); p.update(A_("L", 40, 14, 80)); p["spine"] = (28 + s_, 0, 4 * s_); p["head"] = (24, 0, 0); l = dict(l); l["pelvis"] = (.02 * s_, .08, -.55); return p, l
make("crouch_hold_wind_loop", 48, crouch_wind, 2, True); MOVES.append("crouch_hold_wind_loop")
seq("step_from_shaft", 36, [kf(0, {"spine": (14, 0, 0), **L("L", 30, 70), **L("R", 6, 20), **G("L", .8), **G("R", .8)}, {"root": (0, -.1, 0)}, {"hand.L": (-.3, 1.0), "hand.R": (-.3, 1.0)}),
                            kf(14, {"spine": (20, 0, 0), "head": (-10, 0, 0), **L("L", 82, 100), **L("R", 8, 24), **G("L", .8), **G("R", .8)}, {"root": (0, -.18, .02)}, {"hand.L": (-.3, 1.0), "hand.R": (-.3, 1.0)}),
                            kf(26, {"spine": (12, 0, 0), **L("L", 30, 40), **L("R", 20, 40)}, {"root": (0, -.5, 0)}), kf(36, {}, {"root": (0, -.6, 0)})])
seq("hatch_climb", 48, [kf(0, {"spine": (0, 0, 0), **A_("L", 160, 14, 20), **A_("R", 160, 14, 20), "head": (-26, 0, 0)}, {"root": (0, -.1, .0)}, {"hand.L": (-.1, 2.2), "hand.R": (-.1, 2.2)}),
                        kf(20, {"head": (-30, 0, 0), **L("L", 70, 100), **L("R", 20, 40), **G("L", .9), **G("R", .9)}, {"root": (0, -.1, .4)}, {"hand.L": (-.12, 2.2), "hand.R": (-.12, 2.2)}),
                        kf(36, {"spine": (8, 0, 0), "head": (-14, 0, 0), **L("L", 20, 20), **L("R", 50, 60)}, {"root": (0, -.1, .9)}, {"hand.L": (-.12, 2.2), "hand.R": (-.12, 2.2)}), kf(48, {"spine": (6, 0, 0)}, {"root": (0, -.1, 1.0)})])

# ---- abandoned (limp) poses
def abandoned_stand(f):
    u = f / 96; s_ = math.sin(2 * math.pi * u); p = {"head": (34 + 2 * s_, 0, 4 * math.sin(2 * math.pi * u * 1 + 1)), "neck": (14, 0, 0), "spine": (14, 0, 0), "spine2": (12 + s_, 0, 0),
        "shoulder.L": (-10, 0, 0), "shoulder.R": (-10, 0, 0), **A_("L", 6 + 2 * s_, 3, 8), **A_("R", 4 - 2 * s_, 3, 8), **G("L", .1), **G("R", .1), **L("L", 4, 8), **L("R", 6, 6), "pelvis": (0, 1.4 * s_, 0)}
    return mixp(S0(), p), {"pelvis": (.006 * s_, 0, -.04 + .004 * s_)}
make("abandoned_stand_loop", 96, abandoned_stand, 8, True); MOVES.append("abandoned_stand_loop")
def abandoned_sit(f):
    u = f / 96; s_ = math.sin(2 * math.pi * u); p = seated(s_ * .6, 18); p.update({"head": (38, 0, 6 * math.sin(2 * math.pi * u)), "neck": (12, 0, 0), "spine": (22, 0, 0), "spine2": (22 + s_, 0, 0), "shoulder.L": (-10, 0, 0), "shoulder.R": (-10, 0, 0),
        **A_("L", 4, 6, 14), **A_("R", 4, 6, 14), **G("L", .1), **G("R", .1)}); return mixp(S0(), p), {"pelvis": (0, .1, -.46)}
make("abandoned_sit_loop", 96, abandoned_sit, 8, True); MOVES.append("abandoned_sit_loop")
