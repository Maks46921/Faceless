extends Node
## Проверка механик по шагам со снимками: -- --mech [seed]

var w: Node
var main: Node
var dir := "user://shots/"
var n := 0


func shot(nm: String) -> void:
	await get_tree().process_frame
	await get_tree().process_frame
	get_viewport().get_texture().get_image().save_png(dir + "mech_%02d_%s.png" % [n, nm])
	n += 1


func wait(s: float) -> void:
	var t0 := Time.get_ticks_msec()
	while (Time.get_ticks_msec() - t0) / 1000.0 < s:
		await get_tree().process_frame


func _ready() -> void:
	DirAccess.make_dir_recursive_absolute(dir)
	var args: Array = get_meta("args")
	var seed_v := 4242 if args.size() < 2 else int(args[1])
	main = get_parent()
	# меню
	main.show_menu()
	await wait(1.0)
	await shot("menu")
	# папка
	main.show_brief(seed_v)
	w = main.current
	await wait(0.6)
	await shot("brief")
	w.hud._close_brief()
	await wait(1.0)
	var pl: PlayerCtl = w.player
	var cs: Case = w.case
	print("start host ", pl.host.full_name(), " area ", pl.host.area, " target home ", cs.p["home_bid"], " apt ", cs.p["apt"])
	# выйти из тела
	pl.leave(true)
	await wait(1.5)
	print("spirit area ", pl.spirit.area, " density ", pl.density, " hurt ", pl.hurt_why)
	await shot("spirit")
	# клешня: оглушить ближайшего
	var near: Person = pl._nearest_body(pl.spirit.center(), 400.0)
	print("near ", near.full_name() if near else "none")
	if near:
		pl.spirit.global_position = near.center() + Vector2(-30, -10)
		await wait(0.2)
		pl.claw = 3
		pl._claw_person(near, "stun", pl._claw_cost(3))
		print("stunned state ", near.state, " memory ", cs.memory())
		pl.claw = -1
	await wait(1.0)
	await shot("stun")
	# войти в другого
	var other: Person = null
	for p in w.people:
		if p.state == "ok" and p != cs.target and not p.inside and p != near:
			other = p
			break
	pl.spirit.global_position = other.center()
	pl._try_enter(other)
	await wait(0.6)
	print("host now ", pl.host.full_name() if pl.host else "none", " memory ", cs.memory())
	# доска и карта
	w.hud.board = true
	await shot("board")
	w.hud.board = false
	w.hud.map = true
	await shot("map")
	w.hud.map = false
	# телепорт к цели и задушить
	var t: Person = cs.target
	print("target at ", t.area, " ", t.global_position)
	pl.host.global_position = t.global_position + Vector2(-12, 0)
	pl.host.area = t.area
	pl.host.set_inside(t.inside)
	pl.host.facing = 1
	await wait(0.3)
	pl._body_prompts()
	print("act_q ", pl.act_q.get("text", "-"), " who ", pl.act_q.get("who").full_name() if pl.act_q.has("who") else "-")
	if pl.act_q.has("who"):
		Input.parse_input_event(_key(KEY_Q, true))
		await get_tree().process_frame
		pl._hands(pl.act_q)
		var t0 := 0.0
		while not cs.target_dead and t0 < 1.0:
			Input.parse_input_event(_key(KEY_Q, true))
			await get_tree().process_frame
			t0 += get_process_delta_time()

		print("strangle progress after 1s: ", pl.strangle.get("t", -1))
		w.susp = 0.0
		if not cs.target_dead:
			pl.strangle = {}
			w.kill(t, "hands", pl.host)
		Input.parse_input_event(_key(KEY_Q, false))
	print("target dead ", cs.target_dead, " how ", cs.dead_how, " tails ", cs.open_tails().map(func(x): return x["id"]))
	print("before shot kill")
	await shot("kill")
	print("after shot kill")
	# поднять тело и спрятать
	print("prompts after kill")
	pl._body_prompts()
	print("act_g ", pl.act_g)
	if pl.act_g.get("kind", "") == "pick":
		pl._pick(pl.act_g["who"])
		print("carrying ", pl.host.carrying != null)
		await wait(0.5)
		await shot("carry")
	print("before exit")
	print("exit ring ", w.exit_ring.get("phone", {}).get("name", "-"), " h0 ", w.exit_ring.get("h0", 0), " now ", w.env.hour)
	# снять трубку
	if not w.exit_ring.is_empty():
		var ph: Dictionary = w.exit_ring["phone"]
		w.env.hour = float(w.exit_ring["h0"]) + 0.01
		await wait(0.3)
		print("ringing ", ph["ring"])
		w.answer_phone(ph)
	await wait(1.0)
	await shot("end")
	await wait(2.5)
	await shot("result")
	print("result ", Game.last_result)
	get_tree().quit()


func _key(k: Key, down: bool) -> InputEventKey:
	var e := InputEventKey.new()
	e.physical_keycode = k
	e.keycode = k
	e.pressed = down
	return e
