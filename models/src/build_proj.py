"""Projectile items for glass breaking: brick and bottle (hand + ground variants) -> models/movement/items/"""
_src = open("D:/Faceless/models/src/build_items.py", encoding="utf-8").read()
exec(_src[:_src.index("# ---------------- knife (kitchen)")])
import os
os.makedirs("D:/Faceless/models/movement/items", exist_ok=True)
_exp = export
def export(name, objs=None, anims=False, out_dir=None): return _exp(name, objs, anims, "D:/Faceless/models/movement/items")
def brick():
    mat("brick_item", (.3, .12, .08), .95); P = [box((.215, .065, .102), MATS["brick_item"], loc=(0, 0, 0), bev=.004, name="brick")]
    for k in range(2): P.append(box((.045, .067, .02), MATS["brick_item"], loc=(-.03 + k * .08, 0, .052), bev=0, name="hollow"))
    return P
def bottle():
    mat("bottle_glass", (.08, .2, .1), .12)
    return [lathe([(0, -.11), (.036, -.11), (.038, -.09), (.038, .03), (.03, .06), (.016, .08), (.014, .11), (.017, .115), (.017, .12), (0, .12)], MATS["bottle_glass"], loc=(0, 0, 0), seg=12, rot=(0, math.pi / 2, 0), name="bottle")]
build_item("brick", brick, ground_rot=(0, 0, 0), ground_yaw=.5)
build_item("bottle", bottle, ground_rot=(math.pi / 2, 0, 0), ground_yaw=-.3)
