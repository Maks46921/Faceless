#!/bin/bash
cd D:/Faceless/models/src
for p in $(tr -d "" < presets_list.txt); do
  PRESET=$p LOD=near "D:/Cosmoteer/blender.exe" -b -P build_human_preset.py 2>&1 | grep -E "TRIS|Traceback|Error" | sed "s/^/$p near: /" | cut -c1-110
  PRESET=$p LOD=far "D:/Cosmoteer/blender.exe" -b -P build_human_preset.py 2>&1 | grep -E "TRIS|Traceback|Error" | sed "s/^/$p far: /" | cut -c1-110
done
echo ALLDONE
