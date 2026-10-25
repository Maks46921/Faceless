#!/bin/bash
# rebuild every non-human glb (collider nodes -colonly / -convcolonly); human presets are unaffected
cd D:/Faceless/models/src
B="D:/Cosmoteer/blender.exe -b -P"
for s in build_props_a build_props_b build_p2 build_p3 build_items build_items2 build_hatch_decals build_canopy_panel build_flash build_proj build_furniture_v2 build_spirit; do
  [ -f $s.py ] && { echo "== $s"; $B $s.py 2>&1 | grep -E "Traceback|Error" | head -3; }
done
for s in build_buildings build_vehicles build_animals; do echo "== $s"; $B $s.py 2>&1 | grep -E "Traceback|Error" | head -3; done
for s in build_move_a build_move_b build_move_c build_move_d; do echo "== $s"; $B $s.py 2>&1 | grep -E "Traceback|Error" | head -3; done
echo ALLDONE
