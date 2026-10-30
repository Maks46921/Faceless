extends Node
## Гиперплотный район без людей: время сборки, число узлов, снимки на разных высотах.
## -- --towers [сид] [час]

func _ready() -> void:
	var args: Array = get_meta("args")
	var seed_v := 1234 if args.size() < 2 else int(args[1])
	var hour := 11.0 if args.size() < 3 else float(args[2])
	var t0 := Time.get_ticks_msec()
	var city := City.new()
	city.build(seed_v)
	city.room_lamps()
	var t1 := Time.get_ticks_msec()
	var env := Env.new()
	add_child(env)
	env.setup(5, hour, 70.0)
	env.weather_plan = [[0.0, "clear"]]
	env.tick(0.0)
	var cl := CanvasLayer.new()
	add_child(cl)
	var view := View.new()
	cl.add_child(view)
	view.setup(city, env)
	view.size = Vector2(1920, 1080)
	var nodes := 0
	for k in city.sections:
		nodes += (city.sections[k]["node"] as Node).get_child_count()
	print("build %d ms; width %d; buildings %d; rooms %d; portals %d; areas %d; galleries %d; sections %d (%d nodes); lamps %d" % [
		t1 - t0, city.width, city.buildings.size(), city.rooms.size(), city.portals.size(), city.areas.size(), city.galleries.size(),
		city.sections.size(), nodes, city.lamps.size()])
	for b in city.buildings:
		print("  ", b["id"], " ", b["name"], " ", b["kind"], " n=", b["n"], " w=", b["w"], " gal_l=", b["gal_l"], " gal_r=", b["gal_r"])
	var r0 := Time.get_ticks_msec()
	var rt: Array = city.route("S", city.area_of_floor(0, 37))
	print("route S -> B0F37: %d steps, %d ms: %s" % [rt.size(), Time.get_ticks_msec() - r0, str(rt.map(func(e): return e["p"]["kind"]))])
	var dir := "user://shots/"
	DirAccess.make_dir_recursive_absolute(dir)
	var spots := []
	var modes := []
	var ta: Dictionary = {}
	for b in city.buildings:
		if b["tower"] == "А":
			ta = b
	var g: Dictionary = city.galleries[0] if city.galleries.size() > 0 else {}
	for gg in city.galleries:
		if int(gg["a"]) == int(ta["id"]):
			g = gg
			break
	var gx := (float(g["x0"]) + float(g["x1"])) / 2.0
	var tx := (float(ta["px0"]) + float(ta["px1"])) / 2.0
	spots.append(Vector2(gx, K.floor_y(0) - 120)); modes.append("out")
	spots.append(Vector2(gx, K.floor_y(int(g["f"])) - 40)); modes.append("out")
	spots.append(Vector2(gx, K.floor_y(30) - 40)); modes.append("out")
	spots.append(Vector2(tx, K.floor_y(10) - 40)); modes.append("in")
	spots.append(Vector2(tx, K.floor_y(43) - 40)); modes.append("in")
	spots.append(Vector2(gx, K.floor_y(55) - 40)); modes.append("out")
	spots.append(Vector2(tx, K.floor_y(60) - 100)); modes.append("out")
	var i := 0
	for p in spots:
		view.snap_to(p)
		view.viewer_inside = modes[i] == "in"
		view.viewer_bid = city.building_at(p.x).get("id", -1)
		view.viewer_under = false
		city.show_sections(Rect2(p - Vector2(K.VIEW_W, K.VIEW_H) / 2.0, Vector2(K.VIEW_W, K.VIEW_H)))
		for k in 30:
			await get_tree().process_frame
		var img := get_viewport().get_texture().get_image()
		img.save_png(dir + "towers_%02d.png" % i)
		i += 1
	print("shots saved")
	get_tree().quit()
