"""Flashlight item (hand + ground) -> models/movement/basement/"""
_src = open("D:/Faceless/models/src/build_items.py", encoding="utf-8").read()
exec(_src[:_src.index("# ---------------- knife (kitchen)")])
_exp = export
def export(name, objs=None, anims=False, out_dir=None): return _exp(name, objs, anims, "D:/Faceless/models/movement/basement")
def flash():
    mat("flashlight_lens", (.5, .5, .4), .1, 0.0, emit=(1, .95, .7), emit_strength=3); P = []
    P.append(cyl(.016, .13, MATS["steel_dark"], loc=(-.03, 0, 0), seg=10, rot=(0, math.pi / 2, 0), name="body")); P.append(cyl(.026, .06, MATS["steel_dark"], loc=(.065, 0, 0), seg=10, rot=(0, math.pi / 2, 0), name="head"))
    P.append(cyl(.022, .004, MATS["flashlight_lens"], loc=(.097, 0, 0), seg=10, rot=(0, math.pi / 2, 0), name="lens")); P.append(box((.016, .01, .008), MATS["rubber"], loc=(-.02, 0, .018), bev=0, name="switch"))
    P.append(cyl(.017, .012, MATS["rubber"], loc=(-.1, 0, 0), seg=10, rot=(0, math.pi / 2, 0), name="cap")); return P
build_item("flashlight", flash, ground_rot=(math.pi / 2, 0, 0), ground_yaw=.4)
