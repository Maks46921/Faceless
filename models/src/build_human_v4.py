"""Builds models/human_noir_v4.glb: v3 body + sculpted face + 11 face shape keys + 24-bone rig + 19 animations.
Run: D:\Cosmoteer\blender.exe -b -P D:\Faceless\models\src\build_human_v4.py   (parts: build_human_v4_head.py, build_human_v4_rig.py)"""
import os
_g = globals()
exec(compile(open("D:/Faceless/models/src/build_human_v4_head.py", encoding="utf-8").read(), "v4_head", "exec"), _g)
exec(compile(open("D:/Faceless/models/src/build_human_v4_rig.py", encoding="utf-8").read(), "v4_rig", "exec"), _g)
