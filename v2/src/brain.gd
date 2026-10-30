class_name Brain
extends RefCounted
## Мозг прохожего: расписание по часам, путь по зонам через лестницы и входы, двери,
## реакции на шум и тела, разговоры, оцепенение после того, как дух покинул тело.

var p: Person
var world: Node
var city: City
var sched: Array = []          # [{h, area, x, act, name}]
var goal := {}
var route: Array = []
var step := 0
var arrived := false
const SPREAD_ACTS := ["idle", "sit", "smoke", "shop", "eat", "work", "phone", "away"]
var slot_x := INF               # занятое место на людной точке
var react := {}                # {kind, pos, t, area}
var ko_left := 0.0
var dazed_t := 0.0
var away := false
var talk_t := 0.0
var think_t := 0.0
var stuck_t := 0.0
var last_x := 0.0
var door_wait := 0.0
var seen_host := {}            # pid тела игрока -> секунды на виду (для цели)
var alert := 0.0               # настороженность 0..100
var fear := 0.0
var lines: Array = []          # что может сказать в разговоре
var wander_t := 0.0
var is_target := false


func _init(person: Person, w: Node) -> void:
	p = person
	world = w
	city = person.city
	p.brain = self


func current_goal(h: float) -> Dictionary:
	var g := {}
	var hh := fmod(h, 24.0)
	if hh < 6.0:
		hh += 24.0
	for e in sched:
		if float(e["h"]) <= hh:
			g = e
	if g.is_empty() and sched.size() > 0:
		g = sched[sched.size() - 1]
	return g


func tick(dt: float) -> void:
	if p.host:
		return
	if p.state == "ko":
		ko_left -= dt
		if ko_left <= 0.0:
			p.wake_up()
			dazed_t = 25.0
			world.woke_up(p)
		return
	if p.state in ["dead", "carried", "hidden", "gone"]:
		return
	if p.state == "transit":
		return
	if dazed_t > 0.0:
		dazed_t -= dt
		p.move_x = 0.0
		p.pose = "stagger" if dazed_t > 6.0 else ""
		if dazed_t <= 0.0:
			p.pose = ""
			_replan()
		return
	alert = maxf(0.0, alert - dt * 0.6)
	fear = maxf(0.0, fear - dt * 2.0)
	# реакция важнее расписания
	if not react.is_empty():
		react["t"] = float(react["t"]) - dt
		if float(react["t"]) <= 0.0:
			react = {}
			p.mode = "walk"
			p.pose = ""
			goal = {}
			think_t = 0.0
		else:
			_do_react(dt)
			return
	think_t -= dt
	if think_t <= 0.0:
		think_t = randf_range(0.6, 1.2)
		var g := current_goal(world.env.hour)
		if g != goal and not g.is_empty():
			goal = g
			_replan()
	if away:
		return
	_follow(dt)


func _replan() -> void:
	arrived = false
	slot_x = INF
	if goal.is_empty():
		return
	p.pose = ""
	if goal.get("act", "") == "away" and p.area == "M":
		_go_away()
		return
	route = city.route(p.area, goal["area"])
	step = 0
	if route.is_empty() and p.area != goal["area"]:
		# нет пути (заперто или потерялся): уточнить зону и ждать
		p.update_area()
		route = city.route(p.area, goal["area"])


func _follow(dt: float) -> void:
	if goal.is_empty():
		p.move_x = 0.0
		return
	if step < route.size():
		var e: Dictionary = route[step]
		var pt: Dictionary = e["p"]
		var x := City.px_from(pt, int(e["dir"]))
		var from_area: String = pt["a"] if int(e["dir"]) > 0 else pt["b"]
		if p.area != from_area:
			p.update_area()
			_replan()
			return
		if _walk_to(x, dt, 3.0):
			if pt["lock"] != "" and not (pt["lock"] in p.keys) and not world.portal_unlocked(pt):
				# заперто — ждём, потом меняем цель
				door_wait += dt
				p.move_x = 0.0
				if door_wait > 4.0:
					door_wait = 0.0
					goal = {"h": 0, "area": p.area, "x": p.global_position.x + randf_range(-60, 60), "act": "idle"}
					route = []
				return
			door_wait = 0.0
			step += 1
			p.use_portal(pt, int(e["dir"]))
		return
	if p.area != goal["area"]:
		_replan()
		if route.is_empty():
			p.move_x = 0.0
		return
	var gx := float(goal["x"]) + float(goal.get("dx", 0.0))
	# на людных местах — своё место рядом, а не в одной точке со всеми
	if goal.get("act", "") in SPREAD_ACTS and p.area == goal["area"] and not p.inside:
		if is_inf(slot_x) and absf(gx - p.global_position.x) < 160.0:
			slot_x = world.free_spot(p, gx)
		if not is_inf(slot_x):
			gx = slot_x
	if not arrived:
		if _walk_to(gx, dt, 4.0):
			arrived = true
			_arrive()
	else:
		p.move_x = 0.0
		_idle(dt)


func _walk_to(x: float, dt: float, tol: float) -> bool:
	var dx := x - p.global_position.x
	if absf(dx) <= tol:
		p.move_x = 0.0
		return true
	# дверь на пути
	var d: Dictionary = world.door_between(p, p.global_position.x, x)
	if not d.is_empty():
		var ddx := float(d["x"]) - p.global_position.x
		if absf(ddx) < 18.0:
			if bool(d["locked"]) and not (d["key"] in p.keys):
				p.move_x = 0.0
				door_wait += dt
				if door_wait > 3.0:
					door_wait = 0.0
					goal = {"h": 0, "area": p.area, "x": p.global_position.x - signf(ddx) * 50.0, "act": "idle"}
					route = []
					arrived = false
				return false
			world.open_door(d, p)
	p.move_x = signf(dx) * (1.0 if absf(dx) > 6 else 0.4)
	# застрял
	if absf(p.global_position.x - last_x) < 0.2:
		stuck_t += dt
		if stuck_t > 2.5:
			stuck_t = 0.0
			p.want_jump = true
			if p.is_on_floor() and absf(dx) < 30:
				return true
	else:
		stuck_t = 0.0
	last_x = p.global_position.x
	return false


func _arrive() -> void:
	var act: String = goal.get("act", "idle")
	p.facing = int(goal.get("face", p.facing))
	match act:
		"sit", "sofa", "eat", "desk":
			p.pose = "sit"
		"bed":
			p.pose = "sit"
		"smoke":
			p.pose = "smoke"
		"phone":
			p.pose = "phone"
		"read":
			p.pose = "read"
		"work", "stove", "cashier", "barista", "shop":
			p.pose = "work"
		"guard":
			p.pose = ""
		"away":
			_go_away()
		_:
			p.pose = ""
	world.npc_arrived(p, goal)


func _go_away() -> void:
	## Уехал на метро: пропадает из района до следующей цели.
	away = true
	p.state = "gone"
	p.visible = false
	p.collision_mask = 0
	world.npc_left(p)


func come_back() -> void:
	away = false
	p.state = "ok"
	p.visible = true
	p.area = "M"
	p.set_inside(true)
	var a: Dictionary = city.areas["M"]
	p.global_position = Vector2(randf_range(float(a["x0"]) + 40, float(a["x1"]) - 40), float(a["y"]))
	_replan()


func _idle(dt: float) -> void:
	# у цели: изредка переступить, оглянуться, заговорить
	wander_t -= dt
	if p.gait == "glance" and randf() < dt * 0.2:
		p.look_t = 0.8
	if wander_t <= 0.0:
		wander_t = randf_range(5.0, 14.0)
		if goal.get("act", "") in ["idle", "wait", "walk"] and randf() < 0.5:
			goal = goal.duplicate()
			goal["dx"] = randf_range(-26, 26)
			arrived = false
	talk_t -= dt
	if talk_t <= 0.0:
		talk_t = randf_range(8.0, 20.0)
		world.try_talk(p)


# ======================= реакции =======================

func hear(pos: Vector2, loud: float, kind: String) -> void:
	## Шум рядом: посмотреть, подойти (если не испуган).
	if p.host or p.state != "ok":
		return
	if not react.is_empty() and react["kind"] in ["flee", "alarm"]:
		return
	p.facing = 1 if pos.x > p.global_position.x else -1
	var area := city.area_at(pos, p.inside)
	if loud > 80.0 and area == p.area and kind != "step":
		react = {"kind": "look", "pos": pos, "t": randf_range(4.0, 7.0), "area": area}
		p.pose = ""
		p.say(["Что там?", "Кто здесь?", "А?", "Что за шум?"][randi() % 4], 2.0)
	else:
		p.look_t = 1.2


func see_body(body: Person) -> void:
	if p.host or p.state != "ok":
		return
	if not react.is_empty() and react["kind"] in ["alarm", "flee"]:
		return
	react = {"kind": "alarm", "pos": body.global_position, "t": 40.0, "area": p.area, "body": body}
	p.mode = "run"
	p.say(["Помогите!", "Тут человек лежит!", "Убили!", "Милиция!"][randi() % 4], 3.0, Color(1.0, 0.6, 0.5))
	fear = 100.0


func scare(pos: Vector2, t: float = 6.0) -> void:
	if p.host or p.state != "ok":
		return
	react = {"kind": "flee", "pos": pos, "t": t, "area": p.area}
	p.mode = "run"
	fear = 100.0
	p.say(["Ай!", "Что это?!", "Господи…", "Мама…"][randi() % 4], 2.0)


func distract(pos: Vector2, t: float = 8.0) -> void:
	if p.host or p.state != "ok":
		return
	react = {"kind": "look", "pos": pos, "t": t, "area": city.area_at(pos, p.inside)}
	p.pose = ""


func _do_react(dt: float) -> void:
	var pos: Vector2 = react["pos"]
	match react["kind"]:
		"look":
			if react["area"] == p.area and absf(pos.x - p.global_position.x) > 24:
				_walk_to(pos.x, dt, 20.0)
				p.mode = "walk"
			else:
				p.move_x = 0.0
				p.facing = 1 if pos.x > p.global_position.x else -1
		"flee":
			var dir := -signf(pos.x - p.global_position.x)
			if dir == 0:
				dir = 1
			var a: Dictionary = city.areas.get(p.area, {})
			if not a.is_empty() and (p.global_position.x < float(a["x0"]) + 10 or p.global_position.x > float(a["x1"]) - 10):
				p.move_x = 0.0
				p.pose = "cower"
			else:
				p.move_x = dir
		"alarm":
			# бежит к ближайшему таксофону звонить; если таксофона нет — кричит на месте
			if not react.has("phone"):
				react["phone"] = world.nearest_payphone(p.global_position)
				goal = {"h": 0, "area": "S", "x": float(react["phone"]["x"]) + 10.0, "act": "phone"}
				route = city.route(p.area, "S")
				step = 0
				arrived = false
			if p.area == "S" and absf(p.global_position.x - float(goal["x"])) < 8:
				p.move_x = 0.0
				p.pose = "phone"
				if not react.has("called"):
					react["called"] = true
					world.police_called(react.get("body"), p)
					react["t"] = 6.0
			else:
				_follow(dt)
		"follow":
			var tgt: Person = react["who"]
			if is_instance_valid(tgt) and tgt.area == p.area:
				var dx := tgt.global_position.x - p.global_position.x
				if absf(dx) > 30:
					p.move_x = signf(dx)
				else:
					p.move_x = 0.0
					p.facing = 1 if dx > 0 else -1
			else:
				react["t"] = 0.0
		"goto":
			goal = {"h": 0, "area": react["area"], "x": pos.x, "act": "idle"}
			_follow(dt)
		"talk":
			p.move_x = 0.0
			var who: Person = react["who"]
			if is_instance_valid(who):
				p.facing = 1 if who.global_position.x > p.global_position.x else -1
