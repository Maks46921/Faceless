extends Node
## Прогон по многим сидам: -- --seeds [сколько] [первый сид] [сколько прогнать на ускорении] [игровых часов]
## 1) у каждой важной точки есть путь от улицы (цель, её дом и работа, таксофоны, улики, ящики, все точки расписаний);
## 2) точка не замурована в стену; 3) на ускорении никто не застревает надолго.
## Итог печатается строкой «SEEDS ok=… bad=…» и списком проблем.

var main: Node
var problems: Array = []


func wait_frames(n: int) -> void:
	for i in n:
		await get_tree().process_frame


func solid(city: City, pos: Vector2, inside: bool) -> bool:
	## Снаружи с людьми сталкивается только общий слой, внутри — ещё и внутренний.
	var layers: Array = [city.tm_common, city.tm_inner] if inside else [city.tm_common]
	for dy in [-10.0, -26.0]:
		var c := Vector2i(int(floor(pos.x / K.T)), int(floor((pos.y + dy) / K.T)))
		for tm in layers:
			if (tm as TileMapLayer).get_cell_source_id(c) == -1:
				continue
			var alt: int = (tm as TileMapLayer).get_cell_alternative_tile(c)
			if alt in [Res.ALT_PLATFORM, Res.ALT_GRATE]:
				continue
			return true
	return false


func check(seed_v: int, w: Node) -> int:
	var city: City = w.city
	var bad := 0
	var pts := []        # [что, зона, x, y]
	for pl in city.places:
		var p: Dictionary = city.places[pl]
		pts.append(["место " + pl, p["area"], float(p["x"]), -1.0])
	for o in city.objs:
		if o["kind"] in ["payphone", "clue", "lockbox"]:
			var area := city.area_at(Vector2(float(o["x"]), float(o.get("y", K.floor_y(0))) - 4), bool(o.get("inside", false)))
			pts.append([o["kind"], area, float(o["x"]), float(o.get("y", -1.0))])
	for p in w.people:
		for e in p.brain.sched:
			if e["act"] == "away":
				continue
			pts.append(["%s/%s %s" % [p.prof, p.first, e.get("name", e["act"])], e["area"], float(e["x"]), -1.0])
	for pt in pts:
		var area: String = pt[1]
		if area == "" or not city.areas.has(area):
			problems.append("%d: нет зоны у «%s» (%s)" % [seed_v, pt[0], area])
			bad += 1
			continue
		if area != "S" and city.route("S", area).is_empty():
			problems.append("%d: нет пути с улицы к «%s» (%s)" % [seed_v, pt[0], area])
			bad += 1
		var y: float = pt[3] if pt[3] > 0.0 else float(city.areas[area]["y"])
		if solid(city, Vector2(pt[2], y), bool(city.areas[area]["inside"])):
			problems.append("%d: «%s» в стене (%s, x=%d)" % [seed_v, pt[0], area, int(pt[2])])
			bad += 1
	return bad


func _ready() -> void:
	var args: Array = get_meta("args")
	var count := 40 if args.size() < 2 else int(args[1])
	var first := 1000 if args.size() < 3 else int(args[2])
	var sims := 3 if args.size() < 4 else int(args[3])
	var hours := 1.0 if args.size() < 5 else float(args[4])
	main = get_parent()
	Game.hints_seen = {"start": true, "spirit": true, "tails": true}
	var ok := 0
	var badn := 0
	for i in count:
		var seed_v := first + i * 7919
		var w: Node = load("res://src/world.gd").new()
		w.main = main
		w.case_seed = seed_v
		main.add_child(w)
		main.current = w
		await wait_frames(2)
		var b := check(seed_v, w)
		if i < sims:
			b += await run_sim(seed_v, w, hours)
		print("seed %d: buildings %d width %d people %d problems %d" % [seed_v, w.city.buildings.size(), w.city.width, w.people.size(), b])
		if b == 0:
			ok += 1
		else:
			badn += 1
		w.queue_free()
		await wait_frames(2)
	for pr in problems.slice(0, 60):
		print("  ", pr)
	print("SEEDS ok=%d bad=%d problems=%d" % [ok, badn, problems.size()])
	get_tree().quit()


func run_sim(seed_v: int, w: Node, hours: float) -> int:
	## Дух висит в воздухе, люди живут по расписанию на ускорении. Застрявший дольше 20 с — проблема.
	w.player.leave(true)
	Engine.time_scale = 8.0
	var h0: float = w.env.hour
	var last := {}
	var stuck := {}
	var reported := {}
	var bad := 0
	while w.env.hour < h0 + hours and not w.over:
		await get_tree().process_frame
		w.player.density = 100.0
		var dt := get_process_delta_time()
		for p in w.people:
			var k: Vector2 = p.global_position
			# спящий вдали идёт «по бумаге»: стоит на месте, пока не дойдёт; застрял — только если пути нет
			var frozen: bool = p.brain.paper.is_empty() if p.dormant else (last.has(p.pid) and (last[p.pid] as Vector2).distance_to(k) < 0.5)
			if frozen and p.brain and not p.brain.arrived \
					and p.state == "ok" and not p.brain.away and p.brain.react.is_empty():
				stuck[p.pid] = float(stuck.get(p.pid, 0.0)) + dt
			else:
				stuck[p.pid] = 0.0
			last[p.pid] = k
			if float(stuck[p.pid]) > 20.0 and not reported.has(p.pid):
				reported[p.pid] = true
				bad += 1
				problems.append("%d: застрял%s %s/%s в %s (%d,%d) → %s" % [seed_v, " (спит)" if p.dormant else "", p.prof, p.first, p.area, int(k.x), int(k.y), p.brain.goal.get("area", "?")])
	var dn := 0
	for p in w.people:
		if p.dormant:
			dn += 1
	print("  sim %d: %d people, %d dormant, fps %d" % [seed_v, w.people.size(), dn, Engine.get_frames_per_second()])
	Engine.time_scale = 1.0
	return bad
