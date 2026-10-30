extends Node
## Проверка управления клавишами: -- --input [seed]

var w: Node


func key(k: Key, down: bool) -> void:
	var e := InputEventKey.new()
	e.physical_keycode = k
	e.keycode = k
	e.pressed = down
	Input.parse_input_event(e)


func tap(k: Key) -> void:
	key(k, true)
	await get_tree().process_frame
	await get_tree().process_frame
	key(k, false)
	await get_tree().process_frame


func hold(k: Key, s: float) -> void:
	key(k, true)
	var t0 := Time.get_ticks_msec()
	while (Time.get_ticks_msec() - t0) / 1000.0 < s:
		await get_tree().process_frame
	key(k, false)
	await get_tree().process_frame


func wait(s: float) -> void:
	var t0 := Time.get_ticks_msec()
	while (Time.get_ticks_msec() - t0) / 1000.0 < s:
		await get_tree().process_frame


func shot(nm: String) -> void:
	await get_tree().process_frame
	get_viewport().get_texture().get_image().save_png("user://shots/input_%s.png" % nm)


func _ready() -> void:
	var args: Array = get_meta("args")
	var seed_v := 4242 if args.size() < 2 else int(args[1])
	var main := get_parent()
	w = load("res://src/world.gd").new()
	w.main = main
	w.case_seed = seed_v
	main.add_child(w)
	await wait(0.5)
	var pl: PlayerCtl = w.player
	var h: Person = pl.host
	var x0 := h.global_position.x
	await hold(KEY_D, 1.5)
	print("walk right: dx=", h.global_position.x - x0, " area ", h.area)
	# к ближайшему подъезду
	var best := {}
	for pt in w.city.portals:
		if pt["kind"] == "entrance" and pt["a"] == "S" and int(w.city.buildings[int(w.city.areas[pt["b"]]["bid"])]["n"]) > 3 and (best.is_empty() or absf(float(pt["x"]) - h.global_position.x) < absf(float(best["x"]) - h.global_position.x)):
			best = pt
	h.global_position.x = float(best["x"]) + 4
	await wait(0.3)
	print("prompts at entrance: ", pl.prompts)
	await tap(KEY_E)
	await wait(1.2)
	print("after E: area ", h.area, " inside ", h.inside, " state ", h.state)
	print("prompts inside: ", pl.prompts)
	await shot("inside")
	await tap(KEY_W)
	await wait(2.0)
	print("after W: area ", h.area, " y ", h.global_position.y)
	await shot("upstairs")
	# выйти из тела и полетать
	await tap(KEY_F)
	await wait(0.4)
	var s := pl.spirit
	var sp0 := s.global_position
	await hold(KEY_A, 1.0)
	print("spirit fly left: dx=", s.global_position.x - sp0.x, " area ", s.area, " density ", pl.density)
	await tap(KEY_S)
	await wait(1.0)
	print("spirit after S: area ", s.area)
	await tap(KEY_4)
	print("claw selected ", pl.claw)
	await shot("spirit")
	await tap(KEY_TAB)
	await wait(0.2)
	print("board ", w.hud.board)
	await tap(KEY_TAB)
	await tap(KEY_ESCAPE)
	await wait(0.2)
	print("paused ", get_tree().paused, " pause ", w.hud.pause)
	await shot("pause")
	await tap(KEY_ESCAPE)
	await wait(0.2)
	print("paused after esc ", get_tree().paused)
	await tap(KEY_F)
	await wait(0.6)
	print("host after F ", pl.host.full_name() if pl.host else "none")
	get_tree().quit()
