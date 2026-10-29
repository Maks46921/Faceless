extends Node
## Прогон дела без игрока: -- --play [seed] [секунд] [час]

var w: Node


func _ready() -> void:
	var args: Array = get_meta("args")
	var seed_v := 4242 if args.size() < 2 else int(args[1])
	var secs := 8.0 if args.size() < 3 else float(args[2])
	var main := get_parent()
	w = load("res://src/world.gd").new()
	w.main = main
	w.case_seed = seed_v
	if args.size() > 3:
		w.start_h = float(args[3])
	main.add_child(w)
	if args.size() > 4 and args[4] == "spirit":
		await get_tree().process_frame
		w.player.leave(true)
	var dir := "user://shots/"
	DirAccess.make_dir_recursive_absolute(dir)
	var t0 := Time.get_ticks_msec()
	var frames := 0
	var shot_i := 0
	while (Time.get_ticks_msec() - t0) / 1000.0 < secs:
		await get_tree().process_frame
		frames += 1
		if frames % 120 == 60:
			get_viewport().get_texture().get_image().save_png(dir + "play_%02d.png" % shot_i)
			shot_i += 1
	print("frames ", frames, " fps ", frames / secs, " hour ", w.env.hour, " people ", w.people.size(), " host ", w.player.host.full_name() if w.player.host else "spirit")
	print("memory ", w.case.memory(), " susp ", w.susp)
	get_tree().quit()
