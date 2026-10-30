class_name PlayerCtl
extends Node
## Игрок — дух без лица. В теле ходит, говорит, прячет и убивает руками.
## Вне тела летает, тает на свету и действует клешнями; каждое действие стоит памяти.

const CLAWS := [
	{"id": "tug", "name": "Дёрнуть", "cost": 3.5, "hint": "стук, рывок за рукав, горшок с подоконника, рубильник"},
	{"id": "take", "name": "Утащить", "cost": 5.2, "hint": "взять улику, ключи из кармана, ключ из ящика"},
	{"id": "move", "name": "Передвинуть", "cost": 3.5, "hint": "дверь, урну, мебель — или толкнуть человека"},
	{"id": "stun", "name": "Оглушить", "cost": 15.8, "hint": "человек падает без памяти на полминуты"},
	{"id": "choke", "name": "Задушить", "cost": 30.0, "hint": "три секунды держать рядом — и всё"},
]
const REACH := 56.0
const ENTER_R := 170.0
const NEAR := 20.0
const STRANGLE_T := 3.2
const SPEEDS := [1.0, 4.0, 10.0]

var world: Node
var city: City
var case: Case
var host: Person = null
var spirit: Spirit
var density := 100.0
var claw := -1
var last_enter_t := -100.0
var hover: Person = null
var hover_claw := {}            # что под клешнёй: {kind, ref, text, ok}
var mouse_w := Vector2.ZERO
var prompts: Array = []         # [[клавиша, текст]]
var act_e := {}                 # что сделает E
var act_w := {}
var act_s := {}
var greet_t := 0.0
var hold_kind := ""            # тип перехода, который повторяется, пока держишь W/S
var act_q := {}
var act_g := {}
var strangle := {}              # {victim, t, need}
var choke := {}                 # {victim, t}
var emergency_t := 0.0
var used := {}                  # pid -> true (входил ли уже)
var wait_i := 0
var hurt := 0.0
var hurt_why := ""
var swoop := {}                 # полёт духа в тело: {from, p, t}
var msg := ""
var msg_t := 0.0


func setup() -> void:
	city = world.city
	case = world.case
	spirit = Spirit.new()
	spirit.setup(city)
	city.people.add_child(spirit)
	spirit.visible = false


# ======================= тело =======================

func enter(p: Person, free: bool) -> void:
	if host:
		leave(false)
	if not free:
		var cost := 8.0 + (20.0 if world.t_total - last_enter_t < 8.0 else 0.0)
		case.spend(cost, "enter" if cost < 10.0 else "enter_fast")
		last_enter_t = world.t_total
	host = p
	p.host = true
	if p.brain:
		p.brain.react = {}
		p.brain.dazed_t = 0.0
	p.pose = ""
	p.move_x = 0.0
	p.mode = "walk"
	spirit.visible = false
	spirit.held = {}
	world.susp = 0.0
	world.stats["jumps"] += 1
	Game.stats["jumps"] = int(Game.stats.get("jumps", 0)) + 1
	density = maxf(density, 30.0)
	wait_i = 0
	world.env.speed = 1.0
	Sfx.play("enter", -4.0)
	p.flash = 1.0
	if not used.has(p.pid):
		used[p.pid] = true
		_foreign(p)
	if world.hud:
		world.hud.body_changed()


func leave(show_spirit: bool = true) -> void:
	if host == null:
		return
	var p := host
	_stop_strangle(false)
	if p.carrying:
		var c := p.carrying
		p.carrying = null
		c.drop_from(p)
		_dropped(c)
	p.host = false
	p.mode = "walk"
	p.move_x = 0.0
	p.pose = ""
	if p.climbing:
		p.climb_stop()
	if p.is_active() and p.brain:
		p.brain.dazed_t = 7.0
		p.brain.goal = {}
		p.say(["Где я?..", "Что я тут делаю?", "Голова…", "…"][randi() % 4], 2.5)
	# тело не помнит, что видело, пока в нём был дух
	for w in world.witnesses:
		if w["who"] == p and not w["done"]:
			w["done"] = true
			case.clear_tail("witness%d" % p.pid)
	if p.has_meta("executor"):
		var t := case.target
		if t and (t.area != p.area or t.global_position.distance_to(p.global_position) > 260.0):
			p.remove_meta("executor")
			case.clear_tail("executor")
	host = null
	world.env.speed = 1.0
	wait_i = 0
	if show_spirit:
		spirit.global_position = p.head_pos() + Vector2(0, 6)
		spirit.set_inside(p.inside)
		spirit.area = p.area
		spirit.velocity = Vector2(0, -30)
		spirit.visible = true
		Sfx.play("leave", -4.0)
	if world.hud:
		world.hud.body_changed()


func _foreign(p: Person) -> void:
	## Чужая память: тело кое-что знает о своём ремесле.
	match p.prof:
		"guard":
			case.add_foreign("f_guard", "Память охранника", "Пульт в каморке у входа. Записи камер стираются кнопкой «сброс». Ключи от крыши и пожарной лестницы — на поясе.")
			world.hud.card_toast(case.card("f_guard"), "Чужая память")
		"janitor":
			case.add_foreign("f_janitor", "Память дворника", "Подвалы связаны с коллектором шахтами. Люк у гаражей открыт всегда. Ключи от подвалов и крыш — свои.")
			world.hud.card_toast(case.card("f_janitor"), "Чужая память")
		"police":
			case.add_foreign("f_police", "Память милиционера", "Тело в шкафу ищут последним. Несчастный случай не расследуют.")
			world.hud.card_toast(case.card("f_police"), "Чужая память")


func focus_pos() -> Vector2:
	if host:
		return host.global_position
	return spirit.global_position


func focus_inside() -> bool:
	return host.inside if host else spirit.inside


func focus_area() -> String:
	return host.area if host else spirit.area


func facing() -> int:
	if host:
		return host.facing
	return -1 if spirit.spr.flip_h else 1


func after_transit() -> void:
	if host and host.carrying:
		host.carrying.area = host.area


func say(t: String, dur: float = 2.5) -> void:
	msg = t
	msg_t = dur


# ======================= цикл =======================

func _process(dt: float) -> void:
	if world.over or world.paused:
		return
	msg_t = maxf(0.0, msg_t - dt)
	emergency_t = maxf(0.0, emergency_t - dt * 0.5) if not Input.is_physical_key_pressed(KEY_R) else emergency_t
	mouse_w = world.view.screen_to_world(world.view.get_local_mouse_position())
	if not swoop.is_empty():
		_swoop(dt)
	elif host:
		if host.state == "dead":
			leave(true)
			world.hud.voice("ЧУТЬЁ", "Тело умерло. Ты снаружи.", Color(0.9, 0.6, 0.5))
		else:
			_body(dt)
	else:
		_spirit(dt)
	world.view.spirit_k = move_toward(world.view.spirit_k, 0.0 if host else 1.0, dt * 2.5)
	world.view.hurt_k = move_toward(world.view.hurt_k, hurt, dt * 3.0)
	world.view.fade_k = clampf((60.0 - case.memory()) / 60.0, 0.0, 1.0)


func _key(k: Key) -> bool:
	return Input.is_physical_key_pressed(k)


func _body(dt: float) -> void:
	var p := host
	hurt = 0.0
	density = minf(100.0, density + 9.0 * dt)
	if p.state == "transit" or p.state == "ko":
		p.move_x = 0.0
		_body_prompts()
		return
	_neighbours(dt)
	if world.hud and world.hud.talk:
		p.move_x = 0.0
		p.mode = "walk"
		prompts = []
		return
	var mx := 0.0
	if _key(KEY_A) or _key(KEY_LEFT):
		mx -= 1.0
	if _key(KEY_D) or _key(KEY_RIGHT):
		mx += 1.0
	p.mode = "run" if _key(KEY_SHIFT) else ("sneak" if _key(KEY_CTRL) else "walk")
	if p.climbing:
		var v := 0.0
		if _key(KEY_W) or _key(KEY_UP):
			v -= 75.0
		if _key(KEY_S) or _key(KEY_DOWN):
			v += 90.0
		p.climb_v = v
		if mx != 0.0:
			p.climb_stop()
			p.velocity.x = mx * 40.0
	if not strangle.is_empty():
		mx = 0.0
		_strangle(dt)
	p.move_x = mx
	if world.env.speed > 1.0 and (mx != 0.0 or world.susp > 5.0 or not strangle.is_empty()):
		wait_i = 0
		world.env.speed = 1.0
	_body_prompts()
	# держишь W/S — лестница и лифт идут этаж за этажом без новых нажатий
	if hold_kind != "" and not p.climbing and p.state == "ok":
		var up := _key(KEY_W) or _key(KEY_UP)
		var dn := _key(KEY_S) or _key(KEY_DOWN)
		var a: Dictionary = act_w if up else (act_s if dn else {})
		if not a.is_empty() and a["kind"] == "portal" and a["p"]["kind"] == hold_kind and not a["locked"]:
			_do(a)
		elif not up and not dn:
			hold_kind = ""


func _neighbours(dt: float) -> void:
	## Соседи и коллеги здороваются с телом. Не ответишь — обидятся и запомнят.
	var p := host
	greet_t -= dt
	if greet_t <= 0.0:
		greet_t = 0.5
		for q in world.people:
			if q == p or q.state != "ok" or q.area != p.area or q.host or q == case.target:
				continue
			if absf(q.global_position.x - p.global_position.x) > 46.0 or absf(q.global_position.y - p.global_position.y) > 30.0:
				continue
			var nb: bool = q.home.has("bid") and p.home.has("bid") and int(q.home["bid"]) == int(p.home["bid"])
			var col: bool = q.has_meta("work") and p.has_meta("work") and q.get_meta("work") == p.get_meta("work")
			if not (nb or col):
				continue
			var k := "%d:%d" % [q.pid, p.pid]
			if world.greeted_by.has(k):
				continue
			world.greeted_by[k] = true
			q.facing = 1 if p.global_position.x > q.global_position.x else -1
			q.say(["Здравствуй, %s!" % p.first, "О, %s, привет!" % p.first, "Доброе утро, %s." % p.first if world.env.hour < 12.0 else "Добрый вечер, %s." % p.first][randi() % 3], 3.0)
			world.greet_wait[q.pid] = 7.0
	for pid in world.greet_wait.keys():
		world.greet_wait[pid] = float(world.greet_wait[pid]) - dt
		if float(world.greet_wait[pid]) <= 0.0:
			world.greet_wait.erase(pid)
			var q2: Person = world.people[pid]
			if q2.state == "ok":
				q2.say(["Даже не поздоровался…", "Ишь, нос задрал.", "Что это с ним сегодня?"][randi() % 3] if not p.female else ["Даже не поздоровалась…", "Что это с ней сегодня?"][randi() % 2], 3.0)
				world.susp += 6.0
				if world.susp_why == "":
					world.susp_why = "не ответил соседу"
				Talk.remember(world, q2, p, "grudge", "не поздоровал%s" % ("ась" if p.female else "ся"), -8.0)


func _strangle(dt: float) -> void:
	var v: Person = strangle["victim"]
	if not is_instance_valid(v) or v.state == "dead" or host.global_position.distance_to(v.global_position) > 30.0:
		_stop_strangle(false)
		return
	if not _key(KEY_Q):
		_stop_strangle(true)
		return
	strangle["t"] = float(strangle["t"]) + dt
	host.pose = "strangle"
	host.facing = 1 if v.global_position.x > host.global_position.x else -1
	v.facing = -host.facing
	v.move_x = 0.0
	v.pose = "choke"
	if v.brain and v.state == "ok":
		v.brain.react = {"kind": "look", "pos": host.global_position, "t": 0.6, "area": v.area}
	if fmod(float(strangle["t"]), 0.9) < dt:
		Sfx.play("choke", -6.0, randf_range(0.9, 1.1))
	world.noise_at(v.global_position, 50.0, v, "choke")
	if float(strangle["t"]) >= float(strangle["need"]):
		strangle = {}
		host.pose = ""
		v.pose = ""
		world.kill(v, "hands", host)


func _stop_strangle(released: bool) -> void:
	if strangle.is_empty():
		return
	var v: Person = strangle["victim"]
	strangle = {}
	if host:
		host.pose = ""
	if is_instance_valid(v) and v.state == "ok":
		v.pose = ""
		if released:
			v.say("Помогите!", 2.5, Color(1.0, 0.5, 0.4))
			world.add_witness(v, "на него напали")


func suspicious_acts() -> Array:
	## Что в поведении тела бросается в глаза: [скорость роста подозрения, «что делает»].
	var out := []
	var p := host
	if p == null:
		return out
	if not strangle.is_empty():
		out.append([30.0, "душит человека"])
	if p.carrying:
		out.append([55.0, "несёт тело"])
	if p.climbing:
		out.append([16.0, "лезет по трубе"])
	if p.state == "ok" and absf(p.velocity.x) > 70.0:
		out.append([5.0, "бежит"])
	if p.mode == "sneak" and absf(p.velocity.x) > 4.0:
		out.append([3.0, "крадётся"])
	if p.area.begins_with("R") and p.prof != "janitor":
		out.append([3.0, "на крыше"])
	if p.inside:
		var rm := city.room_at(p.area, p.global_position.x)
		if not rm.is_empty():
			if int(rm.get("apt", 0)) > 0 and rm["kind"] in ["living", "kitchen"]:
				var key := "apt%d_%d" % [int(rm["bid"]), int(rm["apt"])]
				if not (key in p.keys):
					out.append([8.0, "в чужой квартире"])
			elif rm.get("staff", false) and not (p.prof in ["guard", "janitor", "police", "barista", "pharm", "cashier"]):
				out.append([7.0, "в служебном помещении"])
	for q in world.people:
		if q != p and q.state == "dead" and q.visible and q.area == p.area and q.global_position.distance_to(p.global_position) < 40.0:
			out.append([5.0, "стоит над телом"])
			break
	return out


# ======================= подсказки и действия в теле =======================

func _portal_side(pt: Dictionary, area: String, inside: bool, pos: Vector2) -> int:
	## 1 — можно пройти a→b, -1 — b→a, 0 — портал не с этой стороны.
	if pt["kind"] in ["window", "vent"]:
		if pt["b"] == area and inside:
			return -1
		if not inside and absf(pos.y - float(pt["y"])) < 12.0:
			return 1
		return 0
	if pt["a"] == area:
		return 1
	if pt["b"] == area:
		return -1
	return 0


func _portal_dir_word(pt: Dictionary, dir: int) -> String:
	var from_y := float(pt["ya"]) if dir > 0 else float(pt["yb"])
	var to_y := float(pt["yb"]) if dir > 0 else float(pt["ya"])
	if to_y < from_y - 4.0:
		return "up"
	if to_y > from_y + 4.0:
		return "down"
	return "side"


func _portal_text(pt: Dictionary, dir: int) -> String:
	var to: String = pt["b"] if dir > 0 else pt["a"]
	match pt["kind"]:
		"stairs":
			var f := int(city.areas[to]["f"])
			return "лестница: %s" % ("подвал" if f < 0 else "%d-й этаж" % (f + 1))
		"entrance", "backdoor":
			return "выйти на улицу" if to == "S" else "войти: %s" % _bname(pt, to)
		"hatch":
			return "люк на крышу" if dir > 0 else "люк вниз"
		"manhole":
			return "в коллектор" if dir > 0 else "наверх, на улицу"
		"shaft":
			return "шахта в коллектор" if dir > 0 else "шахта в подвал"
		"escalator":
			return "эскалатор вниз" if dir > 0 else "эскалатор наверх"
		"window":
			return "залезть в окно" if dir > 0 else "вылезти в окно"
		"vent":
			return "в форточку" if dir > 0 else "из форточки"
		"lift":
			return "лифт: %d-й этаж" % (int(city.areas[to]["f"]) + 1)
		"bridge":
			return "по переходу в соседний дом"
		"passage":
			return "подвальный ход в соседний дом"
		"roofladder":
			return "лестница на соседнюю крышу"
		"ladder":
			return "скобы вниз, в дренаж" if dir > 0 else "скобы наверх, в коллектор"
		"srvstairs":
			return "служебная лестница на станцию" if dir > 0 else "служебная лестница вниз"
		"ventshaft":
			return "вентшахта вверх" if _portal_dir_word(pt, dir) == "up" else "вентшахта вниз"
		"drain":
			return "в водосток" if dir > 0 else "из водостока"
	return "пройти"


func _bname(_pt: Dictionary, area: String) -> String:
	if not city.areas.has(area):
		return "дом"
	var b: Dictionary = city.buildings[int(city.areas[area]["bid"])]
	if b["name"] != "":
		return b["name"]
	return "подъезд"


func _portals_here(pos: Vector2, area: String, inside: bool, human: bool, r: float) -> Array:
	var out := []
	for pt in city.portals:
		if human and not pt["human"]:
			continue
		if not human and not pt["spirit"]:
			continue
		var dir := _portal_side(pt, area, inside, pos)
		if dir == 0:
			continue
		var px := City.px_from(pt, dir)
		var d := absf(px - pos.x)
		if d > float(pt.get("zw", r)):
			continue
		out.append({"p": pt, "dir": dir, "w": _portal_dir_word(pt, dir), "d": d})
	out.sort_custom(func(a, b): return a["d"] < b["d"])
	return out


func _locked_for(pt: Dictionary, dir: int, p: Person) -> bool:
	if pt["lock"] == "" or pt.get("opened", false):
		return false
	if pt["kind"] == "window" and dir < 0:
		return false        # изнутри окно открывается
	if pt["kind"] == "hatch" and dir < 0:
		return false
	return not (pt["lock"] in p.keys)


func _body_prompts() -> void:
	var p := host
	act_e = {}
	act_w = {}
	act_s = {}
	act_q = {}
	act_g = {}
	prompts = []
	var pos := p.global_position
	if p.state == "ko":
		prompts.append(["F", "покинуть тело"])
		return
	if p.state == "transit":
		return
	# лазы и лестницы
	for e in _portals_here(pos, p.area, p.inside, true, 14.0):
		var pt: Dictionary = e["p"]
		var t := _portal_text(pt, e["dir"])
		var locked := _locked_for(pt, e["dir"], p)
		var a := {"kind": "portal", "p": pt, "dir": e["dir"], "text": t + (" (заперто)" if locked else ""), "locked": locked}
		if e["w"] == "up" and act_w.is_empty():
			act_w = a
		elif e["w"] == "down" and act_s.is_empty():
			act_s = a
		elif e["w"] == "side" and act_e.is_empty():
			act_e = a
	# трубы и пожарные лестницы
	if act_w.is_empty() and not p.climbing:
		for c in city.climbs:
			if absf(float(c["x"]) - pos.x) < 14.0 and pos.y <= float(c["y1"]) + 6.0 and pos.y > float(c["y0"]):
				act_w = {"kind": "climb", "c": c, "text": "лезть по %s" % ("трубе" if c["kind"] == "pipe" else "лестнице")}
				break
	if act_s.is_empty() and not p.inside and p.is_on_floor() and _on_platform(p):
		act_s = {"kind": "drop", "text": "спрыгнуть вниз"}
	# предметы, двери, люди
	var best := {}
	var bd := 1e9
	for o in city.objs:
		var a2 := _obj_action(o, p)
		if a2.is_empty():
			continue
		var d := absf(float(o["x"]) - pos.x)
		if a2.get("prio", false):
			d -= 100.0
		if d < bd:
			bd = d
			best = a2
	var near := _person_near(p, 26.0)
	if near and (best.is_empty() or absf(near.global_position.x - pos.x) < bd):
		if near.is_active() and not p.carrying:
			best = {"kind": "talk", "who": near, "text": "заговорить: %s" % _who_word(near)}
	if not best.is_empty() and (act_e.is_empty() or best.get("prio", false) or bd < 8.0):
		act_e = best
	# руки
	if not p.carrying:
		var v := _person_near(p, NEAR, true)
		if v:
			if v.state == "ok":
				if _can_push_off(p, v):
					act_q = {"kind": "push", "who": v, "text": "столкнуть"}
				elif _road_push(p, v):
					act_q = {"kind": "road", "who": v, "text": "толкнуть под машину"}
				else:
					act_q = {"kind": "strangle", "who": v, "text": "задушить (держать)"}
			elif v.state == "ko":
				act_q = {"kind": "strangle", "who": v, "text": "добить (держать)"}
		var body := _body_near(p)
		if body:
			act_g = {"kind": "pick", "who": body, "text": "поднять тело"}
	else:
		act_g = {"kind": "drop", "text": "бросить тело"}
	for a3 in [["E", act_e], ["W", act_w], ["S", act_s], ["Q", act_q], ["G", act_g]]:
		if not (a3[1] as Dictionary).is_empty():
			prompts.append([a3[0], a3[1]["text"]])
	if _payphone_near(p):
		prompts.append(["R", "экстренная линия (держать)"])
	prompts.append(["F", "покинуть тело"])


func _on_platform(p: Person) -> bool:
	var sp := city.get_world_2d().direct_space_state
	var q := PhysicsRayQueryParameters2D.create(p.global_position + Vector2(0, -2), p.global_position + Vector2(0, 6), K.L_PLATFORM)
	return not sp.intersect_ray(q).is_empty()


func _who_word(q: Person) -> String:
	var words := {"vendor": "киоскёрша" if q.female else "киоскёр", "barista": "буфетчица", "pharm": "аптекарша", "cashier": "кассир", "guard": "охранник",
		"janitor": "дворник", "pensioner": "пенсионерка" if q.female else "пенсионер", "student": "студентка" if q.female else "студент",
		"worker": "рабочий", "courier": "курьер", "police": "милиционер", "teacher": "учительница" if q.female else "учитель",
		"office": "служащая" if q.female else "служащий", "resident": "соседка" if q.female else "сосед",
		"tramp": "бродяжка" if q.female else "бродяга"}
	return words.get(q.prof, "прохожий")


func _person_near(p: Person, r: float, facing_only: bool = false) -> Person:
	var best: Person = null
	var bd := r
	for q in world.people:
		if q == p or q.state in ["dead", "carried", "hidden", "gone", "transit"]:
			continue
		if q.inside != p.inside or q.area != p.area:
			continue
		var dx: float = q.global_position.x - p.global_position.x
		if absf(q.global_position.y - p.global_position.y) > 16.0:
			continue
		if facing_only and dx * p.facing < -4.0:
			continue
		if absf(dx) < bd:
			bd = absf(dx)
			best = q
	return best


func _body_near(p: Person) -> Person:
	for q in world.people:
		if q == p or not (q.state in ["dead", "ko"]) or not q.visible or q.carried_by:
			continue
		if q.inside != p.inside:
			continue
		if q.global_position.distance_to(p.global_position) < 24.0:
			return q
	return null


func _can_push_off(p: Person, v: Person) -> bool:
	if not p.area.begins_with("R"):
		return false
	for o in city.objs:
		if o["kind"] == "roof_edge" and int(o["bid"]) == int(city.areas[p.area]["bid"]):
			var ex := float(o["x"])
			if absf(v.global_position.x - ex) < 26.0 and signf(ex - p.global_position.x) == float(p.facing):
				return true
	return false


func _road_push(p: Person, v: Person) -> bool:
	return p.area == "S" and not p.inside and world.car_near(v.global_position.x, 260.0)


func _payphone_near(p: Person) -> bool:
	if p.inside:
		return false
	for o in city.objs:
		if o["kind"] == "payphone" and absf(float(o["x"]) - p.global_position.x) < 22.0:
			return true
	return false


func _obj_action(o: Dictionary, p: Person) -> Dictionary:
	var pos := p.global_position
	if absf(float(o["x"]) - pos.x) > 22.0:
		return {}
	var oy := float(o.get("y", 0.0))
	if absf(oy - pos.y) > 28.0:
		return {}
	if o.has("inside") and bool(o["inside"]) != p.inside:
		return {}
	match o["kind"]:
		"door":
			if o["open"]:
				return {"kind": "door", "o": o, "text": "закрыть дверь"}
			if o["locked"]:
				if o["key"] in p.keys:
					return {"kind": "door", "o": o, "text": "отпереть ключом"}
				if _mat_key(o):
					return {"kind": "mat", "o": o, "text": "ключ под ковриком?", "prio": true}
				return {"kind": "locked", "o": o, "text": "заперто"}
			return {"kind": "door", "o": o, "text": "открыть дверь"}
		"clue":
			if o["taken"]:
				return {}
			return {"kind": "clue", "o": o, "text": "осмотреть: %s" % o["name"], "prio": true}
		"closet":
			if p.carrying and not o["full"]:
				return {"kind": "hide", "o": o, "text": "спрятать тело в шкаф", "prio": true}
		"dumpster":
			if p.carrying and not o["full"]:
				return {"kind": "hide", "o": o, "text": "спрятать тело в бак", "prio": true}
		"console":
			return {"kind": "console", "o": o, "text": "стереть записи камер"}
		"fusebox":
			return {"kind": "fuse", "o": o, "text": "выключить свет на этаже"}
		"lockbox":
			if not o["open"]:
				return {"kind": "lockbox", "o": o, "text": "открыть ящик"}
		"payphone":
			if o["ring"]:
				return {"kind": "answer", "o": o, "text": "СНЯТЬ ТРУБКУ", "prio": true}
			if case.calls_left > 0:
				return {"kind": "call", "o": o, "text": "позвонить куратору (%d)" % case.calls_left}
	return {}


func _mat_key(o: Dictionary) -> bool:
	var key := "apt%d_%d" % [int(case.p["home_bid"]), int(case.p["apt"])]
	return o["key"] == key and case.card("home")["known"] and case.stage(case.card("home")) != "empty"


func _do(a: Dictionary) -> void:
	var p := host
	match a["kind"]:
		"portal":
			if a["locked"]:
				say("Заперто. Нужен ключ.")
				Sfx.play("door_lock", -6.0)
				return
			if p.carrying and a["p"]["kind"] in ["window", "vent", "hatch", "manhole", "shaft", "ladder", "roofladder"]:
				say("С телом на руках не пролезть.")
				return
			hold_kind = a["p"]["kind"] if a["p"]["kind"] in ["stairs", "lift"] else ""
			p.use_portal(a["p"], a["dir"])
		"climb":
			if p.carrying:
				say("С телом не залезть.")
				return
			p.climb_start(a["c"])
		"drop":
			p.drop_t = 0.35
			p.set_inside(p.inside)
		"door":
			var d: Dictionary = a["o"]
			if d["open"]:
				world.city.set_door(d, false)
				d["t_close"] = 0.0
			else:
				d["locked"] = false
				world.open_door(d, p)
				d["t_close"] = 0.0
		"mat":
			var d2: Dictionary = a["o"]
			p.keys.append(d2["key"])
			say("Под ковриком — ключ. Как и говорили.")
			Sfx.play("pickup", -4.0)
		"locked":
			say("Заперто.")
			Sfx.play("door_lock", -6.0)
			world.noise_at(p.global_position, 40.0, p, "knock")
		"clue":
			var o: Dictionary = a["o"]
			o["taken"] = true
			(o["node"] as Node2D).visible = false
			var first := case.learn(o["card"], 100.0, "улика")
			world.hud.card_toast(case.card(o["card"]), o["name"], o["text"])
			Sfx.play("paper", -4.0)
			if not first:
				world.hud.voice("ПАМЯТЬ", "Это я уже знал. Теперь — ясно.", K.GOLD)
		"talk":
			_talk(a["who"])
		"hide":
			var o2: Dictionary = a["o"]
			var c := p.carrying
			p.carrying = null
			c.carried_by = null
			c.state = "hidden"
			c.visible = false
			c.hidden_in = o2
			c.global_position = Vector2(float(o2["x"]), float(o2["y"]))
			o2["full"] = true
			Sfx.play("thud", -4.0)
			Game.stats["bodies_hidden"] = int(Game.stats.get("bodies_hidden", 0)) + 1
			if c == case.target:
				case.clear_tail("body")
			say("Спрятано.")
		"console":
			var n := 0
			for t in case.open_tails():
				if String(t["id"]).begins_with("cam"):
					case.clear_tail(t["id"])
					n += 1
			Sfx.play("click", -2.0)
			if p.prof != "guard":
				world.susp += 25.0
			say("Записи стёрты." if n > 0 else "Пульт. Стирать нечего.")
		"fuse":
			_fuse(a["o"])
		"lockbox":
			var o3: Dictionary = a["o"]
			o3["open"] = true
			(o3["node"] as Sprite2D).frame = 1
			for k in o3["keys"]:
				if not (k in p.keys):
					p.keys.append(k)
			say("В ящике %s." % o3["what"])
			Sfx.play("pickup", -4.0)
		"answer":
			world.answer_phone(a["o"])
		"call":
			_call_curator()


func _talk(q: Person) -> void:
	## Разговор: меню снизу, у собеседника свой характер и настроение (см. Talk).
	if q.state != "ok" or not q.brain:
		return
	world.hud.open_talk(Talk.new(world, self, q))


func _call_curator() -> void:
	## Звонок с таксофона: куратор повторяет самую выцветшую запись.
	var worst := {}
	for c in case.cards:
		if c["known"] and c["own"] and (worst.is_empty() or float(c["clar"]) < float(worst["clar"])):
			worst = c
	case.calls_left -= 1
	Sfx.play("pickup", -4.0)
	if worst.is_empty():
		world.hud.voice("КУРАТОР", "Нечего повторять. Работай.", K.GOLD)
		return
	worst["clar"] = maxf(float(worst["clar"]), 85.0)
	world.hud.voice("КУРАТОР", "%s %s" % [case.curator["tic"], case.text(worst)], K.GOLD)


func _fuse(o: Dictionary) -> void:
	var bid := int(o["bid"])
	var f := int(o["f"])
	for l in city.lamps:
		if int(l["bid"]) == bid and not l["outer"]:
			var rm_ok := true
			if l.has("room"):
				rm_ok = int(city.rooms[int(l["room"])]["f"]) == f
			elif l.has("f"):
				rm_ok = int(l["f"]) == f
			if rm_ok:
				l["off_t"] = world.t_total + 45.0
	for c in city.cams:
		if int(c["bid"]) == bid:
			c["off_until"] = world.t_total + 45.0
	(o["node"] as Sprite2D).frame = 1
	world.get_tree().create_timer(45.0).timeout.connect(func(): if is_instance_valid(o["node"]): (o["node"] as Sprite2D).frame = 0)
	Sfx.play("switch", -2.0)
	world.noise_at(Vector2(float(o["x"]), float(o["y"])), 70.0, null, "switch")
	say("Щёлк. Темно.")


func _dropped(c: Person) -> void:
	## Тело положили: в подвале и коллекторе его никто не ищет.
	if c.area == "D" and c.state == "dead":
		# дренаж: тело уносит потоком — следов не остаётся
		c.set_meta("stashed", true)
		var tw := c.create_tween()
		tw.tween_property(c, "position:x", c.position.x + 90.0, 3.0)
		tw.parallel().tween_property(c, "modulate:a", 0.0, 3.0)
		tw.tween_callback(func(): c.visible = false)
		say("Вода подхватила тело и унесла в темноту.")
		if c == case.target:
			case.clear_tail("body")
	elif c.area.ends_with("F-1") or c.area == "C" or c.area == "D":
		c.set_meta("stashed", true)
		if c == case.target:
			case.clear_tail("body")
	elif c.has_meta("stashed"):
		c.remove_meta("stashed")


func _hands(a: Dictionary) -> void:
	var p := host
	var v: Person = a["who"]
	match a["kind"]:
		"strangle":
			strangle = {"victim": v, "t": 0.0, "need": STRANGLE_T if v.state == "ok" else 1.2}
			if v.brain:
				v.brain.react = {}
			v.say("Кх…", 1.5)
		"push":
			v.velocity = Vector2(p.facing * 150.0, -120.0)
			v.move_x = 0.0
			v.pose = ""
			if v.brain:
				v.brain.react = {"kind": "look", "pos": v.global_position, "t": 3.0, "area": v.area}
			v.say("А-а!", 1.5, Color(1, 0.5, 0.4))
			Sfx.play("grab", -4.0)
			world.cams_check(p.global_position, false, "кто-то столкнул человека")
			_witness_hands(p, v, "столкнул человека")
		"road":
			_road_kill(v, p.facing)
			_witness_hands(p, v, "толкнул под машину")


func _witness_hands(p: Person, v: Person, what: String) -> void:
	for q in world.people:
		if q == p or q == v or q.host or not q.is_active():
			continue
		if world.can_see(q, p.center(), p.inside, p.area, 0.9):
			world.add_witness(q, what)


func _road_kill(v: Person, dir: int) -> void:
	v.move_x = 0.0
	v.state = "transit"
	v.transit = {"pts": [v.global_position, v.global_position + Vector2(dir * 8.0, 22.0)], "i": 0, "t": 0.0, "dur": 0.4,
		"to_area": "S", "to_inside": false, "anim": "stagger", "kind": "road", "p": {}}
	Sfx.play("car", 0.0)
	world.get_tree().create_timer(0.45).timeout.connect(func():
		if is_instance_valid(v) and v.state != "dead":
			v.state = "ok"
			v.transit = {}
			world.kill(v, "car", null)
			world.view.shake = 1.0)


func _pick(v: Person) -> void:
	host.pick_up(v)
	if v.has_meta("stashed"):
		v.remove_meta("stashed")
	Sfx.play("grab", -6.0)


# ======================= дух =======================

func _spirit(dt: float) -> void:
	var s := spirit
	var mv := Vector2.ZERO
	if _key(KEY_A) or _key(KEY_LEFT):
		mv.x -= 1
	if _key(KEY_D) or _key(KEY_RIGHT):
		mv.x += 1
	if _key(KEY_W) or _key(KEY_UP):
		mv.y -= 1
	if _key(KEY_S) or _key(KEY_DOWN):
		mv.y += 1
	s.move = mv
	s.fast = _key(KEY_SHIFT)
	if s.transit.is_empty():
		var a := city.area_at(s.global_position + Vector2(0, 12), s.inside)
		if a == "" and s.inside:
			a = city.area_at(s.global_position + Vector2(0, 40), true)
		if a != "":
			s.area = a
		elif not s.inside:
			s.area = "S"
	# плотность
	var c := s.center()
	var rate := -0.45 * float(Game.d("density_mult")) * (0.67 if Game.has_perm("dense") else 1.0)
	hurt = 0.0
	hurt_why = ""
	if world.sun_on(c, s.inside):
		rate -= 5.0
		hurt = 0.6
		hurt_why = "солнце"
	var burn: float = world.lamp_burn(c, s.inside)
	if burn > 0.0:
		rate -= 7.0 * burn
		hurt = maxf(hurt, 0.4 + burn * 0.4)
		hurt_why = "фонарь"
	if world.dog and world.dog.drain_at(c, s.inside) > 0.0:
		rate -= 16.0
		hurt = 1.0
		hurt_why = "собака"
	if s.area == "C" and world.steam_at(c):
		rate -= 12.0
		hurt = maxf(hurt, 0.8)
		hurt_why = "пар"
	s.flicker = clampf(hurt, 0.0, 1.0)
	density = clampf(density + rate * dt, 0.0, 100.0)
	if density <= 0.0:
		_thrown()
		return
	# удушение клешнями
	if not choke.is_empty():
		_choke(dt)
	# кто под мышью
	hover = null
	var bd := 22.0
	for q in world.people:
		if q.state != "ok" or q.inside != s.inside or not q.visible:
			continue
		var d: float = q.center().distance_to(mouse_w)
		if d < bd and q.center().distance_to(c) < ENTER_R:
			bd = d
			hover = q
	hover_claw = _claw_target(mouse_w) if claw >= 0 else {}
	_spirit_prompts()


func _spirit_prompts() -> void:
	var s := spirit
	prompts = []
	act_e = {}
	act_w = {}
	act_s = {}
	var pos := s.global_position + Vector2(0, 10)
	for e in _portals_here(pos, s.area, s.inside, false, 16.0):
		var pt: Dictionary = e["p"]
		if pt["kind"] in ["window", "vent"]:
			if absf(float(pt["y"]) - pos.y) > 34.0:
				continue
		else:
			var fy := float(pt["ya"]) if e["dir"] > 0 else float(pt["yb"])
			if absf(fy - pos.y) > 40.0:
				continue
		var a := {"kind": "portal", "p": pt, "dir": e["dir"], "text": _portal_text(pt, e["dir"])}
		if e["w"] == "up" and act_w.is_empty():
			act_w = a
		elif e["w"] == "down" and act_s.is_empty():
			act_s = a
		elif e["w"] == "side" and act_e.is_empty():
			act_e = a
	for a2 in [["E", act_e], ["W", act_w], ["S", act_s]]:
		if not (a2[1] as Dictionary).is_empty():
			prompts.append([a2[0], a2[1]["text"]])
	var tgt := hover if hover else _nearest_body(s.center(), 60.0)
	if tgt:
		if tgt == case.target:
			prompts.append(["F", "в это тело не войти"])
		else:
			prompts.append(["F", "войти: %s (−%d)" % [_who_word(tgt), int(round(_enter_cost()))]])
	if claw >= 0:
		prompts.append(["ЛКМ", "%s (−%.0f)" % [CLAWS[claw]["name"], _claw_cost(claw)]])
	prompts.append(["1–5", "клешни"])


func _enter_cost() -> float:
	var cost := 8.0 + (20.0 if world.t_total - last_enter_t < 8.0 else 0.0)
	return cost * case.mem_mult


func _claw_cost(i: int) -> float:
	return float(CLAWS[i]["cost"]) * case.mem_mult * (0.75 if Game.has_perm("claws") else 1.0)


func _nearest_body(c: Vector2, r: float) -> Person:
	var best: Person = null
	var bd := r
	for q in world.people:
		if q.state != "ok" or q.inside != spirit.inside or not q.visible:
			continue
		var d: float = q.center().distance_to(c)
		if d < bd:
			bd = d
			best = q
	return best


func _thrown() -> void:
	## Плотность кончилась: духа швыряет в ближайшего человека, память рвётся.
	case.spend(18.0, "thrown")
	world.pstats["thrown"] = int(world.pstats.get("thrown", 0)) + 1
	var best: Person = null
	var bd := 1e9
	for q in world.people:
		if q.state != "ok" or q == case.target or q.brain == null or q.brain.away:
			continue
		var d: float = q.global_position.distance_to(spirit.global_position) + (0.0 if q.inside == spirit.inside else 400.0)
		if d < bd:
			bd = d
			best = q
	density = 35.0
	choke = {}
	Sfx.play("glitch", 0.0)
	world.view.shake = 1.5
	if best:
		enter(best, true)
		world.hud.voice("ПАМЯТЬ", "Свет выжег тебя. Швырнуло в первое попавшееся тело — и часть памяти осталась там.", Color(1.0, 0.55, 0.45))


func _swoop(dt: float) -> void:
	swoop["t"] = float(swoop["t"]) + dt / 0.28
	var p: Person = swoop["p"]
	var k := clampf(float(swoop["t"]), 0.0, 1.0)
	spirit.global_position = (swoop["from"] as Vector2).lerp(p.center() + Vector2(0, 8), k * k)
	if k >= 1.0:
		swoop = {}
		if p.state == "ok":
			var held: Dictionary = spirit.held
			enter(p, false)
			if held.get("kind", "") == "keys":
				for k2 in held["keys"]:
					if not (k2 in p.keys):
						p.keys.append(k2)
				say("Ключи — теперь в этом кармане.")
		else:
			spirit.visible = true


func _try_enter(q: Person) -> void:
	if q == null:
		return
	if q == case.target:
		say("Чужая воля слишком сильна. В цель не войти.")
		Sfx.play("glitch", -10.0)
		return
	if q.state != "ok":
		return
	swoop = {"from": spirit.global_position, "p": q, "t": 0.0}
	choke = {}


# ======================= клешни =======================

func _claw_target(at: Vector2) -> Dictionary:
	var s := spirit
	var c := s.center()
	var ok := at.distance_to(c) <= REACH
	var id: String = CLAWS[claw]["id"]
	# люди
	for q in world.people:
		if q.inside != s.inside or not q.visible or q.state in ["dead", "hidden", "carried", "gone"]:
			continue
		if absf(q.global_position.x - at.x) < 9.0 and at.y < q.global_position.y + 2 and at.y > q.global_position.y - 44:
			if id in ["tug", "move", "stun", "choke", "take"] and q.state in ["ok", "ko"]:
				if q.state == "ko" and id in ["stun", "move", "tug"]:
					continue
				return {"kind": "person", "ref": q, "text": _who_word(q), "ok": ok}
	# предметы
	var best := {}
	var bd := 14.0
	for o in city.objs:
		if o.has("inside") and bool(o["inside"]) != s.inside:
			continue
		var op := Vector2(float(o["x"]), float(o.get("y", 0.0)) - 10.0)
		var d := op.distance_to(at)
		if absf(op.x - at.x) < 14.0 and at.y < float(o.get("y", 0.0)) + 4 and at.y > float(o.get("y", 0.0)) - 36 and d < bd + 20:
			var t := _claw_obj_text(o, id)
			if t != "":
				bd = d
				best = {"kind": "obj", "ref": o, "text": t, "ok": ok}
	if not best.is_empty():
		return best
	if id == "tug":
		return {"kind": "point", "ref": at, "text": "стукнуть", "ok": ok}
	if id == "take" and not s.held.is_empty():
		return {"kind": "point", "ref": at, "text": "бросить", "ok": ok}
	return {}


func _claw_obj_text(o: Dictionary, id: String) -> String:
	match o["kind"]:
		"pot":
			if not o["fallen"] and id in ["tug", "move"]:
				return "столкнуть горшок"
		"movable":
			if not o["fallen"]:
				if id == "tug":
					return "дёрнуть: %s" % _what_word(o["what"])
				if id == "move":
					return "опрокинуть: %s" % _what_word(o["what"])
		"door":
			if id == "move" and not o["locked"]:
				return "закрыть дверь" if o["open"] else "открыть дверь"
			if id == "tug":
				return "постучать"
		"console":
			if id in ["tug", "move"]:
				return "нажать «сброс»"
		"fusebox":
			if id in ["tug", "move"]:
				return "дёрнуть рубильник"
		"transformer":
			if id == "tug":
				return "замкнуть подстанцию"
		"lockbox":
			if id == "take" and not o["open"]:
				return "вытащить ключ"
		"clue":
			if id == "take" and not o["taken"]:
				return "утащить: %s" % o["name"]
		"dumpster", "closet":
			if id == "tug":
				return "грохнуть"
	return ""


func _what_word(w: String) -> String:
	var m := {"urn": "урну", "chair": "стул", "shelf": "полку", "tv": "телевизор", "crate": "ящик", "bucket": "ведро",
		"cooler": "кулер", "flowerpot": "цветок", "lamp": "лампу", "filing": "шкаф", "coffeemachine": "кофеварку"}
	return m.get(w, "вещь")


func _apply_claw() -> void:
	var t := hover_claw
	if t.is_empty():
		return
	if not t["ok"]:
		say("Далеко. Клешня не дотянется.")
		return
	var id: String = CLAWS[claw]["id"]
	var cost := _claw_cost(claw)
	var at := mouse_w
	spirit.strike(at)
	Sfx.play("claw", -4.0)
	world.stats["claws"] += 1
	match t["kind"]:
		"point":
			if id == "tug":
				case.spend(cost, "claw_" + id)
				Sfx.play_at("thud", at, focus_pos(), -6.0)
				world.noise_at(at, 110.0, null, "knock")
			elif id == "take":
				spirit.held = {}
				say("Бросил.")
		"person":
			_claw_person(t["ref"], id, cost)
		"obj":
			_claw_obj(t["ref"], id, cost)


func _claw_person(q: Person, id: String, cost: float) -> void:
	match id:
		"tug":
			case.spend(cost, "claw_" + id)
			q.say(["Ай!", "Кто здесь?", "Что за…"][randi() % 3], 1.8)
			if q.brain:
				q.brain.distract(q.global_position + Vector2(-q.facing * 30, 0), 5.0)
			q.facing = -q.facing
			if q == case.target:
				world.target_alert += 6.0
		"take":
			if q.keys.is_empty():
				say("В карманах пусто.")
				return
			case.spend(cost, "claw_" + id)
			spirit.held = {"kind": "keys", "keys": q.keys.duplicate(), "name": "ключи: %s" % _who_word(q)}
			say("Связка ключей. Войди в тело — и она будет в его кармане.")
			Sfx.play("pickup", -6.0)
		"move":
			case.spend(cost, "claw_" + id)
			var dir := 1.0 if q.global_position.x > spirit.global_position.x else -1.0
			q.velocity = Vector2(dir * 170.0, -110.0)
			q.say("Ох!", 1.2)
			if q.brain:
				q.brain.react = {"kind": "look", "pos": spirit.global_position, "t": 2.5, "area": q.area}
			if q.area == "S" and world.car_near(q.global_position.x, 240.0):
				_road_kill(q, int(dir))
		"stun":
			case.spend(cost, "claw_" + id)
			q.knock_out(32.0)
			q.say("…", 1.0)
			Sfx.play("thud", -4.0)
			world.noise_at(q.global_position, 60.0, q, "fall")
		"choke":
			case.spend(cost, "claw_" + id)
			choke = {"victim": q, "t": 0.0}
			if q.brain:
				q.brain.react = {}


func _choke(dt: float) -> void:
	var q: Person = choke["victim"]
	if not is_instance_valid(q) or q.state == "dead" or q.center().distance_to(spirit.center()) > REACH + 10.0 or spirit.inside != q.inside:
		choke = {}
		say("Сорвалось.")
		return
	choke["t"] = float(choke["t"]) + dt
	spirit.strike(q.head_pos() + Vector2(0, 6))
	if q.state == "ok":
		q.move_x = 0.0
		q.pose = "choke"
		if q.brain:
			q.brain.react = {"kind": "look", "pos": q.global_position, "t": 0.6, "area": q.area}
	if fmod(float(choke["t"]), 0.9) < dt:
		Sfx.play("choke", -8.0, 0.8)
	if float(choke["t"]) >= 3.0:
		choke = {}
		q.pose = ""
		world.heat.append({"pos": q.global_position, "t": world.t_total})
		world.kill(q, "choke", null)


func _claw_obj(o: Dictionary, id: String, cost: float) -> void:
	var pos := Vector2(float(o["x"]), float(o.get("y", 0.0)))
	match o["kind"]:
		"pot":
			case.spend(cost, "claw_" + id)
			o["fallen"] = true
			_pot_fall(o)
		"movable":
			case.spend(cost, "claw_" + id)
			var n: Sprite2D = o["node"]
			if id == "move":
				o["fallen"] = true
				n.rotation = PI / 2.0 * (1 if randf() < 0.5 else -1)
				n.position.y -= 4
				Sfx.play_at("crash", pos, focus_pos(), -2.0)
				world.noise_at(pos, 170.0, null, "crash")
			else:
				var tw := n.create_tween()
				tw.tween_property(n, "rotation", 0.15, 0.06)
				tw.tween_property(n, "rotation", -0.12, 0.08)
				tw.tween_property(n, "rotation", 0.0, 0.06)
				Sfx.play_at("thud", pos, focus_pos(), -4.0)
				world.noise_at(pos, 120.0, null, "knock")
		"door":
			case.spend(cost, "claw_" + id)
			if id == "move":
				city.set_door(o, not o["open"])
				o["t_close"] = 0.0
				Sfx.play_at("door", pos, focus_pos(), -6.0)
				world.noise_at(pos, 60.0, null, "door")
			else:
				Sfx.play_at("thud", pos, focus_pos(), -2.0)
				world.noise_at(pos, 140.0, null, "knock")
		"console":
			case.spend(cost, "claw_" + id)
			var n2 := 0
			for t in case.open_tails():
				if String(t["id"]).begins_with("cam"):
					case.clear_tail(t["id"])
					n2 += 1
			Sfx.play("click", -2.0)
			say("Записи стёрты." if n2 > 0 else "Стирать нечего.")
		"fusebox":
			case.spend(cost, "claw_" + id)
			_fuse(o)
		"transformer":
			case.spend(cost, "claw_" + id)
			for l in city.lamps:
				if l["outer"] and absf((l["pos"] as Vector2).x - pos.x) < 520.0:
					l["off_t"] = world.t_total + 60.0
			Sfx.play_at("glitch", pos, focus_pos(), 0.0)
			world.noise_at(pos, 160.0, null, "crash")
			world.hud.voice("ГОРОД", "Подстанция треснула искрой. Фонари вокруг погасли.", Color(0.75, 0.78, 0.82))
		"lockbox":
			case.spend(cost, "claw_" + id)
			o["open"] = true
			(o["node"] as Sprite2D).frame = 1
			spirit.held = {"kind": "keys", "keys": (o["keys"] as Array).duplicate(), "name": "ключи из ящика"}
			say("Достал %s. Отдам телу." % o["what"])
			Sfx.play("pickup", -6.0)
		"clue":
			case.spend(cost, "claw_" + id)
			o["taken"] = true
			(o["node"] as Node2D).visible = false
			case.learn(o["card"], 100.0, "улика")
			world.hud.card_toast(case.card(o["card"]), o["name"], o["text"])
			Sfx.play("paper", -4.0)
		"dumpster", "closet":
			case.spend(cost, "claw_" + id)
			Sfx.play_at("crash", pos, focus_pos(), -4.0)
			world.noise_at(pos, 150.0, null, "crash")


func _pot_fall(o: Dictionary) -> void:
	var n: Sprite2D = o["node"]
	var x := float(o["x"])
	var gy := K.floor_y(0)
	var tw := n.create_tween()
	var dur := sqrt(maxf(1.0, gy - n.position.y) / 450.0)
	tw.tween_property(n, "position:y", gy, dur).set_trans(Tween.TRANS_QUAD).set_ease(Tween.EASE_IN)
	tw.tween_callback(func():
		n.frame = mini(1, n.hframes - 1)
		Sfx.play_at("crash", n.position, focus_pos(), 0.0)
		world.noise_at(n.position, 160.0, null, "crash")
		for q in world.people:
			if q.state == "ok" and not q.inside and absf(q.global_position.x - x) < 10.0 and absf(q.global_position.y - gy) < 6.0:
				world.kill(q, "pot", null)
				break)


# ======================= ввод =======================

func _unhandled_input(e: InputEvent) -> void:
	if world.over or world.paused or not swoop.is_empty():
		return
	if world.hud and world.hud.modal():
		return
	if e is InputEventKey and e.pressed and not e.echo:
		var k: Key = e.physical_keycode
		if host:
			_body_key(k)
		else:
			_spirit_key(k)
	if e is InputEventKey and not e.pressed and e.physical_keycode == KEY_R:
		emergency_t = 0.0
	if e is InputEventMouseButton and e.pressed and not host:
		if e.button_index == MOUSE_BUTTON_LEFT:
			if claw >= 0:
				_apply_claw()
			elif hover:
				_try_enter(hover)
		elif e.button_index == MOUSE_BUTTON_RIGHT:
			claw = -1


func _body_key(k: Key) -> void:
	var p := host
	match k:
		KEY_SPACE:
			if p.climbing:
				p.climb_stop()
			elif strangle.is_empty():
				p.want_jump = true
		KEY_W, KEY_UP:
			if not act_w.is_empty() and not p.climbing:
				_do(act_w)
		KEY_S, KEY_DOWN:
			if not act_s.is_empty() and not p.climbing:
				_do(act_s)
		KEY_E:
			if not act_e.is_empty():
				_do(act_e)
		KEY_Q:
			if not act_q.is_empty() and strangle.is_empty():
				_hands(act_q)
		KEY_G:
			if act_g.get("kind", "") == "pick":
				_pick(act_g["who"])
			elif act_g.get("kind", "") == "drop" and p.carrying:
				var c := p.carrying
				p.carrying = null
				c.drop_from(p)
				_dropped(c)
				Sfx.play("thud", -6.0)
		KEY_F:
			leave(true)
		KEY_T:
			if world.susp > 5.0 or not strangle.is_empty() or absf(p.velocity.x) > 1.0:
				say("Не сейчас: на тебя смотрят.")
			else:
				wait_i = (wait_i + 1) % SPEEDS.size()
				world.env.speed = SPEEDS[wait_i]


func _spirit_key(k: Key) -> void:
	match k:
		KEY_1, KEY_2, KEY_3, KEY_4, KEY_5:
			var i := int(k - KEY_1)
			claw = -1 if claw == i else i
			Sfx.play("ui", -10.0)
		KEY_ESCAPE:
			pass
		KEY_W, KEY_UP:
			if not act_w.is_empty():
				spirit.go_portal(act_w["p"], act_w["dir"])
		KEY_S, KEY_DOWN:
			if not act_s.is_empty():
				spirit.go_portal(act_s["p"], act_s["dir"])
		KEY_E:
			if not act_e.is_empty():
				spirit.go_portal(act_e["p"], act_e["dir"])
		KEY_F:
			_try_enter(hover if hover else _nearest_body(spirit.center(), 60.0))
		KEY_T:
			say("Вне тела время не ждёт.")


func _physics_process(dt: float) -> void:
	# экстренная линия: держать R у таксофона
	if host and not world.over and _key(KEY_R) and _payphone_near(host):
		emergency_t += dt
		if emergency_t >= 1.6:
			emergency_t = 0.0
			world.emergency_line()
