extends Node
## Разговоры, лифт, лестница, мостик, подземка: -- --talk [seed]

var w: Node
var main: Node
var dir := "user://shots/"
var n := 0


func shot(nm: String) -> void:
	await get_tree().process_frame
	await get_tree().process_frame
	get_viewport().get_texture().get_image().save_png(dir + "talk_%02d_%s.png" % [n, nm])
	n += 1


func wait(s: float) -> void:
	var t0 := Time.get_ticks_msec()
	while (Time.get_ticks_msec() - t0) / 1000.0 < s:
		await get_tree().process_frame


func key(k: Key, down: bool) -> void:
	var e := InputEventKey.new()
	e.physical_keycode = k
	e.keycode = k
	e.pressed = down
	Input.parse_input_event(e)


func put(p: Person, area: String, x: float) -> void:
	var a: Dictionary = w.city.areas[area]
	p.area = area
	p.set_inside(a["inside"])
	p.global_position = Vector2(x, float(a["y"]) - 1)
	p.velocity = Vector2.ZERO


func find(prof: String) -> Person:
	for p in w.people:
		if p.prof == prof and p.state == "ok" and not p.host and p != w.case.target:
			return p
	return null


func talk_with(q: Person, picks: Array, nm: String) -> void:
	var pl: PlayerCtl = w.player
	put(q, pl.host.area, pl.host.global_position.x + 28)
	q.brain.react = {}
	await wait(0.3)
	pl._talk(q)
	var tk: Talk = w.hud.talk
	print("== ", q.prof, " ", q.full_name(), " traits=", tk.trait_words(), " rel=", tk.rel, " mood=", int(tk.mood()), " pat=", tk.patience())
	print("   > ", tk.line, "  opts=", tk.opts.map(func(o): return o["text"]))
	await wait(0.4)
	await shot(nm)
	for i in picks:
		if w.hud.talk == null:
			break
		var t := w.hud.talk as Talk
		if i >= t.opts.size():
			continue
		var txt: String = t.opts[i]["text"]
		t.choose(i)
		print("   [", txt, "] -> ", t.line, "  mood=", int(t.mood()), " pat=", t.patience())
		await wait(0.2)
	await shot(nm + "_after")
	if w.hud.talk:
		w.hud.close_talk()
	await wait(0.3)


func _ready() -> void:
	DirAccess.make_dir_recursive_absolute(dir)
	var args: Array = get_meta("args")
	var seed_v := 4242 if args.size() < 2 else int(args[1])
	main = get_parent()
	Game.hints_seen = {"start": true, "spirit": true, "tails": true}
	main.show_brief(seed_v)
	w = main.current
	await wait(0.5)
	w.hud._close_brief()
	await wait(0.5)
	var pl: PlayerCtl = w.player
	var h := pl.host
	print("rumours ", w.rumours.size(), ": ", w.rumours.map(func(r): return r[0]))
	# разговоры
	put(h, "S", float(w.city.places["Сквер"]["x"]))
	await wait(0.5)
	var pens := find("pensioner")
	await talk_with(pens, [0, 1, 2, 4, 6, 6], "pensioner")
	var guard := find("guard")
	await talk_with(guard, [0, 5, 6, 1], "guard")
	var tramp := find("tramp")
	await talk_with(tramp, [0, 5, 6, 6, 2], "tramp")
	var cash := find("cashier")
	await talk_with(cash, [3], "dirs")
	print("keys now ", h.keys)
	# лифт: держим W — едем этаж за этажом
	var lb: Dictionary = {}
	for b in w.city.buildings:
		if b["lift"] and not b["lift_broken"]:
			lb = b
			break
	if not lb.is_empty():
		put(h, w.city.area_of_floor(int(lb["id"]), 0), float(lb["lift_x"]) + 4)
		await wait(0.6)
		print("lift prompt W: ", pl.act_w.get("text", "-"))
		key(KEY_W, true)
		await wait(5.0)
		key(KEY_W, false)
		while h.state == "transit":
			await get_tree().process_frame
		await wait(0.3)
		print("after lift hold: area ", h.area, " y ", int(h.global_position.y))
		await shot("lift")
		# лестница вниз, держим S
		put(h, h.area, float(lb["stair_x"]))
		await wait(0.5)
		print("stairs prompt S: ", pl.act_s.get("text", "-"))
		key(KEY_S, true)
		await wait(3.5)
		key(KEY_S, false)
		while h.state == "transit":
			await get_tree().process_frame
		await wait(0.3)
		print("after stairs hold: area ", h.area)
		await shot("stairs")
	# мостик
	for pt in w.city.portals:
		if pt["kind"] == "bridge":
			var a: String = pt["a"]
			put(h, a, City.px_from(pt, 1) + 6)
			await wait(0.6)
			print("bridge prompt E: ", pl.act_e.get("text", "-"))
			await shot("bridge_before")
			if pl.act_e.get("kind", "") == "portal":
				pl._do(pl.act_e)
			await wait(4.0)
			print("after bridge: area ", h.area, " (expected ", pt["b"], ")")
			await shot("bridge_after")
			break
	# подземка: коллектор -> дренаж по скобам
	for pt in w.city.portals:
		if pt["kind"] == "ladder":
			put(h, "C", float(pt["x"]) + 2)
			await wait(0.6)
			print("ladder prompt S: ", pl.act_s.get("text", "-"))
			if pl.act_s.get("kind", "") == "portal":
				pl._do(pl.act_s)
			await wait(3.0)
			print("after ladder: area ", h.area)
			await shot("drain")
			break
	print("done")
	get_tree().quit()
