extends Node
## Клик мышью по кнопкам меню через настоящий ввод окна.

func _ready() -> void:
	var main := get_parent()
	main.show_menu()
	await get_tree().create_timer(1.0).timeout
	var win := get_window()
	print("win size ", win.size, " vis ", get_viewport().get_visible_rect())
	var m: Control = main.current
	print("menu rect ", m.get_global_rect(), " filter ", m.mouse_filter)
	# кнопка «Служба» в координатах 1920x1080 -> окно
	for target in [Vector2(400, 430 + 2 * 84 + 30), Vector2(1000, 520), Vector2(400, 430 + 30), Vector2(960, 540)]:
		var sc := Vector2(win.size) / Vector2(1920, 1080)
		var p: Vector2 = target * sc
		var mv := InputEventMouseMotion.new(); mv.position = p; mv.global_position = p
		Input.parse_input_event(mv)
		await get_tree().process_frame
		for pr in [true, false]:
			var e := InputEventMouseButton.new()
			e.button_index = MOUSE_BUTTON_LEFT; e.pressed = pr; e.position = p; e.global_position = p
			Input.parse_input_event(e)
			await get_tree().process_frame
		await get_tree().create_timer(0.5).timeout
		print("after click at ", target, ": current=", main.current.get_script().resource_path, " panel=", main.current.get("panel"), " diff=", Game.difficulty, " paused=", get_tree().paused)
	var hud = main.current.hud
	var br: Rect2 = hud.brief_btn
	print("brief_btn ", br)
	await _click(br.get_center())
	print("mouse local ", hud.d.get_local_mouse_position(), " vp ", get_viewport().get_mouse_position())
	print("after brief click paused=", get_tree().paused, " brief=", hud.brief)
	get_tree().quit()


func _click(target: Vector2) -> void:
	var win := get_window()
	var p: Vector2 = target * Vector2(win.size) / Vector2(1920, 1080)
	var mv := InputEventMouseMotion.new(); mv.position = p; mv.global_position = p
	Input.parse_input_event(mv)
	await get_tree().process_frame
	for pr in [true, false]:
		var e := InputEventMouseButton.new()
		e.button_index = MOUSE_BUTTON_LEFT; e.pressed = pr; e.position = p; e.global_position = p
		Input.parse_input_event(e)
		await get_tree().process_frame
