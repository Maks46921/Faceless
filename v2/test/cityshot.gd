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
	var spots := [Vector2(300, 1250), Vector2(1100, 1200), Vector2(1700, 1260), Vector2(2400, 1150), Vector2(3100, 1250), Vector2(1700, 1450), Vector2(2560, 1550), Vector2(900, 900)]
	var i := 0
	for p in spots:
		view.snap_to(p)
		view.viewer_inside = i == 5 or i == 7
		view.viewer_bid = city.building_at(p.x).get("id", -1)
		view.viewer_under = i == 6
		for k in 40:
			await get_tree().process_frame
		var img := get_viewport().get_texture().get_image()
		img.save_png(dir + "city_%d_%02d.png" % [int(hour), i])
		i += 1
	print("shots saved ", ProjectSettings.globalize_path(dir))
	get_tree().quit()
