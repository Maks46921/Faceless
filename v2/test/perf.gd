extends Node
## Кадры в секунду на обычной скорости: -- --perf [сид] [секунд]

func _ready() -> void:
	var args: Array = get_meta("args")
	var seed_v := 1000 if args.size() < 2 else int(args[1])
	var secs := 12.0 if args.size() < 3 else float(args[2])
	var main := get_parent()
	Game.hints_seen = {"start": true, "spirit": true, "tails": true}
	var w: Node = load("res://src/world.gd").new()
	w.main = main
	w.case_seed = seed_v
	main.add_child(w)
	main.current = w
	for i in 30:
		await get_tree().process_frame
	var bench := {
		"brains": func(): for p in w.people: p.brain.tick(0.016),
		"perceive": func(): w._perceive(0.2),
		"lamps": func(): w._lamps(false),
		"dormancy": func(): w._dormancy(),
		"doors": func(): w._doors(0.016),
		"player": func(): w.player._process(0.016),
		"hud": func(): w.hud._process(0.016),
		"view": func(): w.view._process(0.016),
	}
	for k in bench:
		var u0 := Time.get_ticks_usec()
		for i in 10:
			(bench[k] as Callable).call()
		print("  %s: %.2f ms" % [k, (Time.get_ticks_usec() - u0) / 10000.0])
	var phases := [["все", func(): pass], ["без дальнего плана", func(): w.view.far.visible = false],
		["без hud", func(): w.hud.d.visible = false], ["без людей", func(): w.city.people.visible = false],
		["без мебели", func(): w.city.furn.visible = false; for k in w.city.sections: w.city.sections[k]["node"].visible = false]]
	for ph in phases:
		(ph[1] as Callable).call()
		var f0 := Engine.get_process_frames()
		var m0 := Time.get_ticks_msec()
		while Time.get_ticks_msec() - m0 < 2500:
			await get_tree().process_frame
		print("  %s: %.1f fps" % [ph[0], (Engine.get_process_frames() - f0) / 2.5])
	var tp := 0.0
	var tph := 0.0
	var t0 := Time.get_ticks_msec()
	var frames := 0
	var worst := 0.0
	var last := t0
	while Time.get_ticks_msec() - t0 < secs * 1000.0:
		await get_tree().process_frame
		var now := Time.get_ticks_msec()
		worst = maxf(worst, float(now - last))
		last = now
		frames += 1
		tp += Performance.get_monitor(Performance.TIME_PROCESS)
		tph += Performance.get_monitor(Performance.TIME_PHYSICS_PROCESS)
	var dn := 0
	for p in w.people:
		if p.dormant:
			dn += 1
	print("process %.1f ms, physics %.1f ms per frame" % [tp / frames * 1000.0, tph / frames * 1000.0])
	print("PERF people %d dormant %d: %.1f fps, worst frame %d ms" % [w.people.size(), dn, frames / secs, int(worst)])
	get_tree().quit()
