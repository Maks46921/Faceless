class_name City
extends Node2D
## Район в разрезе: один проспект, вдоль него дома, переулки и дворы; под землёй подвалы,
## коллектор и станция метро. Строит тайлы, фасады, предметы, свет, двери и граф переходов.

var rng := RandomNumberGenerator.new()
var width := 0                  # в тайлах
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


func _layer(nm: String, vis: int, z: int) -> TileMapLayer:
	var t := TileMapLayer.new()
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
	_underground()
	_street()
	_areas_and_portals()


# ======================= план =======================

func _plan() -> void:
	## Последовательность домов и промежутков вдоль проспекта.
	var res_mats := ["panel", "brick", "sbrick", "panel", "stucco"]
	res_mats.shuffle()
	var seq: Array = [
		["gap", "lane", 4],
		["b", "res", 26, rng.randi_range(8, 9), "panel", "res"],
		["gap", "yard", 11, "Двор"],
		["b", "res", 22, rng.randi_range(5, 6), "brick", "pharmacy"],
		["gap", "lane", 3],
		["b", "office", 28, 7, "granite", "lobby", "Гранит"],
		["gap", "backlane", 5, "Задворки"],
		["b", "res", 32, 6, "stucco", "cafe"],
		["gap", "square", 15, "Сквер"],
		["b", "metro", 12, 1, "conc", "metro"],
		["gap", "lane", 3],
		["b", "res", 26, 9, res_mats[0], "res"],
		["gap", "garages", 13, "Гаражи"],
		["b", "store", 26, 2, "conc", "store", "Универсам"],
		["gap", "lane", 3],
		["b", "office", 24, 6, "brick", "lobby", "НИИ"],
		["gap", "lane", 4],
		["b", "res", 22, rng.randi_range(5, 6), res_mats[1], "res"],
		["gap", "yard", 9, "Площадка"],
		["b", "res", 26, rng.randi_range(8, 9), res_mats[2], "res"],
		["gap", "lane", 5],
	]
	var c := 2
	var bid := 0
	for s in seq:
		if s[0] == "gap":
			var g := {"kind": s[1], "c0": c, "c1": c + int(s[2]) - 1, "name": s[3] if s.size() > 3 else ""}
			gaps.append(g)
			c += int(s[2])
		else:
			var b := {"id": bid, "kind": s[1], "x0": c, "w": int(s[2]), "n": int(s[3]), "mat": s[4], "base": s[5],
				"name": s[6] if s.size() > 6 else "", "basement": s[1] in ["res", "office"], "floors": {}, "rooms": []}
			b["roof_r"] = K.GY - K.FH * int(b["n"])
			b["px0"] = c * K.T
			b["px1"] = (c + int(s[2])) * K.T
			buildings.append(b)
			bid += 1
			c += int(s[2])
	width = c + 2
	# коллектор и метро
	coll_c0 = 4
	coll_c1 = width - 5
	var mb: Dictionary = _first("metro")
	metro_c0 = int(mb["x0"]) - 14
	metro_c1 = int(mb["x0"]) + int(mb["w"]) + 14


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
	for r in range(K.GY - 60, K.GY):
		setc(tm_common, 0, r, "wall_conc", Res.ALT_COMMON)
		setc(tm_common, width - 1, r, "wall_conc", Res.ALT_COMMON)


func carve(c0: int, c1: int, r0: int, r1: int) -> void:
	for c in range(c0, c1 + 1):
		for r in range(r0, r1 + 1):
			tm_common.erase_cell(Vector2i(c, r))


# ======================= дома =======================

const WALLPAPERS := ["wp_flower", "wp_stripe", "wp_rhomb", "wp_blue", "wp_plain"]


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
	# лестничная клетка: 4 колонки посередине (у метро и универсама — сбоку)
	var sw0 := x0 + w / 2 - 2
	if b["kind"] in ["metro"]:
		sw0 = x0 + 2
	if b["kind"] == "store":
		sw0 = x0 + w - 6
	b["sw0"] = sw0
	b["sw1"] = sw0 + 3
	b["stair_x"] = float((sw0 + 2) * K.T)
	for f in range(0, n):
		_floor(b, f)
	if b["basement"]:
		_basement(b)
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
			if wp.begins_with("wp_") and r == r1:
				t = wp + "_low"
			elif wp == "pod":
				t = "pod_high" if r == r0 else ("pod_mid" if r == r0 + 1 else "pod_low")
			elif wp == "office" and r == r1:
				t = "office_low"
			setc(tm_back, c, r, t, Res.ALT_NONE)
	return rm


func _wall(b: Dictionary, f: int, c: int, kind: String, lock: String = "") -> void:
	## Перегородка: верхний ряд стена, ниже проём; дверь — предмет со столкновением.
	var r1 := slab_row(f) - 1 if f >= 0 else K.GY + 5
	var r0 := r1 - 3
	setc(tm_inner, c, r0, "cutwall", Res.ALT_INTERIOR)
	if kind == "solid":
		for r in range(r0 + 1, r1 + 1):
			setc(tm_inner, c, r, "cutwall", Res.ALT_INTERIOR)
		return
	if kind == "vent":     # стена с лазом у пола: человек не пройдёт
		for r in range(r0 + 1, r1):
			setc(tm_inner, c, r, "cutwall", Res.ALT_INTERIOR)
		setc(tm_inner, c, r1, "vent", Res.ALT_GRATE)
		return
	if kind == "door" or kind == "metal":
		_door(b, f, c, kind, lock)


func _door(b: Dictionary, f: int, c: int, kind: String, lock: String) -> Dictionary:
	var x := float(c * K.T + K.T / 2)
	var y := K.floor_y(f)
	var nd := Node2D.new()
	nd.position = Vector2(x, y)
	nd.visibility_layer = K.V_INNER
	var sp := Res.prop_sprite("door" if kind == "door" else "door_metal", 0)
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
		"key": lock, "x": x, "y": y, "bid": b["id"], "f": f, "metal": kind == "metal", "inside": true, "t_close": 0.0}
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
			for c in range(sw0, sw1 + 1):
				setc(tm_inner, c, sr, "slab_concrete", Res.ALT_INTERIOR)
	var ground := f == 0
	var base: String = b["base"]
	# лестничная клетка
	var wpst := "pod" if kind in ["res"] else ("office" if kind == "office" else "shop")
	if kind == "metro":
		wpst = "marble"
	var stair := _add_room(b, f, sw0, sw1, "stair", wpst)
	_stairs_sprite(b, f)
	if kind == "res" and ground:
		_furn("mailboxes", Vector2((sw0 + 1) * K.T + 4, K.floor_y(0) - 22))
	if kind == "metro":
		_metro_floor(b, stair)
		return
	var lw := sw0 - 1        # стена слева от клетки
	var rw := sw1 + 1
	var left := [x0 + 1, lw - 1]
	var right := [rw + 1, x0 + w - 2]
	if kind == "res":
		if ground and base != "res":
			# левая половина — заведение, правая — квартира
			_shop(b, f, left[0], left[1], base)
			_wall(b, f, lw, "door", "")
			_apartment(b, f, right[0], right[1], 2 * f + 2, false)
			_wall(b, f, rw, "door", "apt%d_%d" % [b["id"], 2 * f + 2])
		else:
			_apartment(b, f, left[0], left[1], 2 * f + 1, true)
			_wall(b, f, lw, "door", "apt%d_%d" % [b["id"], 2 * f + 1])
			_apartment(b, f, right[0], right[1], 2 * f + 2, false)
			_wall(b, f, rw, "door", "apt%d_%d" % [b["id"], 2 * f + 2])
	elif kind == "office":
		if ground:
			var lob := _add_room(b, f, left[0], left[1], "lobby", "office")
			_furn("guarddesk", Vector2((left[0] + 3) * K.T, K.floor_y(0)))
			_furn("turnstile", Vector2((left[1] - 1) * K.T, K.floor_y(0)))
			lob["spots"].append({"x": (left[0] + 3) * K.T + 4, "kind": "guard"})
			_wall(b, f, lw, "doorway")
			var sec := _add_room(b, f, right[0], right[1], "security", "office", 0, true)
			var con := _furn("console", Vector2((right[0] + 3) * K.T, K.floor_y(0)))
			_obj({"kind": "console", "node": con, "x": (right[0] + 3) * K.T, "y": K.floor_y(0), "bid": b["id"], "f": 0, "inside": true})
			sec["spots"].append({"x": (right[0] + 2) * K.T, "kind": "sit"})
			_furn("chair", Vector2((right[0] + 2) * K.T, K.floor_y(0)))
			_wall(b, f, rw, "metal", "sec%d" % b["id"])
			_fusebox(b, f, (right[1]) * K.T)
		else:
			for side in [left, right]:
				var o := _add_room(b, f, side[0], side[1], "office", "office", 0, true)
				var c := int(side[0]) + 1
				while c + 2 <= int(side[1]):
					_furn("desk", Vector2((c + 1) * K.T, K.floor_y(f)))
					_furn("chair", Vector2((c + 1) * K.T + 12, K.floor_y(f)))
					o["spots"].append({"x": (c + 1) * K.T + 12, "kind": "desk"})
					c += 4
				_furn("filing", Vector2(int(side[1]) * K.T, K.floor_y(f)))
				if rng.randf() < 0.5:
					_furn("cooler", Vector2(int(side[0]) * K.T + 6, K.floor_y(f)))
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


func _stairs_sprite(b: Dictionary, f: int) -> void:
	var x := float(int(b["sw0"]) * K.T + 32)
	if f < int(b["n"]) - 1:
		_furn("stairs", Vector2(x, K.floor_y(f)))
	# лампочка на клетке
	_lamp_in(b, f, Vector2(x, K.floor_y(f) - 58), 56.0, Color(1.0, 0.9, 0.7))


func _apartment(b: Dictionary, f: int, c0: int, c1: int, apt: int, left: bool) -> void:
	## Квартира: кухня у клетки и комната у наружной стены. Иногда лаз в перегородке.
	var wdt := c1 - c0 + 1
	var kw := maxi(3, wdt / 2 - 1)
	var kc0: int
	var kc1: int
	var rc0: int
	var rc1: int
	var wall: int
	if left:
		rc0 = c0
		rc1 = c1 - kw - 1
		wall = rc1 + 1
		kc0 = wall + 1
		kc1 = c1
	else:
		kc0 = c0
		kc1 = c0 + kw - 1
		wall = kc1 + 1
		rc0 = wall + 1
		rc1 = c1
	var wp: String = WALLPAPERS[rng.randi() % WALLPAPERS.size()]
	var k := _add_room(b, f, kc0, kc1, "kitchen", "kitchen", apt)
	var r := _add_room(b, f, rc0, rc1, "living", wp, apt)
	_wall(b, f, wall, "vent" if rng.randf() < 0.18 else "doorway")
	var y := K.floor_y(f)
	# кухня
	var kx0 := float(kc0 * K.T)
	var kx1 := float((kc1 + 1) * K.T)
	if left:
		_furn("stove", Vector2(kx1 - 14, y)); _furn("sink", Vector2(kx1 - 38, y)); _furn("fridge", Vector2(kx0 + 12, y))
		k["spots"].append({"x": kx1 - 14, "kind": "stove"})
	else:
		_furn("stove", Vector2(kx0 + 14, y)); _furn("sink", Vector2(kx0 + 38, y)); _furn("fridge", Vector2(kx1 - 12, y))
		k["spots"].append({"x": kx0 + 14, "kind": "stove"})
	_furn("cabinet", Vector2((kx0 + kx1) / 2.0, y - 34))
	_furn("table", Vector2((kx0 + kx1) / 2.0 + (8 if left else -8), y))
	k["spots"].append({"x": (kx0 + kx1) / 2.0, "kind": "sit"})
	_movable("chair", (kx0 + kx1) / 2.0 + (24 if left else -24), b, f)
	# комната
	var rx0 := float(rc0 * K.T)
	var rx1 := float((rc1 + 1) * K.T)
	var mid := (rx0 + rx1) / 2.0
	var outer := rx0 if left else rx1
	var dirn := 1.0 if left else -1.0
	_furn("carpet", Vector2(mid, y - 18))
	_furn("sofa", Vector2(mid, y))
	r["spots"].append({"x": mid, "kind": "sofa"})
	if rx1 - rx0 > 96:
		_furn("tv", Vector2(mid + dirn * -34, y))
	var cl := _furn("closet", Vector2(outer + dirn * 18, y))
	_obj({"kind": "closet", "node": cl, "x": outer + dirn * 18, "y": y, "bid": b["id"], "f": f, "inside": true, "full": false, "apt": apt})
	if rx1 - rx0 > 120:
		_furn("bed", Vector2(outer + dirn * 64, y))
		r["spots"].append({"x": outer + dirn * 64, "kind": "bed"})
	_furn("radiator", Vector2(outer + dirn * 44, y - 10))
	b["floors"][f] = b["floors"].get(f, [])
	(b["floors"][f] as Array).append(apt)


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
			hall["name"] = "Кафе"
		"pharmacy":
			var hall := _add_room(b, f, c0, c1 - 4, "pharmacy", "shop")
			_furn("counter", Vector2((c1 - 6) * K.T, y))
			_furn("shelf", Vector2((c1 - 5) * K.T + 6, y - 22))
			hall["spots"].append({"x": (c1 - 5) * K.T + 4, "kind": "cashier"})
			hall["spots"].append({"x": (c0 + 3) * K.T, "kind": "shop"})
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
	_furn("pipes_wall", Vector2((x0 + 4) * K.T, y - 40))
	_furn("pipes_wall", Vector2((x0 + 8) * K.T, y - 40))
	_furn("boiler", Vector2((x0 + w - 5) * K.T, y))
	_furn("crate", Vector2((x0 + 3) * K.T, y))
	_fusebox(b, -1, (x0 + 2) * K.T)
	_lamp_in(b, -1, Vector2((x0 + w / 2) * K.T, y - 56), 90.0, Color(1.0, 0.85, 0.6), "bulb")
	var lb := _furn("lockbox", Vector2((x0 + w - 3) * K.T, y))
	_obj({"kind": "lockbox", "node": lb, "x": (x0 + w - 3) * K.T, "y": y, "bid": b["id"], "f": -1, "inside": true, "open": false, "item": "key"})
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
		var lc: int = int(b["sw1"]) + 3
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
				var on_stair: bool = lc + 1 >= int(b["sw0"]) and lc <= int(b["sw1"])
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
	if b["kind"] == "res":
		_sprop("antenna", Vector2(px0 + 30, top))
		_sprop("vent_roof", Vector2(px1 - 40, top))
		if rng.randf() < 0.5:
			_sprop("antenna", Vector2(px1 - 80, top))
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
		s.region_rect = Rect2(a.x * K.T, a.y * K.T, K.T, K.T)
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
		"square":
			for c in range(c0, c1 + 1):
				setc(tm_common, c, K.GY, "gravel", Res.ALT_COMMON)
			_sprop("monument", Vector2(mid, gy))
			_sprop("tree", Vector2(x0 + 26, gy))
			_sprop("tree", Vector2(x1 - 26, gy))
			_sprop("bench", Vector2(mid - 50, gy))
			_sprop("bench", Vector2(mid + 50, gy))
			var k := _sprop("kiosk", Vector2(x0 + 70, gy))
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
			var d := _sprop("dumpster", Vector2(mid + 10, gy))
			_obj({"kind": "dumpster", "node": d, "x": mid + 10, "y": gy, "inside": false, "full": false, "name": "на задворках"})
			_sprop("urn", Vector2(x0 + 14, gy))
			places["Задворки"] = {"area": "S", "x": mid - 14, "name": "Задворки"}
			_lamp_out(Vector2(mid, gy - 46), 70.0, "walllamp")
			_manhole(x1 - 22)
		"lane":
			if rng.randf() < 0.5:
				_sprop("fence_wood", Vector2(mid, gy))
	# мостки между крышами через узкие переулки
	if kind in ["lane", "backlane"]:
		var bl := _building_at(x0 - 4)
		var br := _building_at(x1 + 4)
		if not bl.is_empty() and not br.is_empty():
			var yl := float(int(bl["roof_r"]) * K.T)
			var yr := float(int(br["roof_r"]) * K.T)
			if absf(yl - yr) < 2.0:
				_platform_vis(Rect2(x0 - 8, yl, x1 - x0 + 16, 4))


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
	portals.append({"kind": "manhole", "x": x, "a": "S", "b": "C", "ya": gy, "yb": float((K.GY + 11) * K.T), "human": true, "spirit": true, "lock": "", "dur": 1.6})


# ======================= подземелье =======================

func _underground() -> void:
	# коллектор
	carve(coll_c0, coll_c1, K.GY + 8, K.GY + 10)
	for c in range(coll_c0, coll_c1 + 1):
		setc(tm_common, c, K.GY + 7, "tunnel_brick", Res.ALT_COMMON)
		setc(tm_common, c, K.GY + 11, "tunnel_brick", Res.ALT_COMMON)
		for r in range(K.GY + 8, K.GY + 11):
			setc(tm_back, c, r, "tunnel_back", Res.ALT_NONE)
	var cr := _add_room({"id": -1, "rooms": []}, -2, coll_c0, coll_c1, "collector", "tunnel_back", 0, false, false)
	cr["y"] = float((K.GY + 11) * K.T)
	var x := float(coll_c0 * K.T) + 60
	while x < float(coll_c1 * K.T):
		var l := _lamp_in({"id": -1}, -2, Vector2(x, float((K.GY + 8) * K.T) + 4), 70.0, Color(0.9, 0.85, 0.6), "bulb")
		l["inside_area"] = "C"
		x += 260.0
	# станция метро
	carve(metro_c0, metro_c1, K.GY + 13, K.GY + 18)
	for c in range(metro_c0, metro_c1 + 1):
		setc(tm_common, c, K.GY + 19, "platform", Res.ALT_COMMON)
		setc(tm_common, c, K.GY + 12, "wall_granite", Res.ALT_COMMON)
		for r in range(K.GY + 13, K.GY + 19):
			setc(tm_back, c, r, "marble", Res.ALT_NONE)
	var mr := _add_room({"id": -1, "rooms": []}, -3, metro_c0, metro_c1, "platform", "marble", 0, false, false)
	mr["y"] = float((K.GY + 19) * K.T)
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
	# шахты из подвалов в коллектор
	for b in buildings:
		if b["basement"]:
			var sx := float((int(b["x0"]) + 2) * K.T)
			carve(int(b["x0"]) + 1, int(b["x0"]) + 2, K.GY + 6, K.GY + 7)
			for r in range(K.GY + 6, K.GY + 8):
				setc(tm_back, int(b["x0"]) + 1, r, "tunnel_back", Res.ALT_NONE)
				setc(tm_back, int(b["x0"]) + 2, r, "tunnel_back", Res.ALT_NONE)
				setc(tm_inner, int(b["x0"]) + 1, r, "vent", Res.ALT_GRATE)
				setc(tm_inner, int(b["x0"]) + 2, r, "vent", Res.ALT_GRATE)
			portals.append({"kind": "shaft", "x": sx, "a": "B%dF-1" % b["id"], "b": "C", "ya": K.floor_y(-1), "yb": float((K.GY + 11) * K.T),
				"human": true, "spirit": true, "lock": "", "dur": 1.4})


# ======================= улица =======================

func _street() -> void:
	var gy := K.floor_y(0)
	# фонари вдоль тротуара
	var x := 120.0
	while x < float(width * K.T) - 60:
		var b := _building_at(x)
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
	# урны и гидранты
	for i in 8:
		var ux := rng.randf_range(100, float(width * K.T) - 100)
		var u := _sprop("urn", Vector2(ux, gy))
		_obj({"kind": "movable", "what": "urn", "node": u, "x": ux, "y": gy, "inside": false, "fallen": false})
	# светофор у метро
	_sprop("trafficlight", Vector2(float(mb["px0"]) - 12, gy))
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
		if rm["kind"] in ["stair", "collector", "platform", "basement"]:
			continue
		var cx := (float(rm["x0"]) + float(rm["x1"])) / 2.0
		var y := float(rm["y"])
		var wdt := float(rm["x1"]) - float(rm["x0"])
		var b := {"id": rm["bid"]}
		var col := Color(1.0, 0.86, 0.62)
		if rm["kind"] in ["office", "store", "pharmacy", "security", "lobby", "metro"]:
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


func _areas_and_portals() -> void:
	var gy := K.floor_y(0)
	areas["S"] = {"id": "S", "inside": false, "bid": -1, "f": 0, "y": gy, "x0": 24.0, "x1": float(width * K.T) - 24.0}
	areas["C"] = {"id": "C", "inside": true, "bid": -1, "f": -2, "y": float((K.GY + 11) * K.T), "x0": float(coll_c0 * K.T) + 8, "x1": float((coll_c1 + 1) * K.T) - 8}
	areas["M"] = {"id": "M", "inside": true, "bid": -1, "f": -3, "y": float((K.GY + 19) * K.T), "x0": float(metro_c0 * K.T) + 8, "x1": float((metro_c1 + 1) * K.T) - 8}
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
		# лестницы
		for f in fl:
			if f + 1 < int(b["n"]):
				portals.append({"kind": "stairs", "x": sx, "a": area_of_floor(bid, f), "b": area_of_floor(bid, f + 1),
					"ya": K.floor_y(f), "yb": K.floor_y(f + 1), "human": true, "spirit": true, "lock": "", "dur": 1.3})
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
		# служебный выход «Гранита» на задворки
		if b["name"] == "Гранит":
			var bx := float(b["px1"]) - 24
			portals.append({"kind": "backdoor", "x": bx, "a": "S", "b": area_of_floor(bid, 0), "ya": gy, "yb": gy,
				"human": true, "spirit": true, "lock": "sec%d" % bid, "dur": 0.6})
			_sprop("door_metal", Vector2(float(b["px1"]) - 8, gy), false, b["fp"])
		if b["kind"] == "metro":
			portals.append({"kind": "escalator", "x": float(b["px1"]) - 70, "a": area_of_floor(bid, 0), "b": "M",
				"ya": gy, "yb": float((K.GY + 19) * K.T), "human": true, "spirit": true, "lock": "", "dur": 2.6})
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
	if pos.y > float((K.GY + 12) * K.T):
		return "M"
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
