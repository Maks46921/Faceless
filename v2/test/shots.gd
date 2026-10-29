extends Node
## Снимки для папки screens: -- --shots

var main: Node
var w: Node
var n := 0


func wait(s: float) -> void:
	var t0 := Time.get_ticks_msec()
	while (Time.get_ticks_msec() - t0) / 1000.0 < s:
		await get_tree().process_frame


func shot(nm: String) -> void:
	await get_tree().process_frame
	await get_tree().process_frame
	get_viewport().get_texture().get_image().save_png("user://shots/final_%02d_%s.png" % [n, nm])
	n += 1


func game(seed_v: int, h: float, weather: String = "") -> void:
	if w and is_instance_valid(w):
		w.queue_free()
		await get_tree().process_frame
	w = load("res://src/world.gd").new()
	w.main = main
	w.case_seed = seed_v
	w.start_h = h
	main.add_child(w)
	main.current = w
	if weather != "":
		w.env.weather_plan = [[0.0, weather]]
		w.env.rain = 1.0 if weather == "rain" else 0.0
		w.env.fog = 0.0
	await wait(0.5)


func _ready() -> void:
	main = get_parent()
	Game.hints_seen = {"start": true, "spirit": true, "tails": true}
	main.show_menu()
	await wait(1.0)
	await shot("menu")
	main.show_brief(31337)
	w = main.current
	await wait(0.6)
	await shot("brief")
	w.hud._close_brief()
	w.env.weather_plan = [[0.0, "clear"]]
	await wait(3.0)
	await shot("street_morning")
	# в доме цели
	var pl: PlayerCtl = w.player
	var cs: Case = w.case
	var t: Person = cs.target
	var h := pl.host
	h.global_position = t.global_position + Vector2(-40, 0)
	h.area = t.area
	h.set_inside(t.inside)
	await wait(2.0)
	await shot("inside_home")
	# дух с клешнями
	pl.leave(true)
	await wait(1.0)
	pl.claw = 3
	for c in ["gait", "lunch", "habit", "work"]:
		cs.learn(c, randf_range(30, 95), "со слов")
	cs.card("portrait")["pinned"] = true
	await wait(1.0)
	await shot("spirit")
	w.hud.board = true
	await shot("board")
	w.hud.board = false
	w.hud.map = true
	await shot("map")
	w.hud.map = false
	# вечер, фонари
	await game(2024, 20.6, "clear")
	await wait(3.0)
	await shot("evening")
	# дождь ночью
	await game(555, 22.4, "rain")
	await wait(3.0)
	await shot("night_rain")
	# метро
	await game(808, 8.2, "cloudy")
	var pl2: PlayerCtl = w.player
	pl2.leave(true)
	var m: Dictionary = w.city.areas["M"]
	pl2.spirit.global_position = Vector2((float(m["x0"]) + float(m["x1"])) / 2.0 + 60, float(m["y"]) - 20)
	pl2.spirit.set_inside(true)
	pl2.spirit.area = "M"
	w.train_t = 0.0
	await wait(4.0)
	await shot("metro")
	var c: Dictionary = w.city.areas["C"]
	pl2.spirit.global_position = Vector2((float(c["x0"]) + float(c["x1"])) / 2.0, float(c["y"]) - 20)
	pl2.spirit.area = "C"
	await wait(1.5)
	await shot("collector")
	# разговор с прохожим
	await game(31337, 10.2, "clear")
	var pl3: PlayerCtl = w.player
	var hh := pl3.host
	var who: Person = null
	for p in w.people:
		if p.prof == "pensioner" and p.state == "ok" and p != w.case.target:
			who = p
			break
	var sq: float = w.city.places["Сквер"]["x"]
	for q in [hh, who]:
		q.area = "S"
		q.set_inside(false)
	hh.global_position = Vector2(sq, K.floor_y(0) - 1)
	who.global_position = Vector2(sq + 30, K.floor_y(0) - 1)
	who.brain.react = {}
	await wait(1.0)
	pl3._talk(who)
	w.hud.talk.choose(0)
	await wait(0.3)
	w.hud.talk.choose(1)
	await wait(1.0)
	await shot("talk")
	w.hud.close_talk()
	# дренаж под коллектором
	var dd: Dictionary = w.city.areas["D"]
	var lx := float(w.city.places["Лежанка"]["x"])
	hh.area = "D"
	hh.set_inside(true)
	hh.global_position = Vector2(lx + 60, float(dd["y"]) - 1)
	await wait(2.0)
	await shot("drain")
	# итог
	var res := {"ok": true, "grade": "чисто", "tails": [], "how": "fall", "alarms": 0, "extra": 0, "hour": 13.4, "target": "Лариса Савельева", "curator": "Лиса", "seed": 808}
	w.queue_free()
	main.show_result(res)
	await wait(1.2)
	await shot("result")
	get_tree().quit()
