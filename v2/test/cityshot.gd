extends Node
## Снимки района без людей: -- --cityshot [час]

func _ready() -> void:
	var args: Array = get_meta("args")
	var hour := 11.0 if args.size() < 2 else float(args[1])
	var city := City.new()
	city.build(1234)
	city.room_lamps()
	var env := Env.new()
	add_child(env)
	env.setup(5, hour, 70.0)
	env.weather_plan = [[0.0, "clear"]]
	if args.size() > 2:
		env.weather_plan = [[0.0, args[2]]]
		env.rain = 1.0 if args[2] == "rain" else 0.0
	env.tick(0.0)
	var cl := CanvasLayer.new()
	add_child(cl)
	var view := View.new()
	cl.add_child(view)
	view.setup(city, env)
	view.size = Vector2(1920, 1080)
	print("width tiles ", city.width, " buildings ", city.buildings.size(), " rooms ", city.rooms.size(), " portals ", city.portals.size())
	var on := env.lamps_on()
	for l in city.lamps:
		l["light"].visible = on or not l["outer"]
	var dir := "user://shots/"
	DirAccess.make_dir_recursive_absolute(dir)
	var gy := float(K.GY * K.T)
	var spots := []
	var modes := []
	for b in city.buildings:
		var cx := (float(b["x0"]) + float(b["w"]) / 2.0) * K.T
		spots.append(Vector2(cx, gy - 200)); modes.append("out")
	var b0: Dictionary = city.buildings[1]
	var bc := (float(b0["x0"]) + float(b0["w"]) / 2.0) * K.T
	for f in [1, 4, int(b0["n"]) - 1]:
		spots.append(Vector2(bc, K.floor_y(f) - 40)); modes.append("in")
	spots.append(Vector2(bc, K.floor_y(int(b0["n"])) - 300)); modes.append("out")
	for r in [City.C_ROW, City.M_ROW, City.D_ROW]:
		spots.append(Vector2(bc + 600, r * K.T - 60)); modes.append("under")
	var i := 0
	for p in spots:
		view.snap_to(p)
		view.viewer_inside = modes[i] == "in"
		view.viewer_bid = city.building_at(p.x).get("id", -1)
		view.viewer_under = modes[i] == "under"
		for k in 40:
			await get_tree().process_frame
		var img := get_viewport().get_texture().get_image()
		img.save_png(dir + "city_%d_%02d.png" % [int(hour), i])
		i += 1
	print("shots saved ", ProjectSettings.globalize_path(dir))
	get_tree().quit()
