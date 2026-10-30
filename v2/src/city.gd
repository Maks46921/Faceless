class_name City
extends Node2D
## Район в разрезе. Каждое дело — свой город: ряд домов вдоль улицы в случайном порядке, высота,
## ширина, материал и планировки тоже случайны. Между домами дворы, сквер, гаражи и узкие переулки;
## соседние дома связаны застеклёнными мостиками, подвальными ходами и лестницами между крышами.
## В домах вентшахты и лифты. Под землёй подвалы, верхний коллектор с решётками, нижний дренажный
## тоннель с водой и станция метро. Строит тайлы, фасады, предметы, свет, двери и граф переходов.

var rng := RandomNumberGenerator.new()
var width := 0                  # в тайлах
var top_row := 0                # выше этого ряда камера не поднимается
var buildings: Array = []       # словари домов
var gaps: Array = []            # промежутки между домами: {kind, c0, c1, name}
var rooms: Array = []
var areas := {}                 # id -> {id, inside, bid, f, y, x0, x1}
var portals: Array = []         # переходы
var climbs: Array = []          # трубы и лестницы снаружи: {x, y0, y1}
var lamps: Array = []           # {pos, r, on, outer, bid, node, light, kind}
var doors: Array = []
var objs: Array = []            # всё, с чем можно взаимодействовать
var places := {}                # имя места -> {area, x, name}
var cams: Array = []
var street_x := []              # x фонарей
var steams: Array = []          # струи пара в коллекторе: {x, y, node, t, on}
var rats: Array = []            # крысы: {node, x0, x1, v}
var metro_c0 := 0
var metro_c1 := 0
var coll_c0 := 0
var coll_c1 := 0

var tm_lane: TileMapLayer
var tm_back: TileMapLayer
var tm_inner: TileMapLayer
var tm_common: TileMapLayer
var furn: Node2D
var fprops: Node2D
var sprops: Node2D
var front: Node2D
var lights_in: Node2D
var lights_out: Node2D
var facades: Node2D
var people: Node2D
var water: WaterLayer

const C_ROW := K.GY + 11        # пол верхнего коллектора
const M_ROW := K.GY + 19        # пол платформы метро
const D_ROW := K.GY + 25        # пол нижнего тоннеля


func _layer(nm: String, vis: int, z: int) -> TileMapLayer:
	var t := TileMapLayer.new()
	t.scale = Vector2(1.0 / K.PX, 1.0 / K.PX)
	t.name = nm
	t.tile_set = Res.tileset
	t.visibility_layer = vis
	t.z_index = z
	add_child(t)
	return t


func _node(nm: String, vis: int, z: int) -> Node2D:
	var n := Node2D.new()
	n.name = nm
	n.visibility_layer = vis
	n.z_index = z
	add_child(n)
	return n


func build(seed_v: int) -> void:
	rng.seed = seed_v
	visibility_layer = K.V_ALL
	tm_lane = _layer("lane", K.V_OUTER, K.Z_BACK)
	tm_back = _layer("back", K.V_INNER, K.Z_BACK)
	furn = _node("furn", K.V_INNER, K.Z_FURN)
	tm_inner = _layer("inner", K.V_INNER, K.Z_SOLID)
	tm_common = _layer("common", K.V_OUTER, K.Z_SOLID + 1)
	facades = _node("facades", K.V_OUTER, K.Z_FACADE)
	fprops = _node("fprops", K.V_OUTER, K.Z_FACADE_PROPS)
	sprops = _node("sprops", K.V_OUTER, K.Z_FACADE_PROPS + 2)
	people = _node("people", K.V_ALL, 0)
	front = _node("front", K.V_OUTER, K.Z_FRONT)
	lights_in = _node("lights_in", K.V_LIN, 0)
	lights_out = _node("lights_out", K.V_LOUT, 0)
	_plan()
	_ground()
	for b in buildings:
		_building(b)
	for g in gaps:
		_gap(g)
	_links()
	_underground()
	_street()
	_areas_and_portals()
	_unwall_spots()


func blocked(x: float, y: float) -> bool:
	## Клетка на уровне груди/головы стоящего внутри человека — стена (не решётка и не платформа).
	for dy in [-10.0, -26.0]:
		var c := Vector2i(int(floor(x / K.T)), int(floor((y + dy) / K.T)))
		for tm in [tm_common, tm_inner]:
			if tm.get_cell_source_id(c) == -1:
				continue
			if tm.get_cell_alternative_tile(c) in [Res.ALT_PLATFORM, Res.ALT_GRATE]:
				continue
			return true
	return false


func unwall(x: float, y: float, mid: float) -> float:
	## Сдвинуть точку из стены к середине комнаты (шагами по полклетки).
	var d := signf(mid - x) if mid != x else 1.0
	var nx := x
	for i in 12:
		if not blocked(nx, y):
			return nx
		nx += d * K.T * 0.5
	return x


func _unwall_spots() -> void:
	## 1.7: точки расписаний (диван, плита, стул) не должны попадать в стену.
	for rm in rooms:
		var mid := (float(rm["x0"]) + float(rm["x1"])) / 2.0
		for sp in rm["spots"]:
			sp["x"] = unwall(float(sp["x"]), float(rm["y"]), mid)
		if rm.has("bed_x"):
			rm["bed_x"] = unwall(float(rm["bed_x"]), float(rm["y"]), mid)


func ri(a: int, b: int) -> int:
	return rng.randi_range(a, b)


func pick(arr: Array):
	return arr[rng.randi() % arr.size()]


func shuffled(arr: Array) -> Array:
	## Перемешать по сиду дела (встроенный shuffle берёт общий генератор и ломает повторяемость).
	var a := arr.duplicate()
	for i in range(a.size() - 1, 0, -1):
		var j := rng.randi_range(0, i)
		var t = a[i]
		a[i] = a[j]
		a[j] = t
	return a


# ======================= план =======================

func _plan() -> void:
	## Случайный ряд домов и промежутков. Обязательны: два офиса («Гранит» с задворками справа и НИИ),
	## «Универсам», вестибюль метро, четыре-пять жилых домов (один с кафе, один с аптекой внизу).
	var mats := ["panel", "brick", "sbrick", "stucco"]
	var specs: Array = [
		{"kind": "res", "w": ri(34, 38), "n": ri(12, 16), "mat": pick(["panel", "panel", "brick"]), "base": "res"},
		{"kind": "res", "w": ri(34, 38), "n": ri(6, 8), "mat": "stucco", "base": "cafe"},
		{"kind": "res", "w": ri(32, 36), "n": ri(9, 12), "mat": pick(["brick", "sbrick"]), "base": "pharmacy"},
		{"kind": "res", "w": ri(32, 36), "n": ri(9, 14), "mat": pick(mats), "base": "res"},
		{"kind": "office", "w": ri(28, 32), "n": ri(10, 14), "mat": "granite", "base": "lobby", "name": "Гранит"},
		{"kind": "office", "w": ri(26, 30), "n": ri(8, 11), "mat": "brick", "base": "lobby", "name": "НИИ"},
		{"kind": "store", "w": ri(24, 28), "n": 2, "mat": "conc", "base": "store", "name": "Универсам"},
		{"kind": "metro", "w": 12, "n": 1, "mat": "conc", "base": "metro"},
	]
	if rng.randf() < 0.5:
		specs.append({"kind": "res", "w": ri(28, 30), "n": 5, "mat": pick(["panel", "brick"]), "base": "res"})
	specs = shuffled(specs)
	# «Гранит» не последним: справа от него задворки
	var gi := -1
	for i in specs.size():
		if specs[i].get("name", "") == "Гранит":
			gi = i
	if gi == specs.size() - 1:
		var t = specs[gi]
		specs[gi] = specs[gi - 1]
		specs[gi - 1] = t
		gi -= 1
	# промежутки между домами
	var slots: Array = []
	for i in specs.size() - 1:
		slots.append(i)
	slots.erase(gi)
	slots = shuffled(slots)
	var named := [["yard", ri(9, 11), "Двор"], ["square", ri(13, 15), "Сквер"], ["garages", ri(10, 12), "Гаражи"], ["yard", ri(8, 9), "Площадка"]]
	var gap_at := {}
	gap_at[gi] = ["backlane", ri(4, 5), "Задворки"]
	for i in named.size():
		gap_at[slots[i]] = named[i]
	var c := 3
	var bid := 0
	for i in specs.size():
		var s: Dictionary = specs[i]
		var b := {"id": bid, "kind": s["kind"], "x0": c, "w": int(s["w"]), "n": int(s["n"]), "mat": s["mat"], "base": s["base"],
			"name": s.get("name", ""), "basement": s["kind"] in ["res", "office"], "floors": {}, "rooms": [],
			"bridge_l": [], "bridge_r": [], "lift": false}
		b["roof_r"] = K.GY - K.FH * int(b["n"])
		b["px0"] = c * K.T
		b["px1"] = (c + int(s["w"])) * K.T
		b["lift"] = (s["kind"] == "res" and int(s["n"]) >= 9) or (s["kind"] == "office" and int(s["n"]) >= 9)
		b["lift_broken"] = b["lift"] and rng.randf() < 0.3
		buildings.append(b)
		bid += 1
		c += int(s["w"])
		if i < specs.size() - 1:
			var g: Array = gap_at.get(i, ["lane", pick([0, 0, 1, 2, 2, 3]), ""])
			if int(g[1]) > 0:
				gaps.append({"kind": g[0], "c0": c, "c1": c + int(g[1]) - 1, "name": g[2]})
			c += int(g[1])
	width = c + 3
	var top := K.GY
	for b in buildings:
		top = mini(top, int(b["roof_r"]))
	top_row = maxi(0, top - 12)
	# мостики и проходы между соседними домами
	for i in buildings.size() - 1:
		var a: Dictionary = buildings[i]
		var b2: Dictionary = buildings[i + 1]
		var gw := int(b2["x0"]) - int(a["x0"]) - int(a["w"])
		if gw > 4 or not (a["kind"] in ["res", "office"]) or not (b2["kind"] in ["res", "office"]):
			continue
		var top_f := mini(int(a["n"]), int(b2["n"])) - 1
		if top_f < 2:
			continue
		var fl := range(2, top_f)
		fl = shuffled(fl)
		var k := 1 + (1 if top_f >= 9 and rng.randf() < 0.6 else 0)
		for j in mini(k, fl.size()):
			(a["bridge_r"] as Array).append(fl[j])
			(b2["bridge_l"] as Array).append(fl[j])
	# коллектор и метро
	coll_c0 = 3
	coll_c1 = width - 4
	var mb: Dictionary = _first("metro")
	metro_c0 = maxi(coll_c0 + 2, int(mb["x0"]) - 14)
	metro_c1 = mini(coll_c1 - 2, int(mb["x0"]) + int(mb["w"]) + 14)


func _first(kind: String) -> Dictionary:
	for b in buildings:
		if b["kind"] == kind:
			return b
	return {}


func b_named(nm: String) -> Dictionary:
	for b in buildings:
		if b["name"] == nm:
			return b
	return {}


# ======================= тайлы =======================

func setc(tm: TileMapLayer, c: int, r: int, nm: String, alt: int) -> void:
	if not Res.tiles.has(nm):
		push_error("нет тайла " + nm)
		return
	tm.set_cell(Vector2i(c, r), 0, Res.tiles[nm], alt)


func _ground() -> void:
	for c in range(0, width):
		setc(tm_common, c, K.GY, "sidewalk", Res.ALT_COMMON)
		for r in range(K.GY + 1, K.ROWS):
			var nm := "earth" if r < K.GY + 12 else "rock"
			if r >= K.GY + 12 and (c * 7 + r * 3) % 11 == 0:
				nm = "earth"
			setc(tm_common, c, r, nm, Res.ALT_COMMON)
	# края мира: глухие стены
	for r in range(top_row, K.GY):
		setc(tm_common, 0, r, "wall_conc", Res.ALT_COMMON)
		setc(tm_common, width - 1, r, "wall_conc", Res.ALT_COMMON)


func carve(c0: int, c1: int, r0: int, r1: int) -> void:
	for c in range(c0, c1 + 1):
		for r in range(r0, r1 + 1):
			tm_common.erase_cell(Vector2i(c, r))


# ======================= дома =======================

const WALLPAPERS := ["wp_flower", "wp_stripe", "wp_rhomb", "wp_blue", "wp_plain", "wp_green", "wp_check", "wp_damask", "wp_ochre"]

## Хозяева квартир: обои, мебель комнаты, спальни, стен, прихожей и кухни.
const THEMES := {
	"old": {"wp": ["wp_flower", "wp_damask", "wp_rhomb"], "living": ["sideboard", "sofa", "armchair", "tv"],
		"wall": ["wallrug", "clock", "portrait_frame", "calendar"], "bed": ["bed", "dresser", "sewing"],
		"hall": ["coatrack", "shoerack", "mirror"], "kitchen": ["radio", "gasheater"]},
	"family": {"wp": ["wp_blue", "wp_check", "wp_green"], "living": ["sofa", "tv", "shelf", "plant"],
		"wall": ["picture", "calendar", "clock"], "bed": ["bed", "crib", "toyhorse"],
		"hall": ["coatrack", "shoerack", "bicycle"], "kitchen": ["washer", "radio"], "kids": true},
	"student": {"wp": ["wp_plain", "wp_stripe", "wp_ochre"], "living": ["sofa", "homedesk", "bookshelf", "guitar"],
		"wall": ["poster", "poster", "calendar"], "bed": ["bed", "stool"], "hall": ["bicycle", "coatrack"], "kitchen": ["radio"]},
	"intel": {"wp": ["wp_green", "wp_damask", "wp_stripe"], "living": ["piano", "bookshelf", "armchair", "floorlamp", "chesstable"],
		"wall": ["picture", "portrait_frame", "clock"], "bed": ["bed", "bookshelf", "homedesk"], "hall": ["coatrack", "mirror"], "kitchen": ["gasheater"]},
	"worker": {"wp": ["wp_plain", "wp_check", "wp_ochre"], "living": ["sofa", "tv", "armchair", "aquarium"],
		"wall": ["calendar", "picture", "wallrug"], "bed": ["bed", "wardrobe", "rods"], "hall": ["coatrack", "shoerack"], "kitchen": ["washer", "gasheater"]},
	"lonely": {"wp": ["wp_plain", "wp_rhomb", "wp_flower"], "living": ["sofa", "tv", "plant", "ironboard"],
		"wall": ["clock", "mirror", "picture"], "bed": ["bed", "dresser"], "hall": ["coatrack"], "kitchen": ["radio"]},
}


func _building(b: Dictionary) -> void:
	var x0: int = b["x0"]
	var w: int = b["w"]
	var n: int = b["n"]
	var rr: int = b["roof_r"]
	var mat: String = b["mat"]
	var cutw := "wall_" + ("conc" if mat == "panel" else mat)
	if mat == "panel":
		cutw = "wall_panel"
	# крыша
	for c in range(x0, x0 + w):
		setc(tm_common, c, rr, "roof_tin" if mat == "stucco" else "roof_tar", Res.ALT_COMMON)
	setc(tm_common, x0, rr - 1, "parapet", Res.ALT_COMMON)
	setc(tm_common, x0 + w - 1, rr - 1, "parapet", Res.ALT_COMMON)
	# стены в разрезе
	for r in range(rr + 1, K.GY):
		setc(tm_inner, x0, r, cutw, Res.ALT_INTERIOR)
		setc(tm_inner, x0 + w - 1, r, cutw, Res.ALT_INTERIOR)
	# ядро: лестничная клетка (4 колонки) и лифт (2 колонки) — около середины, со сдвигом
	var core_w := 4 + (2 if b["lift"] else 0)
	var sw0 := x0 + (w - core_w) / 2 + ri(-2, 2)
	if b["kind"] == "metro":
		sw0 = x0 + 2
	if b["kind"] == "store":
		sw0 = x0 + w - 6
	b["sw0"] = sw0
	b["sw1"] = sw0 + 3
	b["stair_x"] = float((sw0 + 2) * K.T)
	if b["lift"]:
		b["lw0"] = sw0 + 4
		b["lw1"] = sw0 + 5
		b["lift_x"] = float((sw0 + 5) * K.T)
	b["core1"] = sw0 + core_w - 1
	# вентшахта у наружной стены
	if b["kind"] in ["res", "office"]:
		b["vent_c"] = x0 + 1 if rng.randf() < 0.5 else x0 + w - 2
	for f in range(0, n):
		_floor(b, f)
	if b["basement"]:
		_basement(b)
	if b.has("vent_c"):
		_vent_shaft(b)
	_facade(b)
	_roof_props(b)


func slab_row(f: int) -> int:
	return K.GY - K.FH * f


func _add_room(b: Dictionary, f: int, c0: int, c1: int, kind: String, wp: String, apt: int = 0, staff: bool = false, fill: bool = true) -> Dictionary:
	var rm := {"id": rooms.size(), "bid": b["id"], "f": f, "c0": c0, "c1": c1, "kind": kind, "wp": wp, "apt": apt,
		"staff": staff, "x0": float(c0 * K.T), "x1": float((c1 + 1) * K.T), "y": K.floor_y(f), "lamp": null, "spots": []}
	rooms.append(rm)
	b["rooms"].append(rm["id"])
	if not fill:
		return rm
	# фон
	var r1 := slab_row(f) - 1 if f >= 0 else K.GY + 5
	var r0 := r1 - 3
	for c in range(c0, c1 + 1):
		for r in range(r0, r1 + 1):
			var t := wp
			if (wp.begins_with("wp_") or wp == "hall") and r == r1:
				t = wp + "_low"
			elif wp == "pod":
				t = "pod_high" if r == r0 else ("pod_mid" if r == r0 + 1 else "pod_low")
			elif wp == "office" and r == r1:
				t = "office_low"
			setc(tm_back, c, r, t, Res.ALT_NONE)
	return rm


func _wall(b: Dictionary, f: int, c: int, kind: String, lock: String = "", sprite: String = "") -> Dictionary:
	## Перегородка: верхний ряд стена, ниже проём; дверь — предмет со столкновением.
	var r1 := slab_row(f) - 1 if f >= 0 else K.GY + 5
	var r0 := r1 - 3
	setc(tm_inner, c, r0, "cutwall", Res.ALT_INTERIOR)
	if kind == "solid":
		for r in range(r0 + 1, r1 + 1):
			setc(tm_inner, c, r, "cutwall", Res.ALT_INTERIOR)
		return {}
	if kind == "vent":     # стена с лазом у пола: человек не пройдёт
		for r in range(r0 + 1, r1):
			setc(tm_inner, c, r, "cutwall", Res.ALT_INTERIOR)
		setc(tm_inner, c, r1, "vent", Res.ALT_GRATE)
		return {}
	if kind == "door" or kind == "metal":
		return _door(b, f, float(c * K.T + K.T / 2), K.floor_y(f), sprite if sprite != "" else ("door" if kind == "door" else "door_metal"), lock)
	return {}


func _door(b: Dictionary, f: int, x: float, y: float, sprite: String, lock: String) -> Dictionary:
	var nd := Node2D.new()
	nd.position = Vector2(x, y)
	nd.visibility_layer = K.V_INNER
	var sp := Res.prop_sprite(sprite, 0)
	sp.visibility_layer = K.V_ALL
	nd.add_child(sp)
	var body := StaticBody2D.new()
	body.collision_layer = K.L_DOOR
	body.collision_mask = 0
	var sh := CollisionShape2D.new()
	var rs := RectangleShape2D.new()
	rs.size = Vector2(6, 46)
	sh.shape = rs
	sh.position = Vector2(0, -24)
	body.add_child(sh)
	nd.add_child(body)
	furn.add_child(nd)
	var d := {"kind": "door", "node": nd, "sprite": sp, "body": body, "shape": sh, "open": false, "locked": lock != "",
		"key": lock, "x": x, "y": y, "bid": b.get("id", -1), "f": f, "metal": sprite != "door", "inside": true, "t_close": 0.0,
		"grate": sprite == "grate_door"}
	doors.append(d)
	objs.append(d)
	return d


func set_door(d: Dictionary, open: bool) -> void:
	d["open"] = open
	(d["sprite"] as Sprite2D).frame = 1 if open else 0
	(d["shape"] as CollisionShape2D).set_deferred("disabled", open)


func _floor(b: Dictionary, f: int) -> void:
	var x0: int = b["x0"]
	var w: int = b["w"]
	var sw0: int = b["sw0"]
	var sw1: int = b["sw1"]
	var core1: int = b["core1"]
	var sr := slab_row(f)
	var kind: String = b["kind"]
	# перекрытие (пол этажа f ≥ 1)
	if f >= 1:
		var st := "slab_concrete"
		match kind:
			"res": st = "slab_parquet" if f % 2 == 0 else "slab_lino"
			"office": st = "slab_office"
			"store": st = "slab_tile"
		for c in range(x0 + 1, x0 + w - 1):
			setc(tm_inner, c, sr, st, Res.ALT_INTERIOR)
		if kind == "res":
			for c in range(sw0, core1 + 1):
				setc(tm_inner, c, sr, "slab_concrete", Res.ALT_INTERIOR)
	var ground := f == 0
	var base: String = b["base"]
	# лестничная клетка
	var wpst := "pod" if kind in ["res"] else ("office" if kind == "office" else "shop")
	if kind == "metro":
		wpst = "marble"
	var stair := _add_room(b, f, sw0, sw1, "stair", wpst)
	_stairs_sprite(b, f)
	if b["lift"]:
		_lift_floor(b, f)
	if kind == "res" and ground:
		_furn("mailboxes", Vector2((sw0 + 1) * K.T + 4, K.floor_y(0) - 22))
	if kind == "metro":
		_metro_floor(b, stair)
		return
	var lw := sw0 - 1        # стена слева от ядра
	var rw := core1 + 1
	var left := [x0 + 1, lw - 1]
	var right := [rw + 1, x0 + w - 2]
	var br_l: bool = f in b["bridge_l"]
	var br_r: bool = f in b["bridge_r"]
	if kind == "res":
		if ground and base != "res":
			# левое крыло — заведение, правое — квартира
			_shop(b, f, left[0], left[1], base)
			_wall(b, f, lw, "door", "")
			_apartment(b, f, right[0], right[1], 2 * f + 2, false)
			_wall(b, f, rw, "door", "apt%d_%d" % [b["id"], 2 * f + 2])
		else:
			if br_l:
				_gallery(b, f, left[0], left[1])
				_wall(b, f, lw, "doorway")
			else:
				_apartment(b, f, left[0], left[1], 2 * f + 1, true)
				_wall(b, f, lw, "door", "apt%d_%d" % [b["id"], 2 * f + 1])
			if br_r:
				_gallery(b, f, right[0], right[1])
				_wall(b, f, rw, "doorway")
			else:
				_apartment(b, f, right[0], right[1], 2 * f + 2, false)
				_wall(b, f, rw, "door", "apt%d_%d" % [b["id"], 2 * f + 2])
	elif kind == "office":
		if ground:
			var lob := _add_room(b, f, left[0], left[1], "lobby", "office")
			_furn("guarddesk", Vector2((left[0] + 3) * K.T, K.floor_y(0)))
			_furn("turnstile", Vector2((left[1] - 1) * K.T, K.floor_y(0)))
			_furn("plant", Vector2((left[0] + 7) * K.T, K.floor_y(0)))
			lob["spots"].append({"x": (left[0] + 3) * K.T + 4, "kind": "guard"})
			_wall(b, f, lw, "doorway")
			var sec := _add_room(b, f, right[0], right[1], "security", "office", 0, true)
			var con := _furn("console", Vector2((right[0] + 3) * K.T, K.floor_y(0)))
			_obj({"kind": "console", "node": con, "x": (right[0] + 3) * K.T, "y": K.floor_y(0), "bid": b["id"], "f": 0, "inside": true})
			sec["spots"].append({"x": (right[0] + 2) * K.T, "kind": "sit"})
			_furn("chair", Vector2((right[0] + 2) * K.T, K.floor_y(0)))
			_furn("filing", Vector2((right[1] - 2) * K.T, K.floor_y(0)))
			_furn("calendar", Vector2((right[0] + 6) * K.T, K.floor_y(0) - 30))
			_wall(b, f, rw, "metal", "sec%d" % b["id"])
			_fusebox(b, f, (right[1]) * K.T)
		else:
			var opts := ["open", "open", "open", "meeting", "archive", "boss", "smoke"]
			for side in [left, right]:
				var kind2: String = "open" if f == 2 or (side == left and br_l) or (side == right and br_r) else pick(opts)
				_office_room(b, f, int(side[0]), int(side[1]), kind2)
			_wall(b, f, lw, "doorway")
			_wall(b, f, rw, "door", "")
	elif kind == "store":
		if ground:
			var h := _add_room(b, f, x0 + 1, lw - 6, "store", "shop")
			var c2 := x0 + 2
			while c2 + 3 < lw - 7:
				_furn("shopshelf", Vector2((c2 + 1) * K.T, K.floor_y(0)))
				h["spots"].append({"x": (c2 + 1) * K.T + 20, "kind": "shop"})
				c2 += 4
			_furn("counter", Vector2((lw - 8) * K.T, K.floor_y(0)))
			_furn("register", Vector2((lw - 8) * K.T, K.floor_y(0) - 20))
			h["spots"].append({"x": (lw - 7) * K.T + 4, "kind": "cashier"})
			_wall(b, f, lw - 5, "door", "")
			var br := _add_room(b, f, lw - 4, lw - 1, "storage", "basement", 0, true)
			_furn("crate", Vector2((lw - 3) * K.T, K.floor_y(0)))
			_movable("bucket", (lw - 2) * K.T, b, f)
			_fusebox(b, f, (lw - 1) * K.T)
			_wall(b, f, lw, "door", "")
			if rw <= x0 + w - 2:
				_add_room(b, f, rw + 1, x0 + w - 2, "storage", "basement", 0, true)
				_wall(b, f, rw, "door", "")
		else:
			var o := _add_room(b, f, x0 + 1, lw - 1, "office", "office", 0, true)
			_furn("desk", Vector2((x0 + 4) * K.T, K.floor_y(f)))
			o["spots"].append({"x": (x0 + 4) * K.T + 12, "kind": "desk"})
			_furn("filing", Vector2((lw - 2) * K.T, K.floor_y(f)))
			_wall(b, f, lw, "door", "")
			if rw <= x0 + w - 2:
				_add_room(b, f, rw + 1, x0 + w - 2, "storage", "basement", 0, true)
				_wall(b, f, rw, "solid")


func _office_room(b: Dictionary, f: int, c0: int, c1: int, kind: String) -> void:
	## Офисный этаж бывает разным: общий зал со столами, переговорная, архив, кабинет начальника, курилка.
	var y := K.floor_y(f)
	match kind:
		"open":
			var o := _add_room(b, f, c0, c1, "office", "office", 0, true)
			var c := c0 + 1
			while c + 2 <= c1:
				_furn("desk", Vector2((c + 1) * K.T, y))
				_furn("chair", Vector2((c + 1) * K.T + 12, y))
				o["spots"].append({"x": (c + 1) * K.T + 12, "kind": "desk"})
				c += 4
			_furn("filing", Vector2(c1 * K.T, y))
			if rng.randf() < 0.6:
				_movable("cooler", c0 * K.T + 6, b, f)
			_furn("calendar", Vector2((c0 + 2) * K.T, y - 34))
		"meeting":
			var o2 := _add_room(b, f, c0, c1, "meeting", "wp_stripe", 0, true)
			var mid := (c0 + c1 + 1) * K.T / 2.0
			_furn("table", Vector2(mid, y))
			for dx in [-28, -12, 12, 28]:
				_movable("chair", mid + dx, b, f)
			o2["spots"].append({"x": mid - 12, "kind": "desk"})
			_furn("picture", Vector2(mid, y - 40))
			_furn("plant", Vector2(c1 * K.T, y))
		"archive":
			var o3 := _add_room(b, f, c0, c1, "archive", "office", 0, true)
			var c3 := c0 + 1
			while c3 <= c1:
				_furn("filing", Vector2(c3 * K.T + 8, y))
				c3 += 2
			o3["spots"].append({"x": (c0 + 1) * K.T, "kind": "work"})
		"boss":
			var o4 := _add_room(b, f, c0, c1, "boss", "wp_damask", 0, true)
			var mid4 := (c0 + c1 + 1) * K.T / 2.0
			_furn("homedesk", Vector2(mid4, y))
			_furn("armchair", Vector2(mid4 + 22, y))
			_furn("sofa", Vector2(c0 * K.T + 26, y))
			_furn("bookshelf", Vector2(c1 * K.T, y))
			_furn("portrait_frame", Vector2(mid4, y - 40))
			_furn("plant", Vector2(c0 * K.T + 56, y))
			o4["spots"].append({"x": mid4 + 22, "kind": "desk"})
		"smoke":
			var o5 := _add_room(b, f, c0, c1, "smoke", "office", 0, true)
			_furn("stool", Vector2((c0 + 2) * K.T, y))
			_furn("stool", Vector2((c0 + 4) * K.T, y))
			_movable("urn", (c0 + 3) * K.T, b, f)
			_furn("poster", Vector2((c0 + 6) * K.T, y - 34))
			o5["spots"].append({"x": (c0 + 3) * K.T, "kind": "sit"})


func _gallery(b: Dictionary, f: int, c0: int, c1: int) -> void:
	## Общий коридор у мостика в соседний дом: жильцы ходят здесь, квартиры на этом крыле нет.
	var y := K.floor_y(f)
	var g := _add_room(b, f, c0, c1, "corridor", "pod")
	_furn("radiator", Vector2((c0 + 2) * K.T, y - 10))
	_furn("plant", Vector2((c0 + c1) * K.T / 2.0, y))
	_furn("arrow_sign", Vector2((c0 + c1) * K.T / 2.0 + 30, y - 38))
	g["spots"].append({"x": (c0 + c1) * K.T / 2.0, "kind": "wait"})


func _stairs_sprite(b: Dictionary, f: int) -> void:
	var x := float(int(b["sw0"]) * K.T + 32)
	if f < int(b["n"]) - 1:
		_furn("stairs", Vector2(x, K.floor_y(f)))
	# лампочка на клетке
	_lamp_in(b, f, Vector2(x, K.floor_y(f) - 58), 56.0, Color(1.0, 0.9, 0.7))


func _lift_floor(b: Dictionary, f: int) -> void:
	## Шахта лифта: тёмный фон, двери на каждом этаже. Сломанный — с табличкой.
	var lw0: int = b["lw0"]
	var r1 := slab_row(f) - 1
	for c in range(lw0, lw0 + 2):
		for r in range(r1 - 3, r1 + 1):
			setc(tm_back, c, r, "lift_shaft", Res.ALT_NONE)
	var x: float = b["lift_x"]
	var y := K.floor_y(f)
	var dr := _furn("lift_door", Vector2(x, y))
	_furn("lift_panel", Vector2(x - 20, y - 26))
	if not b.has("lift_doors"):
		b["lift_doors"] = {}
	b["lift_doors"][f] = dr
	if b["lift_broken"]:
		_furn("broken_sign", Vector2(x, y - 30))
	var rm := _add_room(b, f, lw0, lw0 + 1, "lift", "lift_shaft", 0, false, false)
	rm["broken"] = b["lift_broken"]


func _vent_shaft(b: Dictionary) -> void:
	## Вентшахта: короб у наружной стены на всю высоту. В перекрытиях — решётки: люди стоят,
	## дух пролетает с этажа на этаж. Сверху — выход на крышу, снизу — в подвал (только для духа).
	var c: int = b["vent_c"]
	var n: int = b["n"]
	for f in range(0, n):
		var r1 := slab_row(f) - 1
		for r in range(r1 - 3, r1 + 1):
			setc(tm_back, c, r, "duct_back", Res.ALT_NONE)
		if f >= 1:
			setc(tm_inner, c, slab_row(f), "vent", Res.ALT_GRATE)
		_furn("vent_grille", Vector2(c * K.T + 8, K.floor_y(f) - 2))
	b["vent_x"] = float(c * K.T + 8)


func _apartment(b: Dictionary, f: int, c0: int, c1: int, apt: int, left: bool) -> void:
	## Квартира: от входа (у лестницы) к наружной стене — прихожая, кухня, ванная, комната, спальня
	## в случайном порядке и разной ширины. Хозяин (тема) решает обои и обстановку.
	var wdt := c1 - c0 + 1
	var theme_k: String = pick(THEMES.keys())
	var th: Dictionary = THEMES[theme_k]
	var plan: Array = ["kitchen", "living"]
	if wdt >= 12:
		plan.append("bath")
	if wdt >= 14:
		plan.append("bedroom")
	plan = shuffled(plan)
	var hall := rng.randf() < 0.7 and wdt >= 11
	if hall:
		plan.push_front("hall")
	# ширины: минимумы, остаток раздаём жилым комнатам
	var mins := {"hall": 2, "kitchen": 4, "living": 5, "bath": 2, "bedroom": 4}
	var ws := []
	var total := plan.size() - 1
	for k in plan:
		ws.append(int(mins[k]))
		total += int(mins[k])
	while total > wdt and plan.size() > 2:
		# не влезло: выкинуть необязательную комнату
		var drop := plan.find("bedroom") if plan.has("bedroom") else (plan.find("bath") if plan.has("bath") else plan.find("hall"))
		if drop < 0:
			break
		total -= int(ws[drop]) + 1
		plan.remove_at(drop)
		ws.remove_at(drop)
	var extra := wdt - total
	var grow := []
	for i in plan.size():
		if plan[i] in ["living", "bedroom", "kitchen"]:
			grow.append(i)
	while extra > 0 and grow.size() > 0:
		var gi: int = grow[rng.randi() % grow.size()]
		if plan[gi] == "kitchen" and int(ws[gi]) >= 6:
			grow.erase(gi)
			continue
		ws[gi] = int(ws[gi]) + 1
		extra -= 1
	if extra > 0:
		ws[0] = int(ws[0]) + extra
	# раскладка от входа: у левой квартиры вход справа (у лестницы), у правой — слева
	var spans := []
	var cur := c1 if left else c0
	for i in plan.size():
		var w2: int = ws[i]
		var a: int
		var z: int
		if left:
			z = cur
			a = cur - w2 + 1
			cur = a - 2
		else:
			a = cur
			z = cur + w2 - 1
			cur = z + 2
		spans.append([a, z])
	var y := K.floor_y(f)
	var living_wp: String = pick(th["wp"])
	for i in plan.size():
		var k: String = plan[i]
		var a2: int = spans[i][0]
		var z2: int = spans[i][1]
		# перегородка после комнаты (в сторону наружной стены)
		if i < plan.size() - 1:
			var wc := a2 - 1 if left else z2 + 1
			var wk := "doorway"
			if k == "bath" or plan[i + 1] == "bath":
				wk = "door"
			elif rng.randf() < 0.15:
				wk = "vent"
			elif plan[i + 1] == "bedroom" and rng.randf() < 0.5:
				wk = "door"
			_wall(b, f, wc, wk, "")
		var wp := ""
		match k:
			"hall": wp = "hall"
			"kitchen": wp = "kitchen" if rng.randf() < 0.7 else "wp_check"
			"bath": wp = "bath"
			"living": wp = living_wp
			"bedroom":
				wp = pick(WALLPAPERS)
				if th.get("kids", false):
					wp = "wp_kids"
		var rm := _add_room(b, f, a2, z2, k, wp, apt)
		rm["theme"] = theme_k
		var x0 := float(a2 * K.T)
		var x1 := float((z2 + 1) * K.T)
		var outer_side := not ((left and i == 0) or (not left and i == 0))
		match k:
			"hall": _furnish_hall(rm, th, x0, x1, y, left, b, f)
			"kitchen": _furnish_kitchen(rm, th, x0, x1, y, left, b, f)
			"bath": _furnish_bath(rm, x0, x1, y)
			"living": _furnish_living(rm, th, x0, x1, y, left, b, f, apt, not plan.has("bedroom"))
			"bedroom": _furnish_bedroom(rm, th, x0, x1, y, left, b, f, apt)
	b["floors"][f] = b["floors"].get(f, [])
	(b["floors"][f] as Array).append(apt)


func _row(items: Array, x0: float, x1: float, y: float, from_hi: bool, gap: float = 3.0) -> Array:
	## Ставит предметы вдоль пола от одного края комнаты. Не влезшее пропускает. Возвращает [[имя, x]].
	var out := []
	var x := x1 - 4.0 if from_hi else x0 + 4.0
	for nm in items:
		var w := Res.prop_size(nm).x
		var cx := x - w / 2.0 if from_hi else x + w / 2.0
		if cx - w / 2.0 < x0 + 2.0 or cx + w / 2.0 > x1 - 2.0:
			continue
		out.append([nm, cx])
		x = (cx - w / 2.0 - gap) if from_hi else (cx + w / 2.0 + gap)
	return out


func _put_row(lst: Array, y: float, b: Dictionary, f: int) -> void:
	for it in lst:
		if it[0] in ["chair", "armchair", "stool", "plant", "floorlamp", "toyhorse", "ironboard"]:
			_movable(it[0], it[1], b, f)
		else:
			_furn(it[0], Vector2(it[1], y))


func _wall_items(items: Array, x0: float, x1: float, y: float, h: float) -> void:
	## Картины, часы, ковры на стене — над мебелью, по высоте h от пола.
	var n := items.size()
	if n == 0:
		return
	var step := (x1 - x0) / float(n + 1)
	for i in n:
		var nm: String = items[i]
		var w := Res.prop_size(nm).x
		if w > (x1 - x0) - 8:
			continue
		var cx := clampf(x0 + step * (i + 1) + rng.randf_range(-6, 6), x0 + w / 2.0 + 2, x1 - w / 2.0 - 2)
		var hh := h
		if nm == "wallrug":
			hh = h - 4
		elif nm in ["clock", "mirror"]:
			hh = h + 4
		_furn(nm, Vector2(cx, y - hh))


func _furnish_hall(rm: Dictionary, th: Dictionary, x0: float, x1: float, y: float, left: bool, b: Dictionary, f: int) -> void:
	var items: Array = th["hall"].duplicate()
	var lst := _row(shuffled(items), x0, x1, y, not left)
	_put_row(lst, y, b, f)


func _furnish_kitchen(rm: Dictionary, th: Dictionary, x0: float, x1: float, y: float, left: bool, b: Dictionary, f: int) -> void:
	## Кухня: плита, мойка, холодильник у стены; стол со стулом посередине; по хозяину — радио, колонка, стиралка.
	var wall_hi := rng.randf() < 0.5
	var row1 := _row(["stove", "sink", "fridge"] if rng.randf() < 0.6 else ["fridge", "stove", "sink"], x0, x1, y, wall_hi)
	_put_row(row1, y, b, f)
	for it in row1:
		if it[0] == "stove":
			rm["spots"].append({"x": it[1], "kind": "stove"})
		if it[0] == "sink":
			_furn("cabinet", Vector2(it[1], y - 34))
	var free0 := x0
	var free1 := x1
	if row1.size() > 0:
		var last: Array = row1[row1.size() - 1]
		var lw := Res.prop_size(last[0]).x
		if wall_hi:
			free1 = float(last[1]) - lw / 2.0 - 4
		else:
			free0 = float(last[1]) + lw / 2.0 + 4
	var mid := (free0 + free1) / 2.0
	if free1 - free0 > 44:
		_furn("table", Vector2(mid, y))
		_movable("chair", mid + 20, b, f)
		if free1 - free0 > 64:
			_movable("stool", mid - 22, b, f)
		rm["spots"].append({"x": mid, "kind": "sit"})
	else:
		_movable("stool", mid, b, f)
		rm["spots"].append({"x": mid, "kind": "sit"})
	for ex in th["kitchen"]:
		if ex == "gasheater":
			_furn("gasheater", Vector2(x0 + (x1 - x0) * rng.randf_range(0.2, 0.8), y - 34))
		elif ex == "radio":
			_furn("radio", Vector2(mid + rng.randf_range(-8, 8), y - 16))
		elif ex == "washer" and free1 - free0 > 70:
			_furn("washer", Vector2(free0 + 12 if wall_hi else free1 - 12, y))
	if rm["spots"].is_empty() or rm["spots"][0]["kind"] != "stove":
		rm["spots"].push_front({"x": mid, "kind": "stove"})


func _furnish_bath(rm: Dictionary, x0: float, x1: float, y: float) -> void:
	var items := ["washbasin", "toilet"]
	if x1 - x0 >= 48:
		items = ["bathtub", "washbasin"] if x1 - x0 < 64 else ["bathtub", "washbasin", "toilet"]
	var lst := _row(items, x0, x1, y, rng.randf() < 0.5, 2.0)
	for it in lst:
		_furn(it[0], Vector2(it[1], y))
	if lst.size() < 2:
		_furn("mirror", Vector2((x0 + x1) / 2.0, y - 40))


func _furnish_living(rm: Dictionary, th: Dictionary, x0: float, x1: float, y: float, left: bool, b: Dictionary, f: int, apt: int, with_bed: bool) -> void:
	## Комната: диван (точка «диван» — первая), остальное по хозяину; шкаф (можно прятать тело).
	var outer := x0 if left else x1
	var dirn := 1.0 if left else -1.0
	# шкаф у наружной стены
	var cx := outer + dirn * 18
	var cl := _furn("closet", Vector2(cx, y))
	_obj({"kind": "closet", "node": cl, "x": cx, "y": y, "bid": b["id"], "f": f, "inside": true, "full": false, "apt": apt})
	_furn("radiator", Vector2(outer + dirn * 44, y - 10))
	var a := x0 + 34.0 if left else x0
	var z := x1 if left else x1 - 34.0
	var items: Array = th["living"].duplicate()
	if with_bed:
		items.insert(1, "bed")
	var lst := _row(items, a, z, y, left)
	var sofa_x := -1.0
	for it in lst:
		if it[0] == "sofa":
			sofa_x = it[1]
		if it[0] == "bed":
			rm["bed_x"] = it[1]
	if sofa_x < 0.0 and lst.size() > 0:
		sofa_x = lst[0][1]
	_put_row(lst, y, b, f)
	rm["spots"].append({"x": sofa_x if sofa_x > 0 else (a + z) / 2.0, "kind": "sofa"})
	for it in lst:
		if it[0] == "armchair":
			rm["spots"].append({"x": it[1], "kind": "sit"})
	if rm.has("bed_x"):
		rm["spots"].append({"x": rm["bed_x"], "kind": "bed"})
	_wall_items(shuffled(th["wall"]).slice(0, 2), a, z, y, 40.0)


func _furnish_bedroom(rm: Dictionary, th: Dictionary, x0: float, x1: float, y: float, left: bool, b: Dictionary, f: int, apt: int) -> void:
	var outer := x0 if left else x1
	var items: Array = th["bed"].duplicate()
	var lst := _row(items, x0, x1, y, not left)
	var bed_x := (x0 + x1) / 2.0
	for it in lst:
		if it[0] == "bed":
			bed_x = it[1]
	_put_row(lst, y, b, f)
	rm["spots"].append({"x": bed_x, "kind": "bed"})
	_furn("radiator", Vector2(outer + (14.0 if left else -14.0), y - 10))
	_wall_items(shuffled(["picture", "clock", "calendar", "mirror", "poster"]).slice(0, 1), x0, x1, y, 40.0)


func _shop(b: Dictionary, f: int, c0: int, c1: int, base: String) -> void:
	var y := K.floor_y(f)
	match base:
		"cafe":
			var kit := _add_room(b, f, c0, c0 + 3, "kitchen_cafe", "kitchen", 0, true)
			_furn("stove", Vector2((c0 + 1) * K.T, y)); _furn("fridge", Vector2((c0 + 3) * K.T, y))
			kit["spots"].append({"x": (c0 + 2) * K.T, "kind": "stove"})
			_fusebox(b, f, (c0) * K.T + 8)
			_wall(b, f, c0 + 4, "door", "")
			var hall := _add_room(b, f, c0 + 5, c1, "cafe", "cafe")
			_furn("counter", Vector2((c0 + 7) * K.T, y))
			_furn("coffeemachine", Vector2((c0 + 6) * K.T + 8, y - 20))
			hall["spots"].append({"x": (c0 + 6) * K.T, "kind": "barista"})
			var c := c0 + 10
			while c + 1 <= c1:
				_furn("cafetable", Vector2(c * K.T, y))
				_movable("chair", c * K.T + 14, b, f)
				hall["spots"].append({"x": c * K.T + 14, "kind": "eat"})
				c += 3
			_furn("picture", Vector2((c0 + 11) * K.T, y - 40))
			_furn("clock", Vector2((c0 + 14) * K.T, y - 44))
			hall["name"] = "Кафе"
		"pharmacy":
			var hall := _add_room(b, f, c0, c1 - 4, "pharmacy", "shop")
			_furn("counter", Vector2((c1 - 6) * K.T, y))
			_furn("shelf", Vector2((c1 - 5) * K.T + 6, y - 22))
			hall["spots"].append({"x": (c1 - 5) * K.T + 4, "kind": "cashier"})
			hall["spots"].append({"x": (c0 + 3) * K.T, "kind": "shop"})
			_furn("plant", Vector2((c0 + 1) * K.T, y))
			_wall(b, f, c1 - 3, "door", "")
			var back := _add_room(b, f, c1 - 2, c1, "storage", "basement", 0, true)
			_furn("shelf", Vector2((c1 - 1) * K.T, y))
			_fusebox(b, f, c1 * K.T + 8)
			hall["name"] = "Аптека"
		_:
			_add_room(b, f, c0, c1, "storage", "basement", 0, true)


func _basement(b: Dictionary) -> void:
	var x0: int = b["x0"]
	var w: int = b["w"]
	carve(x0 + 1, x0 + w - 2, K.GY + 2, K.GY + 5)
	var rm := _add_room(b, -1, x0 + 1, x0 + w - 2, "basement", "basement", 0, true)
	var y := K.floor_y(-1)
	_furn("pipes_big", Vector2((x0 + 5) * K.T, y - 50))
	_furn("pipes_big", Vector2((x0 + w - 8) * K.T, y - 50))
	_furn("boiler", Vector2((x0 + w - 5) * K.T, y))
	_furn("crate", Vector2((x0 + 4) * K.T, y))
	if rng.randf() < 0.6:
		_furn("bicycle", Vector2((x0 + 9) * K.T, y))
	if rng.randf() < 0.5:
		_furn("barrel", Vector2((x0 + w - 9) * K.T, y))
	_furn("valve", Vector2((x0 + w - 7) * K.T, y - 30))
	_fusebox(b, -1, (x0 + 2) * K.T + 8)
	_lamp_in(b, -1, Vector2((x0 + w / 2) * K.T, y - 56), 90.0, Color(1.0, 0.85, 0.6), "bulb")
	var lb := _furn("lockbox", Vector2((x0 + w - 3) * K.T, y))
	_obj({"kind": "lockbox", "node": lb, "x": (x0 + w - 3) * K.T, "y": y, "bid": b["id"], "f": -1, "inside": true, "open": false,
		"keys": ["roof%d" % b["id"], "fire%d" % b["id"]], "what": "ключи от крыши и пожарной лестницы"})
	b["floors"][-1] = []
	# дверь из клетки в подвал (железная, заперта у части домов)
	var c := int(b["sw0"]) - 1
	_wall(b, -1, c, "metal", ("base%d" % b["id"]) if rng.randf() < 0.6 else "")
	_wall(b, -1, int(b["sw1"]) + 1, "doorway")
	_add_room(b, -1, b["sw0"], b["sw1"], "stair", "basement")


func _metro_floor(b: Dictionary, stair: Dictionary) -> void:
	var x0: int = b["x0"]
	var w: int = b["w"]
	stair["kind"] = "metro"
	var hall := _add_room(b, 0, int(b["sw1"]) + 2, x0 + w - 2, "metro", "marble")
	_wall(b, 0, int(b["sw1"]) + 1, "doorway")
	_furn("escalator", Vector2((x0 + w - 4) * K.T, K.floor_y(0) + 0))
	hall["spots"].append({"x": (x0 + w - 6) * K.T, "kind": "wait"})


func _fusebox(b: Dictionary, f: int, x: float) -> void:
	var y := K.floor_y(f)
	var n := _furn("fusebox", Vector2(x, y - 26))
	_obj({"kind": "fusebox", "node": n, "x": x, "y": y, "bid": b["id"], "f": f, "inside": true, "off_t": 0.0})


func _movable(nm: String, x: float, b: Dictionary, f: int) -> void:
	var y := K.floor_y(f)
	var n := _furn(nm, Vector2(x, y))
	_obj({"kind": "movable", "what": nm, "node": n, "x": x, "y": y, "bid": b["id"], "f": f, "inside": true, "fallen": false})


func _obj(d: Dictionary) -> Dictionary:
	objs.append(d)
	return d


func _furn(nm: String, pos: Vector2) -> Sprite2D:
	var s := Res.prop_sprite(nm)
	s.position = pos.round()
	s.visibility_layer = K.V_INNER
	furn.add_child(s)
	return s


func _sprop(nm: String, pos: Vector2, front_layer: bool = false, parent: Node2D = null) -> Sprite2D:
	var s := Res.prop_sprite(nm)
	s.position = pos.round()
	s.visibility_layer = K.V_OUTER
	var p := parent if parent else (front if front_layer else sprops)
	p.add_child(s)
	return s


# ======================= фасад =======================

func _facade(b: Dictionary) -> void:
	var tm := TileMapLayer.new()
	tm.scale = Vector2(1.0 / K.PX, 1.0 / K.PX)
	tm.tile_set = Res.tileset
	tm.visibility_layer = K.V_OUTER
	tm.name = "facade%d" % b["id"]
	facades.add_child(tm)
	b["facade"] = tm
	b["facade_alpha"] = 1.0
	var fp := Node2D.new()
	fp.name = "fp%d" % b["id"]
	fp.visibility_layer = K.V_OUTER
	fprops.add_child(fp)
	b["fp"] = fp
	var x0: int = b["x0"]
	var w: int = b["w"]
	var n: int = b["n"]
	var key: String = b["mat"]
	var win_step := 5 if key != "granite" else 3
	if key == "stucco":
		win_step = 4
	for f in range(0, n):
		var sr := slab_row(f)
		for c in range(x0, x0 + w):
			for r in range(sr - 4, sr + (1 if f > 0 else 0)):
				var t := "f_%s" % key
				if r == sr and f > 0:
					t = "f_%s_belt" % key
				if f == n - 1 and r == sr - 4:
					t = "f_%s_cornice" % key
				setc(tm, c, r, t, Res.ALT_NONE)
		# окна (кроме первого этажа заведений)
		var lc := x0 + 2
		var shopfront: bool = f == 0 and (b["base"] in ["cafe", "pharmacy", "store", "metro"] or b["kind"] in ["store", "metro"])
		if f == 0 and b["kind"] == "office":
			shopfront = true
		if shopfront:
			_shopfront(b, tm)
			continue
		while lc + 1 < x0 + w - 1:
			# не ставим окно на лестничной клетке первого этажа (там дверь)
			var on_stair: bool = lc + 1 >= int(b["sw0"]) and lc <= int(b["sw1"])
			if not (f == 0 and on_stair):
				for i in 4:
					setc(tm, lc + (i % 2), sr - 3 + i / 2, "f_%s_win%d" % [key, i], Res.ALT_NONE)
			lc += win_step
	_facade_props(b)


func _shopfront(b: Dictionary, tm: TileMapLayer) -> void:
	var x0: int = b["x0"]
	var w: int = b["w"]
	var sr := K.GY
	for c in range(x0 + 1, x0 + w - 1):
		if c >= int(b["sw0"]) and c <= int(b["sw1"]) and b["kind"] != "metro":
			continue
		if b["kind"] == "res":
			# витрина только над заведением слева
			if c >= int(b["sw0"]):
				continue
		setc(tm, c, sr - 3, "shopwin_top", Res.ALT_NONE)
		setc(tm, c, sr - 2, "shopwin", Res.ALT_NONE)
		setc(tm, c, sr - 1, "shopwin_bot", Res.ALT_NONE)
	if b["kind"] == "res":
		var lc: int = int(b["core1"]) + 3
		while lc + 1 < x0 + w - 1:
			for i in 4:
				setc(tm, lc + (i % 2), sr - 3 + i / 2, "f_%s_win%d" % [b["mat"], i], Res.ALT_NONE)
			lc += 5


func _facade_props(b: Dictionary) -> void:
	var fp: Node2D = b["fp"]
	var x0: int = b["x0"]
	var w: int = b["w"]
	var n: int = b["n"]
	var px0 := float(x0 * K.T)
	var px1 := float((x0 + w) * K.T)
	var gy := K.floor_y(0)
	var sx: float = b["stair_x"]
	# вход
	var ent := "entrance"
	if b["kind"] == "office":
		ent = "entrance_glass"
	elif b["kind"] in ["store", "metro"]:
		ent = "entrance_glass"
	elif b["mat"] == "panel":
		ent = "entrance_metal"
	var e := _sprop(ent, Vector2(sx, gy), false, fp)
	b["entr_sprite"] = e
	b["entr_x"] = sx
	if b["kind"] == "res":
		_sprop("canopy", Vector2(sx, gy - 50), false, fp)
		_platform(Rect2(sx - 20, gy - 58, 40, 4))
		_lamp_out(Vector2(sx + 22, gy - 60), 70.0, "walllamp")
	# вход в заведение на первом этаже
	var shop_x := -1.0
	match b["base"]:
		"cafe":
			shop_x = px0 + 14 * K.T
			_sign(fp, "sign_cafe", Vector2(px0 + 10 * K.T, gy - 58))
		"pharmacy":
			shop_x = px0 + 4 * K.T
			_sign(fp, "sign_apteka", Vector2(px0 + 6 * K.T, gy - 58))
		"store":
			_sign(fp, "sign_univ", Vector2(px0 + 9 * K.T, gy - 70))
		"metro":
			_sign(fp, "sign_metro", Vector2(sx + 70, gy - 74))
		"lobby":
			_sign(fp, "sign_granit" if b["name"] == "Гранит" else "sign_nii", Vector2(sx, gy - 62))
	if shop_x > 0:
		_sprop("entrance_glass", Vector2(shop_x, gy), false, fp)
		b["shop_x"] = shop_x
	if b["kind"] == "res" and b["mat"] == "stucco":
		_sign(fp, "sign_slava", Vector2((px0 + px1) / 2.0, float(b["roof_r"] * K.T) + 30))
	# водосточная труба на углу — можно лезть
	var pipe_x := px1 - 6.0 if b["id"] % 2 == 0 else px0 + 6.0
	var top := float(int(b["roof_r"]) * K.T)
	var y := gy - 16.0
	while y >= top:
		_sprop("pipe", Vector2(pipe_x, y + 16), false, fp)
		y -= 16.0
	climbs.append({"x": pipe_x, "y0": top - 4.0, "y1": gy, "kind": "pipe"})
	# балконы жилых домов
	if b["kind"] == "res":
		for f in range(1, n):
			var fy := K.floor_y(f)
			var lc := x0 + 2
			var i := 0
			while lc + 1 < x0 + w - 1:
				var on_stair: bool = lc + 1 >= int(b["sw0"]) and lc <= int(b["core1"])
				if not on_stair and (i + f + int(b["id"])) % 3 == 0:
					var bx := float((lc + 1) * K.T)
					_sprop("balcony%d" % (rng.randi() % 2), Vector2(bx, fy + 4), false, fp)
					_platform(Rect2(bx - 24, fy, 48, 4))
					# балконная дверь
					portals.append({"kind": "window", "x": bx, "y": fy, "bid": b["id"], "f": f, "human": true, "spirit": true, "lock": ""})
					if rng.randf() < 0.35:
						var pot := _sprop("flowerpot", Vector2(bx + rng.randf_range(-18, 18), fy - 10), false, fp)
						_obj({"kind": "pot", "node": pot, "x": pot.position.x, "y": pot.position.y, "inside": false, "bid": b["id"], "f": f, "fallen": false})
				elif not on_stair and rng.randf() < 0.25:
					# форточка: лаз для духа
					portals.append({"kind": "vent", "x": float((lc + 1) * K.T), "y": fy, "bid": b["id"], "f": f, "human": false, "spirit": true, "lock": ""})
				lc += 5
				i += 1
	# пожарная лестница у офисов и сталинки
	if b["kind"] == "office" or b["mat"] == "stucco":
		var lx := px0 + 40.0 if b["id"] % 2 == 1 else px1 - 40.0
		var yy := gy - 32.0
		while yy >= top + 4:
			_sprop("ladder", Vector2(lx, yy + 16), false, fp)
			yy -= 16.0
		climbs.append({"x": lx, "y0": top - 4.0, "y1": gy - 32.0, "kind": "ladder"})
		for f in range(1, n):
			var fy := K.floor_y(f)
			_platform_vis(Rect2(lx - 24, fy, 48, 4))
			portals.append({"kind": "window", "x": lx + (14.0 if b["id"] % 2 == 1 else -14.0), "y": fy, "bid": b["id"], "f": f, "human": true, "spirit": true, "lock": "" if rng.randf() < 0.6 else "fire%d" % b["id"]})
	# камера над входом в офис и магазин
	if b["kind"] in ["office", "store"] or b["base"] in ["pharmacy"]:
		var cam := _sprop("camera", Vector2(sx + 30, gy - 56), false, fp)
		cam.frame = 1
		cams.append({"node": cam, "pos": Vector2(sx + 30, gy - 52), "dir": 1.0, "range": 150.0, "inside": false, "bid": b["id"], "on": true, "seen": []})
	# граффити на глухом цоколе
	if b["kind"] == "res" and rng.randf() < 0.5:
		var g := _sprop(["graf_tsoy", "graf_seen"][rng.randi() % 2], Vector2(px0 + rng.randf_range(30, 90), gy - 6), false, fp)
		g.modulate.a = 0.8


func _sign(fp: Node2D, nm: String, pos: Vector2) -> void:
	var s := _sprop(nm, pos, false, fp)
	var sz := Res.prop_size(nm)
	var c := Color(1.0, 0.85, 0.6)
	_light(lights_out, pos + Vector2(0, -sz.y / 2), Vector2(sz.x * 1.6, 60), c, 0.45, "sign")


func _roof_props(b: Dictionary) -> void:
	var top := float(int(b["roof_r"]) * K.T)
	var px0 := float(int(b["x0"]) * K.T)
	var px1 := px0 + float(int(b["w"]) * K.T)
	if b["kind"] != "metro":
		_sprop("roofexit", Vector2(b["stair_x"], top))
		b["hatch_x"] = b["stair_x"]
	if b.has("vent_x"):
		_sprop("roofvent_big", Vector2(float(b["vent_x"]), top))
	if b["kind"] == "res":
		_sprop("antenna", Vector2(px0 + 30, top))
		if rng.randf() < 0.5:
			_sprop("antenna", Vector2(px1 - 80, top))
		_obj({"kind": "roof_edge", "x": px0 + 8, "y": top, "bid": b["id"]})
		_obj({"kind": "roof_edge", "x": px1 - 8, "y": top, "bid": b["id"]})
	elif b["kind"] == "office":
		_obj({"kind": "roof_edge", "x": px0 + 8, "y": top, "bid": b["id"]})
		_obj({"kind": "roof_edge", "x": px1 - 8, "y": top, "bid": b["id"]})


func _platform(r: Rect2) -> void:
	## Полупроходная площадка (балкон, козырёк): стоять можно, снизу пролетаешь.
	var body := StaticBody2D.new()
	body.collision_layer = K.L_PLATFORM
	body.collision_mask = 0
	var sh := CollisionShape2D.new()
	var rs := RectangleShape2D.new()
	rs.size = r.size
	sh.shape = rs
	sh.one_way_collision = true
	sh.position = r.get_center()
	body.add_child(sh)
	fprops.add_child(body)


func _platform_vis(r: Rect2) -> void:
	var y := int(r.position.y)
	var c0 := int(r.position.x) / K.T
	var c1 := int(r.end.x) / K.T
	for c in range(c0, c1):
		var s := Sprite2D.new()
		s.texture = (Res.tileset.get_source(0) as TileSetAtlasSource).texture
		s.region_enabled = true
		var a: Vector2i = Res.tiles["grate_platform"]
		s.region_rect = Rect2(a.x * K.TT, a.y * K.TT, K.TT, K.TT)
		s.scale = Vector2(1.0 / K.PX, 1.0 / K.PX)
		s.centered = false
		s.position = Vector2(c * K.T, y)
		s.visibility_layer = K.V_OUTER
		fprops.add_child(s)
	_platform(Rect2(c0 * K.T, y, (c1 - c0) * K.T, 4))


# ======================= промежутки =======================

func _gap(g: Dictionary) -> void:
	var c0: int = g["c0"]
	var c1: int = g["c1"]
	var x0 := float(c0 * K.T)
	var x1 := float((c1 + 1) * K.T)
	var gy := K.floor_y(0)
	var kind: String = g["kind"]
	var mid := (x0 + x1) / 2.0
	g["x0"] = x0
	g["x1"] = x1
	# фон: дальние стены двора
	var hb := 3 if kind in ["lane", "backlane"] else 2
	for c in range(c0, c1 + 1):
		for r in range(K.GY - hb, K.GY):
			setc(tm_lane, c, r, "lane_back", Res.ALT_NONE)
	match kind:
		"yard":
			for c in range(c0, c1 + 1):
				setc(tm_common, c, K.GY, "grass", Res.ALT_COMMON)
			_sprop("tree", Vector2(x0 + 30, gy))
			_sprop("birch", Vector2(x1 - 34, gy))
			_sprop("bench", Vector2(mid, gy))
			if x1 - x0 > 150:
				_sprop("fence", Vector2(x0 + 70, gy))
			_lamp_out(Vector2(mid - 30, gy - 66), 110.0, "lamp")
			places[g["name"]] = {"area": "S", "x": mid, "name": g["name"]}
			_manhole(x1 - 20)
		"square":
			for c in range(c0, c1 + 1):
				setc(tm_common, c, K.GY, "gravel", Res.ALT_COMMON)
			_sprop("monument", Vector2(mid, gy))
			_sprop("tree", Vector2(x0 + 26, gy))
			_sprop("tree", Vector2(x1 - 26, gy))
			_sprop("bench", Vector2(mid - 50, gy))
			_sprop("bench", Vector2(mid + 50, gy))
			_sprop("kiosk", Vector2(x0 + 70, gy))
			places["Киоск"] = {"area": "S", "x": x0 + 70 + 30, "name": "Киоск"}
			places["Сквер"] = {"area": "S", "x": mid + 50, "name": "Сквер"}
			places["Парк"] = places["Сквер"]
			var pp := _sprop("payphone", Vector2(x1 - 60, gy))
			_obj({"kind": "payphone", "node": pp, "x": x1 - 60, "y": gy, "inside": false, "ring": false, "name": "у сквера"})
			_lamp_out(Vector2(mid, gy - 66), 120.0, "lamp")
		"garages":
			_sprop("garages", Vector2(x0 + 40, gy))
			_platform(Rect2(x0 + 8, gy - 40, 64, 4))
			var tr := _sprop("transformer", Vector2(x1 - 40, gy))
			_obj({"kind": "transformer", "node": tr, "x": x1 - 40, "y": gy, "inside": false, "off_t": 0.0})
			var d := _sprop("dumpster", Vector2(x1 - 90, gy))
			_obj({"kind": "dumpster", "node": d, "x": x1 - 90, "y": gy, "inside": false, "full": false, "name": "у гаражей"})
			places["Гаражи"] = {"area": "S", "x": x1 - 70, "name": "Гаражи"}
			_lamp_out(Vector2(mid + 10, gy - 66), 100.0, "lamp")
			# люк в коллектор
			_manhole(mid + 24)
		"backlane":
			var d2 := _sprop("dumpster", Vector2(mid + 10, gy))
			_obj({"kind": "dumpster", "node": d2, "x": mid + 10, "y": gy, "inside": false, "full": false, "name": "на задворках"})
			_sprop("urn", Vector2(x0 + 14, gy))
			places["Задворки"] = {"area": "S", "x": mid - 14, "name": "Задворки"}
			_lamp_out(Vector2(mid, gy - 46), 70.0, "walllamp")
			_manhole(x1 - 22)
		"lane":
			if x1 - x0 >= 32 and rng.randf() < 0.5:
				_sprop("fence_wood", Vector2(mid, gy))
			# сток ливнёвки: дух проскальзывает в коллектор
			_drain(mid)


func _links() -> void:
	## Связи соседних домов: мостики на этажах, ходы между подвалами, доски и лестницы между крышами.
	for i in buildings.size() - 1:
		var a: Dictionary = buildings[i]
		var b: Dictionary = buildings[i + 1]
		var gw := int(b["x0"]) - int(a["x0"]) - int(a["w"])
		var ax1 := float(a["px1"])
		var bx0 := float(b["px0"])
		# мостики
		for f in a["bridge_r"]:
			_bridge(a, b, int(f))
		# подвальный ход между соседями
		if a["basement"] and b["basement"] and gw <= 3:
			var y := K.floor_y(-1)
			_furn("door_metal", Vector2(ax1 - 24, y))
			_furn("door_metal", Vector2(bx0 + 24, y))
			portals.append({"kind": "passage", "a": "B%dF-1" % a["id"], "b": "B%dF-1" % b["id"], "x": (ax1 + bx0) / 2.0,
				"path": [Vector2(ax1 - 24, y), Vector2(bx0 + 24, y)], "ya": y, "yb": y, "human": true, "spirit": true,
				"lock": ("base%d" % a["id"]) if rng.randf() < 0.5 else "", "dur": 1.0 + gw * 0.2})
		# крыши
		if a["kind"] == "metro" or b["kind"] == "metro" or gw > 6:
			continue
		var ya := float(int(a["roof_r"]) * K.T)
		var yb := float(int(b["roof_r"]) * K.T)
		if absf(ya - yb) < 2.0:
			if gw > 0:
				_platform_vis(Rect2(ax1 - 8, ya, bx0 - ax1 + 16, 4))
		elif gw <= 4:
			# лестница по стене более высокого дома
			var low_left := ya > yb
			var lo: Dictionary = a if low_left else b
			var hi: Dictionary = b if low_left else a
			var ylo := maxf(ya, yb)
			var yhi := minf(ya, yb)
			var lx := (bx0 - 6.0) if low_left else (ax1 + 6.0)
			if gw == 0:
				lx = (bx0 - 6.0) if low_left else (ax1 + 6.0)
			var yy := ylo - 16.0
			while yy >= yhi - 2:
				_sprop("ladder_iron", Vector2(lx, yy + 16))
				yy -= 16.0
			var xlo := (ax1 - 24.0) if low_left else (bx0 + 24.0)
			var xhi := (bx0 + 24.0) if low_left else (ax1 - 24.0)
			portals.append({"kind": "roofladder", "a": "R%d" % lo["id"], "b": "R%d" % hi["id"], "x": lx,
				"path": [Vector2(xlo, ylo), Vector2(lx, ylo), Vector2(lx, yhi), Vector2(xhi, yhi)], "ya": ylo, "yb": yhi,
				"human": true, "spirit": true, "lock": "", "dur": 0.6 + (ylo - yhi) / 60.0})


func _bridge(a: Dictionary, b: Dictionary, f: int) -> void:
	## Застеклённый мостик через переулок на этаже f (или дверь в общей стене, если дома вплотную).
	var sr := slab_row(f)
	var c0: int = int(a["x0"]) + int(a["w"])
	var c1: int = int(b["x0"]) - 1
	for c in range(c0, c1 + 1):
		setc(tm_back, c, sr, "bridge_floor", Res.ALT_NONE)
		setc(tm_back, c, sr - 5, "bridge_roof", Res.ALT_NONE)
		for r in range(sr - 4, sr):
			setc(tm_back, c, r, "bridge_glass" if r < sr - 1 else "bridge_wall", Res.ALT_NONE)
	var y := K.floor_y(f)
	var ax := float(a["px1"]) - 24.0
	var bx := float(b["px0"]) + 24.0
	_furn("door_metal", Vector2(float(a["px1"]) - 8, y))
	_furn("door_metal", Vector2(float(b["px0"]) + 8, y))
	if c1 >= c0:
		_lamp_in(a, f, Vector2((float(a["px1"]) + float(b["px0"])) / 2.0, y - 60), 40.0, Color(0.9, 0.95, 1.0), "room")
	portals.append({"kind": "bridge", "a": area_of_floor(int(a["id"]), f), "b": area_of_floor(int(b["id"]), f),
		"x": (ax + bx) / 2.0, "path": [Vector2(ax, y), Vector2(bx, y)], "ya": y, "yb": y, "human": true, "spirit": true,
		"lock": "", "dur": maxf(0.8, (bx - ax) / 50.0)})


func _building_at(x: float) -> Dictionary:
	for b in buildings:
		if x >= float(b["px0"]) and x < float(b["px1"]):
			return b
	return {}


func building_at(x: float) -> Dictionary:
	return _building_at(x)


func _manhole(x: float) -> void:
	var gy := K.floor_y(0)
	_sprop("manhole", Vector2(x, gy + 2))
	portals.append({"kind": "manhole", "x": x, "a": "S", "b": "C", "ya": gy, "yb": float(C_ROW * K.T), "human": true, "spirit": true, "lock": "", "dur": 1.6})


func _drain(x: float) -> void:
	var gy := K.floor_y(0)
	_sprop("drain_grate", Vector2(x, gy + 3))
	portals.append({"kind": "drain", "x": x, "a": "S", "b": "C", "ya": gy, "yb": float(C_ROW * K.T), "human": false, "spirit": true, "lock": "", "dur": 0.8})


# ======================= подземелье =======================

func _underground() -> void:
	## Три уровня: верхний коллектор (кирпич, пар, решётки), метро и нижний дренажный тоннель (вода,
	## насосная, лежанка бродяги). Связи: шахты из подвалов, люки и стоки с улицы, железные лестницы
	## между уровнями коллектора, служебная лестница из дренажа на платформу (за ключом обходчика).
	var cy := float(C_ROW * K.T)
	# ---- верхний коллектор ----
	carve(coll_c0, coll_c1, K.GY + 8, K.GY + 10)
	for c in range(coll_c0, coll_c1 + 1):
		setc(tm_common, c, K.GY + 7, "tunnel_brick", Res.ALT_COMMON)
		setc(tm_common, c, C_ROW, "tunnel_brick", Res.ALT_COMMON)
		var wet := (c / 9) % 3 == 1
		for r in range(K.GY + 8, K.GY + 11):
			setc(tm_back, c, r, "tunnel_wet" if wet else "tunnel_back", Res.ALT_NONE)
	var cr := _add_room({"id": -1, "rooms": []}, -2, coll_c0, coll_c1, "collector", "tunnel_back", 0, false, false)
	cr["y"] = cy
	var x := float(coll_c0 * K.T) + 60
	while x < float(coll_c1 * K.T):
		var l := _lamp_in({"id": -1}, -2, Vector2(x, float((K.GY + 8) * K.T) + 4), 105.0, Color(0.9, 0.85, 0.6), "bulb")
		l["inside_area"] = "C"
		if rng.randf() < 0.2:
			l["broken"] = true
		x += rng.randf_range(200.0, 290.0)
	# трубы под сводом, вентили, таблички, лужи, завалы
	x = float(coll_c0 * K.T) + 24
	while x < float(coll_c1 * K.T) - 24:
		_furn("pipes_big", Vector2(x, float((K.GY + 8) * K.T) + 14))
		x += 48.0
	var used := []
	for i in int(width / 22):
		var px := rng.randf_range(float(coll_c0 * K.T) + 40, float(coll_c1 * K.T) - 40)
		match i % 5:
			0: _furn("valve", Vector2(px, cy - 26))
			1: _furn("puddle", Vector2(px, cy + 1))
			2: _furn("rubble", Vector2(px, cy))
			3: _furn("sign_coll", Vector2(px, cy - 34))
			4: _furn("arrow_sign", Vector2(px, cy - 30))
	# решётки поперёк коллектора: часть заперта (ключ у дворника и в насосной)
	var nseg := 4
	for k in range(1, nseg):
		var gx := coll_c0 + (coll_c1 - coll_c0) * k / nseg + ri(-6, 6)
		_door({"id": -1}, -2, float(gx * K.T + 8), cy, "grate_door", "grate" if rng.randf() < 0.6 else "")
		used.append(gx)
	# струи пара: жгут духа, когда бьют
	for i in 3:
		var sx := rng.randf_range(float(coll_c0 * K.T) + 80, float(coll_c1 * K.T) - 80)
		var sp := _furn("steam", Vector2(sx, cy - 30))
		sp.visible = false
		_furn("valve", Vector2(sx, cy - 44))
		steams.append({"x": sx, "y": cy - 40, "node": sp, "t": rng.randf_range(2.0, 8.0), "on": false})
	# крысы
	for i in 4:
		var rx := rng.randf_range(float(coll_c0 * K.T) + 40, float(coll_c1 * K.T) - 40)
		var rs := _furn("rat", Vector2(rx, cy))
		rats.append({"node": rs, "x0": rx - rng.randf_range(40, 120), "x1": rx + rng.randf_range(40, 120), "v": rng.randf_range(24, 46) * (1 if rng.randf() < 0.5 else -1), "y": cy})
	# ---- станция метро ----
	carve(metro_c0, metro_c1, K.GY + 13, K.GY + 18)
	for c in range(metro_c0, metro_c1 + 1):
		setc(tm_common, c, M_ROW, "platform", Res.ALT_COMMON)
		setc(tm_common, c, K.GY + 12, "wall_granite", Res.ALT_COMMON)
		for r in range(K.GY + 13, M_ROW):
			setc(tm_back, c, r, "marble", Res.ALT_NONE)
	var mr := _add_room({"id": -1, "rooms": []}, -3, metro_c0, metro_c1, "platform", "marble", 0, false, false)
	mr["y"] = float(M_ROW * K.T)
	x = float(metro_c0 * K.T) + 40
	while x < float(metro_c1 * K.T):
		var l2 := _lamp_in({"id": -1}, -3, Vector2(x, float((K.GY + 13) * K.T) + 6), 120.0, Color(1.0, 0.95, 0.85), "lamp")
		l2["inside_area"] = "M"
		x += 120.0
	var sb := Res.prop_sprite("sign_metro")
	sb.position = Vector2((metro_c0 + metro_c1) * K.T / 2.0, float((K.GY + 15) * K.T))
	sb.visibility_layer = K.V_INNER
	furn.add_child(sb)
	places["Метро"] = {"area": "M", "x": (metro_c0 + metro_c1) * K.T / 2.0 + 60, "name": "Метро"}
	# ---- нижний дренажный тоннель ----
	var dy := float(D_ROW * K.T)
	carve(coll_c0, coll_c1, K.GY + 22, K.GY + 24)
	for c in range(coll_c0, coll_c1 + 1):
		setc(tm_common, c, K.GY + 21, "tunnel_conc", Res.ALT_COMMON)
		setc(tm_common, c, D_ROW, "tunnel_conc", Res.ALT_COMMON)
		for r in range(K.GY + 22, D_ROW):
			setc(tm_back, c, r, "tunnel_conc_back", Res.ALT_NONE)
	var dr := _add_room({"id": -1, "rooms": []}, -4, coll_c0, coll_c1, "drain", "tunnel_conc_back", 0, false, false)
	dr["y"] = dy
	water = WaterLayer.new()
	water.x0 = float(coll_c0 * K.T)
	water.x1 = float((coll_c1 + 1) * K.T)
	water.y = dy
	water.visibility_layer = K.V_INNER
	water.z_index = K.Z_PEOPLE + 2
	add_child(water)
	x = float(coll_c0 * K.T) + 120
	while x < float(coll_c1 * K.T):
		if rng.randf() < 0.8:
			var l3 := _lamp_in({"id": -1}, -4, Vector2(x, float((K.GY + 22) * K.T) + 4), 95.0, Color(0.8, 0.9, 0.85), "bulb")
			l3["inside_area"] = "D"
		x += rng.randf_range(240.0, 360.0)
	# насосная у левого края: ящик обходчика с ключами от решёток и служебной двери метро
	var pump_x := float((coll_c0 + 5) * K.T)
	_furn("pump", Vector2(pump_x, dy))
	_furn("pipes_big", Vector2(pump_x + 40, dy - 40))
	var lb := _furn("lockbox", Vector2(pump_x + 40, dy))
	_obj({"kind": "lockbox", "node": lb, "x": pump_x + 40, "y": dy, "bid": -1, "f": -4, "inside": true, "open": false,
		"keys": ["grate", "metro"], "what": "ключи обходчика: от решёток коллектора и служебной двери метро"})
	places["Насосная"] = {"area": "D", "x": pump_x + 20, "name": "Насосная"}
	# лежанка бродяги
	var camp_x := rng.randf_range(float(coll_c0 * K.T) + 400, float(coll_c1 * K.T) - 200)
	if camp_x > float(metro_c0 * K.T) - 60 and camp_x < float(metro_c1 * K.T) + 60:
		camp_x = float(metro_c1 * K.T) + 160
	camp_x = minf(camp_x, float(coll_c1 * K.T) - 120)
	_furn("mattress", Vector2(camp_x, dy))
	_furn("campfire", Vector2(camp_x + 34, dy))
	_furn("bottles", Vector2(camp_x - 30, dy))
	_furn("crate", Vector2(camp_x + 56, dy))
	var lc := _lamp_in({"id": -1}, -4, Vector2(camp_x + 34, dy - 10), 80.0, Color(1.0, 0.6, 0.3), "bulb")
	lc["inside_area"] = "D"
	lc["hurt"] = true
	places["Лежанка"] = {"area": "D", "x": camp_x + 10, "name": "Лежанка"}
	# лестницы между коллектором и дренажом (мимо станции)
	var ladders := 0
	var tries := 0
	while ladders < 3 and tries < 40:
		tries += 1
		var lcol := ri(coll_c0 + 4, coll_c1 - 4)
		if lcol >= metro_c0 - 2 and lcol <= metro_c1 + 2:
			continue
		var bad := false
		for u in used:
			if absi(int(u) - lcol) < 6:
				bad = true
		if bad:
			continue
		used.append(lcol)
		ladders += 1
		# решётка в полу коллектора и в своде дренажа, шахта между ними
		setc(tm_common, lcol, C_ROW, "vent", Res.ALT_GRATE)
		setc(tm_common, lcol, K.GY + 21, "vent", Res.ALT_GRATE)
		carve(lcol, lcol, C_ROW + 1, K.GY + 20)
		for r in range(C_ROW + 1, K.GY + 21):
			setc(tm_back, lcol, r, "tunnel_back", Res.ALT_NONE)
		var lx := float(lcol * K.T + 8)
		var yy := cy
		while yy < dy:
			_furn("ladder_iron", Vector2(lx, yy + 16))
			yy += 16.0
		portals.append({"kind": "ladder", "x": lx, "a": "C", "b": "D", "ya": cy, "yb": dy, "human": true, "spirit": true, "lock": "", "dur": 2.2})
	# служебная лестница из дренажа на платформу (заперта)
	var sx2 := float((metro_c0 + 3) * K.T)
	_furn("srv_door", Vector2(sx2, float(M_ROW * K.T)))
	_furn("srv_door", Vector2(sx2, dy))
	portals.append({"kind": "srvstairs", "x": sx2, "a": "D", "b": "M", "ya": dy, "yb": float(M_ROW * K.T), "human": true, "spirit": true, "lock": "metro", "dur": 2.0})
	# шахты из подвалов в коллектор
	for b in buildings:
		if b["basement"]:
			var shx := float((int(b["x0"]) + 3) * K.T)
			carve(int(b["x0"]) + 2, int(b["x0"]) + 3, K.GY + 6, K.GY + 7)
			for r in range(K.GY + 6, K.GY + 8):
				setc(tm_back, int(b["x0"]) + 2, r, "tunnel_back", Res.ALT_NONE)
				setc(tm_back, int(b["x0"]) + 3, r, "tunnel_back", Res.ALT_NONE)
				setc(tm_inner, int(b["x0"]) + 2, r, "vent", Res.ALT_GRATE)
				setc(tm_inner, int(b["x0"]) + 3, r, "vent", Res.ALT_GRATE)
			portals.append({"kind": "shaft", "x": shx, "a": "B%dF-1" % b["id"], "b": "C", "ya": K.floor_y(-1), "yb": cy,
				"human": true, "spirit": true, "lock": "", "dur": 1.4})


# ======================= улица =======================

func _street() -> void:
	var gy := K.floor_y(0)
	# фонари вдоль тротуара
	var x := 120.0
	while x < float(width * K.T) - 60:
		_lamp_out(Vector2(x, gy - 66), 120.0, "lamp")
		street_x.append(x)
		x += rng.randf_range(300, 380)
	# остановка у метро
	var mb := _first("metro")
	var bx := float(mb["px1"]) - 10
	_sprop("busstop", Vector2(bx, gy))
	_platform(Rect2(bx - 30, gy - 46, 60, 4))
	places["Остановка"] = {"area": "S", "x": bx, "name": "Остановка"}
	# таксофоны
	for nm in ["у универсама", "у метро"]:
		var b2 := b_named("Универсам") if nm == "у универсама" else mb
		var px := float(b2["px0"]) - 20 if nm == "у универсама" else float(b2["px0"]) + 30
		var pp := _sprop("payphone", Vector2(px, gy))
		_obj({"kind": "payphone", "node": pp, "x": px, "y": gy, "inside": false, "ring": false, "name": nm})
	# урны
	for i in 8:
		var ux := rng.randf_range(100, float(width * K.T) - 100)
		var u := _sprop("urn", Vector2(ux, gy))
		_obj({"kind": "movable", "what": "urn", "node": u, "x": ux, "y": gy, "inside": false, "fallen": false})
	# светофор у метро
	_sprop("trafficlight", Vector2(float(mb["px0"]) - 12, gy))
	# стоки в случайных местах тротуара
	for i in 3:
		_drain(rng.randf_range(200.0, float(width * K.T) - 200.0))
	# проезжая часть спереди
	var road := Road.new()
	road.w = float(width * K.T)
	road.visibility_layer = K.V_OUTER
	front.add_child(road)
	places["Универсам"] = {"area": "B%dF0" % b_named("Универсам")["id"], "x": float(b_named("Универсам")["px0"]) + 100, "name": "Универсам"}


class Road extends Node2D:
	var w := 1000.0

	func _draw() -> void:
		var gy := K.floor_y(0)
		draw_rect(Rect2(0, gy + 3, w, 3), Color(0.38, 0.38, 0.36))     # бордюр
		draw_rect(Rect2(0, gy + 6, w, 26), Color(0.24, 0.245, 0.26))
		draw_rect(Rect2(0, gy + 6, w, 1), Color(0.18, 0.18, 0.19))
		var x := 0.0
		while x < w:
			draw_rect(Rect2(x, gy + 19, 18, 1), Color(0.62, 0.6, 0.52, 0.7))
			x += 40.0


class WaterLayer extends Node2D:
	## Вода в дренажном тоннеле: по колено, рябь бежит вдоль течения.
	var x0 := 0.0
	var x1 := 0.0
	var y := 0.0
	var t := 0.0

	func _process(dt: float) -> void:
		t += dt
		queue_redraw()

	func _draw() -> void:
		draw_rect(Rect2(x0, y - 10, x1 - x0, 10), Color(0.16, 0.27, 0.3, 0.55))
		var x := x0 + fposmod(t * 22.0, 24.0)
		while x < x1:
			draw_rect(Rect2(x, y - 10, 9, 1), Color(0.45, 0.6, 0.64, 0.6))
			draw_rect(Rect2(x + 12, y - 6, 5, 1), Color(0.35, 0.5, 0.55, 0.45))
			x += 24.0


# ======================= свет =======================

func _light(parent: Node2D, pos: Vector2, size: Vector2, col: Color, energy: float, kind: String) -> Sprite2D:
	var s := Sprite2D.new()
	s.texture = Res.light_tex
	s.position = pos
	s.scale = size / 128.0
	s.modulate = Color(col.r * energy * 0.5, col.g * energy * 0.5, col.b * energy * 0.5, 1.0)
	var m := CanvasItemMaterial.new()
	m.blend_mode = CanvasItemMaterial.BLEND_MODE_ADD
	s.material = m
	s.visibility_layer = parent.visibility_layer
	parent.add_child(s)
	return s


func _lamp_out(pos: Vector2, r: float, kind: String) -> Dictionary:
	var spr: Sprite2D = null
	if kind == "lamp":
		spr = _sprop("lamp", Vector2(pos.x - 4, K.floor_y(0)))
	elif kind == "walllamp":
		spr = _sprop("walllamp", pos + Vector2(0, 6), false, fprops)
	var lpos := pos + (Vector2(10, -5) if kind == "lamp" else Vector2(0, 4))
	var lt := _light(lights_out, lpos + Vector2(0, r * 0.35), Vector2(r * 2.0, r * 2.4), Color(1.0, 0.85, 0.55), 1.0, kind)
	var d := {"pos": lpos, "r": r, "on": true, "outer": true, "bid": -1, "node": spr, "light": lt, "kind": kind, "off_t": 0.0, "hurt": true}
	lamps.append(d)
	return d


func _lamp_in(b: Dictionary, f: int, pos: Vector2, r: float, col: Color, kind: String = "room") -> Dictionary:
	if kind == "bulb":
		var s := Res.prop_sprite("ceilinglamp")
		s.position = pos + Vector2(0, -2)
		s.visibility_layer = K.V_INNER
		furn.add_child(s)
	var lt := _light(lights_in, pos + Vector2(0, r * 0.3), Vector2(r * 2.2, r * 1.6), col, 0.9, kind)
	var d := {"pos": pos, "r": r, "on": true, "outer": false, "bid": int(b.get("id", -1)), "f": f, "node": null, "light": lt,
		"kind": kind, "off_t": 0.0, "hurt": kind == "bulb"}
	lamps.append(d)
	return d


func room_lamps() -> void:
	## Свет в комнатах (по одному на комнату): включается расписанием.
	for rm in rooms:
		if rm["kind"] in ["stair", "collector", "platform", "basement", "lift", "drain"]:
			continue
		var cx := (float(rm["x0"]) + float(rm["x1"])) / 2.0
		var y := float(rm["y"])
		var wdt := float(rm["x1"]) - float(rm["x0"])
		var b := {"id": rm["bid"]}
		var col := Color(1.0, 0.86, 0.62)
		if rm["kind"] in ["office", "store", "pharmacy", "security", "lobby", "metro", "archive", "meeting", "corridor", "bath"]:
			col = Color(0.85, 0.95, 1.0)
		var s := Res.prop_sprite("ceilinglamp")
		s.position = Vector2(cx, y - 64)
		s.visibility_layer = K.V_INNER
		furn.add_child(s)
		var l := _lamp_in(b, int(rm["f"]), Vector2(cx, y - 52), maxf(60.0, wdt * 0.6), col, "room")
		l["light"].scale = Vector2(wdt * 1.3, 120.0) / 128.0
		l["light"].position = Vector2(cx, y - 30)
		l["room"] = rm["id"]
		rm["lamp"] = l


# ======================= граф переходов =======================

func area_of_floor(bid: int, f: int) -> String:
	return "B%dF%d" % [bid, f]


static func px_from(pt: Dictionary, dir: int) -> float:
	## x перехода с той стороны, откуда в него входят.
	if pt.has("path"):
		var path: Array = pt["path"]
		return (path[0] as Vector2).x if dir > 0 else (path[path.size() - 1] as Vector2).x
	return float(pt["x"])


static func px_to(pt: Dictionary, dir: int) -> float:
	if pt.has("path"):
		var path: Array = pt["path"]
		return (path[path.size() - 1] as Vector2).x if dir > 0 else (path[0] as Vector2).x
	return float(pt["x"])


func _areas_and_portals() -> void:
	var gy := K.floor_y(0)
	areas["S"] = {"id": "S", "inside": false, "bid": -1, "f": 0, "y": gy, "x0": 24.0, "x1": float(width * K.T) - 24.0}
	areas["C"] = {"id": "C", "inside": true, "bid": -1, "f": -2, "y": float(C_ROW * K.T), "x0": float(coll_c0 * K.T) + 8, "x1": float((coll_c1 + 1) * K.T) - 8}
	areas["M"] = {"id": "M", "inside": true, "bid": -1, "f": -3, "y": float(M_ROW * K.T), "x0": float(metro_c0 * K.T) + 8, "x1": float((metro_c1 + 1) * K.T) - 8}
	areas["D"] = {"id": "D", "inside": true, "bid": -1, "f": -4, "y": float(D_ROW * K.T), "x0": float(coll_c0 * K.T) + 8, "x1": float((coll_c1 + 1) * K.T) - 8}
	for b in buildings:
		var bid: int = b["id"]
		var x0 := float(int(b["x0"]) + 1) * K.T + 4
		var x1 := float(int(b["x0"]) + int(b["w"]) - 1) * K.T - 4
		var fl := range(0, int(b["n"]))
		if b["basement"]:
			fl = range(-1, int(b["n"]))
		for f in fl:
			var id := area_of_floor(bid, f)
			areas[id] = {"id": id, "inside": true, "bid": bid, "f": f, "y": K.floor_y(f), "x0": x0, "x1": x1}
		var top := float(int(b["roof_r"]) * K.T)
		areas["R%d" % bid] = {"id": "R%d" % bid, "inside": false, "bid": bid, "f": 99, "y": top, "x0": float(b["px0"]) + 20, "x1": float(b["px1"]) - 20}
		var sx: float = b["stair_x"]
		# лифт (если работает): люди едут на нём охотнее, чем идут пешком
		if b["lift"] and not b["lift_broken"]:
			for f in range(0, int(b["n"]) - 1):
				portals.append({"kind": "lift", "x": float(b["lift_x"]), "a": area_of_floor(bid, f), "b": area_of_floor(bid, f + 1),
					"ya": K.floor_y(f), "yb": K.floor_y(f + 1), "human": true, "spirit": true, "lock": "", "dur": 1.0, "bid": bid,
					"zw": 18.0})
		# лестницы: подниматься можно из любой точки клетки
		for f in fl:
			if f + 1 < int(b["n"]):
				portals.append({"kind": "stairs", "x": sx, "a": area_of_floor(bid, f), "b": area_of_floor(bid, f + 1),
					"ya": K.floor_y(f), "yb": K.floor_y(f + 1), "human": true, "spirit": true, "lock": "", "dur": 0.9, "zw": 30.0})
		# вход с улицы
		portals.append({"kind": "entrance", "x": sx, "a": "S", "b": area_of_floor(bid, 0), "ya": gy, "yb": gy,
			"human": true, "spirit": true, "lock": "", "dur": 0.5, "sprite": b.get("entr_sprite")})
		if b.has("shop_x"):
			portals.append({"kind": "entrance", "x": float(b["shop_x"]), "a": "S", "b": area_of_floor(bid, 0), "ya": gy, "yb": gy,
				"human": true, "spirit": true, "lock": "", "dur": 0.5})
		# выход на крышу
		if b.has("hatch_x"):
			portals.append({"kind": "hatch", "x": sx, "a": area_of_floor(bid, int(b["n"]) - 1), "b": "R%d" % bid,
				"ya": K.floor_y(int(b["n"]) - 1), "yb": top, "human": true, "spirit": true, "lock": ("roof%d" % bid) if rng.randf() < 0.5 else "", "dur": 1.0})
		# вентшахта: сверху на крышу, снизу в подвал — только для духа
		if b.has("vent_x"):
			var vx: float = b["vent_x"]
			portals.append({"kind": "ventshaft", "x": vx, "a": area_of_floor(bid, int(b["n"]) - 1), "b": "R%d" % bid,
				"ya": K.floor_y(int(b["n"]) - 1), "yb": top, "human": false, "spirit": true, "lock": "", "dur": 0.6})
			if b["basement"]:
				portals.append({"kind": "ventshaft", "x": vx, "a": area_of_floor(bid, -1), "b": area_of_floor(bid, 0),
					"ya": K.floor_y(-1), "yb": K.floor_y(0), "human": false, "spirit": true, "lock": "", "dur": 0.6})
		# служебный выход «Гранита» на задворки
		if b["name"] == "Гранит":
			var bx := float(b["px1"]) - 24
			portals.append({"kind": "backdoor", "x": bx, "a": "S", "b": area_of_floor(bid, 0), "ya": gy, "yb": gy,
				"human": true, "spirit": true, "lock": "sec%d" % bid, "dur": 0.6})
			_sprop("door_metal", Vector2(float(b["px1"]) - 8, gy), false, b["fp"])
		if b["kind"] == "metro":
			portals.append({"kind": "escalator", "x": float(b["px1"]) - 70, "a": area_of_floor(bid, 0), "b": "M",
				"ya": gy, "yb": float(M_ROW * K.T), "human": true, "spirit": true, "lock": "", "dur": 2.6})
	# окна и форточки: связывают «снаружи» и этаж на одной высоте
	for p in portals:
		if p["kind"] in ["window", "vent"]:
			p["a"] = "OUT"
			p["b"] = area_of_floor(int(p["bid"]), int(p["f"]))
			p["ya"] = p["y"]
			p["yb"] = p["y"]
			p["dur"] = 0.6
	places["Офис"] = _desk_place(b_named("Гранит"), 2)
	places["НИИ"] = _desk_place(b_named("НИИ"), 2)
	var cafe := _first_room("cafe")
	places["Кафе"] = {"area": area_of_floor(int(cafe["bid"]), 0), "x": (float(cafe["x0"]) + float(cafe["x1"])) / 2.0 + 30, "name": "Кафе"}
	var ph := _first_room("pharmacy")
	places["Аптека"] = {"area": area_of_floor(int(ph["bid"]), 0), "x": float(ph["x0"]) + 40, "name": "Аптека"}


func _first_room(kind: String) -> Dictionary:
	for rm in rooms:
		if rm["kind"] == kind:
			return rm
	return {}


func _desk_place(b: Dictionary, f: int) -> Dictionary:
	for rid in b["rooms"]:
		var rm: Dictionary = rooms[rid]
		if int(rm["f"]) == f and rm["kind"] == "office" and (rm["spots"] as Array).size() > 0:
			return {"area": area_of_floor(int(b["id"]), f), "x": float(rm["spots"][0]["x"]), "name": b["name"], "room": rm["id"]}
	return {"area": area_of_floor(int(b["id"]), 0), "x": float(b["stair_x"]), "name": b["name"]}


func room_at(area: String, x: float) -> Dictionary:
	if not areas.has(area):
		return {}
	var a: Dictionary = areas[area]
	if area == "C":
		return rooms_by_kind("collector")
	if area == "M":
		return rooms_by_kind("platform")
	if area == "D":
		return rooms_by_kind("drain")
	if not a["inside"]:
		return {}
	var b: Dictionary = buildings[int(a["bid"])]
	for rid in b["rooms"]:
		var rm: Dictionary = rooms[rid]
		if int(rm["f"]) == int(a["f"]) and x >= float(rm["x0"]) - 8 and x <= float(rm["x1"]) + 8:
			return rm
	return {}


func rooms_by_kind(kind: String) -> Dictionary:
	for rm in rooms:
		if rm["kind"] == kind:
			return rm
	return {}


func route(from_area: String, to_area: String) -> Array:
	## Поиск в ширину по переходам. Возвращает список переходов [{p, dir}] (dir 1: a→b, -1: b→a).
	if from_area == to_area:
		return []
	var prev := {from_area: null}
	var q := [from_area]
	while q.size() > 0:
		var cur: String = q.pop_front()
		if cur == to_area:
			break
		for p in portals:
			if p["kind"] in ["window", "vent"] or not p["human"]:
				continue
			var nxt := ""
			var dir := 0
			if p["a"] == cur:
				nxt = p["b"]
				dir = 1
			elif p["b"] == cur:
				nxt = p["a"]
				dir = -1
			if nxt != "" and not prev.has(nxt):
				prev[nxt] = [cur, p, dir]
				q.append(nxt)
	if not prev.has(to_area):
		return []
	var out := []
	var c := to_area
	while prev[c] != null:
		var e: Array = prev[c]
		out.push_front({"p": e[1], "dir": e[2]})
		c = e[0]
	return out


func area_at(pos: Vector2, inside: bool) -> String:
	## Определяет зону по положению (для брошенных тел и падений).
	if not inside:
		for b in buildings:
			var top := float(int(b["roof_r"]) * K.T)
			if pos.x >= float(b["px0"]) and pos.x < float(b["px1"]) and absf(pos.y - top) < 10:
				return "R%d" % b["id"]
		if absf(pos.y - K.floor_y(0)) < 12:
			return "S"
		return ""
	if pos.y > float((K.GY + 21) * K.T):
		return "D"
	if pos.y > float((K.GY + 12) * K.T):
		if pos.x >= float(metro_c0 * K.T) and pos.x <= float((metro_c1 + 1) * K.T) and pos.y <= float(M_ROW * K.T) + 8:
			return "M"
		return ""
	if pos.y > float((K.GY + 7) * K.T):
		return "C"
	var b := _building_at(pos.x)
	if b.is_empty():
		return ""
	var best := ""
	var bd := 9999.0
	for id in areas:
		var a: Dictionary = areas[id]
		if a["inside"] and int(a["bid"]) == int(b["id"]):
			var d := absf(float(a["y"]) - pos.y)
			if d < bd:
				bd = d
				best = id
	return best if bd < 14.0 else ""


func area_rect(id: String) -> Rect2:
	var a: Dictionary = areas[id]
	return Rect2(float(a["x0"]), float(a["y"]) - 64.0, float(a["x1"]) - float(a["x0"]), 64.0)
