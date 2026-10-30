extends Node
## Игра одного дела: район, люди, цель, восприятие, свидетели, милиция, выход через таксофон.

var main: Node
var case_seed := 0
var city: City
var env: Env
var view: View
var case: Case
var hud: Node
var player: PlayerCtl
var people: Array = []
var t_total := 0.0
var rng := RandomNumberGenerator.new()
var cars: Array = []
var car_t := 2.0
var train := {}
var train_t := 30.0
var dog: Dog
var birds: Array = []
var witnesses: Array = []          # {who, t, what, pos}
var police: Array = []
var police_state := ""             # "", coming, here
var police_t := 0.0
var police_target := Vector2.ZERO
var police_car: Sprite2D
var alarm_count := 0
var susp := 0.0                    # подозрение к текущему телу
var susp_why := ""
var perc_t := 0.0
var over := false
var result := {}
var talks: Array = []
var gossip_people := {}            # pid -> [card id, line]
var told := {}                     # "pid:host" -> true (информатор уже говорил с этим телом)
var exit_ring := {}
var lamp_t := 0.0
var events_t := 30.0
var blackouts: Array = []
var paused := false
var brief := false
var start_h := 7.8
var target_alert := 0.0
var target_spooked := 0
var heat: Array = []               # следы удушения духом
var look_x := 0.0
var talk_mem := {}                 # pid -> память собеседника (черты, настроение к телам, о чём спрашивали)
var greeted_by := {}               # "pid:тело" -> сосед уже здоровался
var greet_wait := {}               # pid соседа -> секунд, пока он ждёт ответного «здравствуйте»
var rumours: Array = []            # [ключ, заголовок, текст] — слухи о районе
var rumours_told := {}
var talk_after := {}
var grudge_t := 2.0
var pstats := {"thrown": 0, "witness": 0, "talks": 0, "max_susp": 0.0, "min_density": 100.0, "body_s": 0.0, "spirit_s": 0.0}
var grudge_said := {}               # что делает собеседник, когда разговор кончился
var stats := {"jumps": 0, "claws": 0, "kills": 0, "extra_dead": 0}


func _ready() -> void:
	if case_seed == 0:
		case_seed = randi() % 900000 + 1000
	rng.seed = case_seed
	city = City.new()
	city.build(case_seed)
	city.room_lamps()
	env = Env.new()
	add_child(env)
	env.setup(case_seed, start_h, float(Game.d("hour_s")))
	var cl := CanvasLayer.new()
	cl.layer = 0
	add_child(cl)
	view = View.new()
	cl.add_child(view)
	view.setup(city, env)
	view.set_anchors_preset(Control.PRESET_TOP_LEFT)
	view.size = Vector2(1920, 1080)
	case = Case.new()
	case.generate(case_seed, city)
	_spawn_people()
	rumours = _make_rumours()
	_items_in_home()
	dog = Dog.new()
	dog.setup(self, city)
	city.people.add_child(dog)
	_birds()
	player = PlayerCtl.new()
	player.world = self
	add_child(player)
	player.setup()
	hud = load("res://src/ui/hud.gd").new()
	hud.world = self
	add_child(hud)
	_start_body()
	env.tick(0.0)
	_lamps(true)
	view.snap_to(player.focus_pos())
	if brief:
		hud.open_brief()


# ======================= население =======================

func _new_person(lk: Dictionary, prof: String, female: bool) -> Person:
	var p := Person.new()
	p.prof = prof
	p.female = female
	p.first = (Looks.FEMALE if female else Looks.MALE)[rng.randi() % (Looks.FEMALE if female else Looks.MALE).size()]
	var sur: String = Looks.SURNAMES[rng.randi() % Looks.SURNAMES.size()]
	p.last = sur + "а" if female else sur
	city.people.add_child(p)
	p.setup(self, city, people.size(), lk)
	p.base_speed = rng.randf_range(40.0, 56.0) if lk.get("age", 1) < 2 else rng.randf_range(28.0, 36.0)
	if lk.get("age", 1) == 2 and rng.randf() < 0.5:
		p.gait = "hunch"
	Brain.new(p, self)
	people.append(p)
	return p


func _apartments() -> Array:
	var out := []
	for b in city.buildings:
		if b["kind"] != "res":
			continue
		for f in b["floors"]:
			if int(f) < 0:
				continue
			for apt in b["floors"][f]:
				if int(b["id"]) == int(case.p["home_bid"]) and int(apt) == int(case.p["apt"]):
					continue
				out.append({"bid": b["id"], "f": int(f), "apt": apt})
	out.shuffle()
	return out


func _apt_spots(a: Dictionary) -> Dictionary:
	## Точки квартиры по меткам комнат: диван, кровать, плита, стул на кухне.
	var b: Dictionary = city.buildings[int(a["bid"])]
	var out := {"area": city.area_of_floor(int(a["bid"]), int(a["f"]))}
	for rid in b["rooms"]:
		var rm: Dictionary = city.rooms[rid]
		if int(rm["apt"]) != int(a["apt"]) or int(rm["f"]) != int(a["f"]):
			continue
		for sp in rm["spots"]:
			var k: String = sp["kind"]
			if k in ["sofa", "bed", "stove"] and not out.has(k):
				out[k] = float(sp["x"])
			elif k == "sit" and rm["kind"] == "kitchen":
				out["sit"] = float(sp["x"])
	if out.has("sofa") and not out.has("bed"):
		out["bed"] = out["sofa"]
	if out.has("bed") and not out.has("sofa"):
		out["sofa"] = out["bed"]
	return out


func _room_spot(kind: String, idx: int = 0) -> Dictionary:
	var n := 0
	for rm in city.rooms:
		for s in rm["spots"]:
			if s["kind"] == kind:
				if n == idx:
					var b := int(rm["bid"])
					var area: String = city.area_of_floor(b, int(rm["f"])) if b >= 0 else {"collector": "C", "drain": "D"}.get(rm["kind"], "M")
					return {"area": area, "x": float(s["x"]), "bid": b, "f": rm["f"]}
				n += 1
	return {}


func _office_desks(name: String) -> Array:
	var b := city.b_named(name)
	var out := []
	for rid in b["rooms"]:
		var rm: Dictionary = city.rooms[rid]
		if rm["kind"] == "office":
			for s in rm["spots"]:
				out.append({"area": city.area_of_floor(int(b["id"]), int(rm["f"])), "x": float(s["x"])})
	out.shuffle()
	return out


func S(h: float, pl: Dictionary, act: String, dx: float = 0.0) -> Dictionary:
	return {"h": h, "area": pl["area"], "x": float(pl["x"]) + dx, "act": act, "name": pl.get("name", "")}


func _spawn_people() -> void:
	var apts := _apartments()
	var ai := 0
	var total := int(Game.d("people"))
	var desks_g := _office_desks("Гранит")
	var desks_n := _office_desks("НИИ")
	var P: Dictionary = city.places
	var roles := ["vendor", "barista", "pharm", "cashier", "cashier", "guard", "guard", "janitor", "pensioner", "pensioner",
		"pensioner", "pensioner", "student", "student", "student", "worker", "worker", "worker", "courier", "teacher", "tramp"]
	for i in desks_g.size() + desks_n.size():
		roles.append("office")
	while roles.size() < total:
		roles.append(["resident", "pensioner", "worker", "student"][rng.randi() % 4])
	var gi := 0
	var ni := 0
	var guard_n := 0
	var cash_n := 0
	for role in roles:
		var female := rng.randf() < 0.5
		if role in ["barista", "cashier", "pharm", "teacher"]:
			female = rng.randf() < 0.85
		if role in ["guard", "worker"]:
			female = rng.randf() < 0.1
		var age := 2 if role == "pensioner" else (0 if role == "student" else 1)
		var lk := Looks.random_look(rng, female, age, role)
		var p := _new_person(lk, role, female)
		var home := {}
		if ai < apts.size() and role != "tramp":
			home = _apt_spots(apts[ai])
			p.keys.append("apt%d_%d" % [apts[ai]["bid"], apts[ai]["apt"]])
			p.home = apts[ai]
			ai += 1
		var commuter := home.is_empty() or not home.has("sofa")
		var hm := {"area": home.get("area", "M"), "x": home.get("sofa", 0.0), "name": "Дом"}
		var hk := {"area": home.get("area", "M"), "x": home.get("stove", home.get("sofa", 0.0)), "name": "Дом"}
		var s: Array = []
		var r := rng.randf_range(-0.4, 0.4)
		var errands := ["Киоск", "Универсам", "Сквер", "Двор", "Остановка", "Гаражи", "Площадка"]
		var e1: Dictionary = P[errands[rng.randi() % errands.size()]]
		var e2: Dictionary = P[errands[rng.randi() % errands.size()]]
		var lunch: Dictionary = [P["Кафе"], P["Сквер"], P["Универсам"]][rng.randi() % 3]
		var dx := rng.randf_range(-40, 40)
		var metro: Dictionary = P["Метро"]
		match role:
			"vendor":
				s = [S(6, hm, "sofa"), S(7.2, P["Киоск"], "work", -30), S(19.5, hk, "stove"), S(21, hm, "sofa")]
			"barista":
				var sp := _room_spot("barista")
				s = [S(6, hm, "sofa"), S(7.6, sp, "barista"), S(20.5, hk, "stove"), S(22, hm, "bed")]
			"pharm":
				var sp2 := _room_spot("cashier", 1)
				s = [S(6, hm, "sofa"), S(8.0, sp2, "cashier"), S(19.2, hk, "stove"), S(21.5, hm, "bed")]
			"cashier":
				var sp3 := _room_spot("cashier", 0 if cash_n == 0 else 1)
				if cash_n == 1:
					sp3 = _room_spot("shop", 1)
				cash_n += 1
				s = [S(6, hm, "sofa"), S(7.8, sp3, "cashier"), S(20.3, hk, "stove"), S(22, hm, "bed")]
			"guard":
				var b := city.b_named("Гранит" if guard_n == 0 else "НИИ")
				var lob := {"area": city.area_of_floor(int(b["id"]), 0), "x": float(b["px0"]) + 3 * K.T + 4}
				guard_n += 1
				p.keys.append("sec%d" % b["id"])
				p.keys.append("roof%d" % b["id"])
				p.keys.append("fire%d" % b["id"])
				s = [S(6, hm, "sofa"), S(7.4, lob, "guard"), S(10.5, P["Задворки"], "smoke"), S(10.8, lob, "guard"), S(20.5, hk, "stove"), S(22, hm, "bed")]
				p.set_meta("post", b["id"])
			"janitor":
				for b2 in city.buildings:
					p.keys.append("base%d" % b2["id"])
					p.keys.append("roof%d" % b2["id"])
				p.keys.append("grate")
				s = [S(6, hm, "sofa"), S(6.8, P["Двор"], "work"), S(9, P["Задворки"], "work"), S(11, P["Гаражи"], "work"),
					S(13, hk, "sit"), S(14.5, P["Площадка"], "work"), S(16.5, P["Сквер"], "work"), S(18.5, hk, "stove"), S(21, hm, "bed")]
			"pensioner":
				s = [S(6, hm, "sofa"), S(9 + r, P["Сквер"], "sit", dx), S(11 + r, P["Универсам"], "shop", dx), S(12.2 + r, hk, "sit"),
					S(14.5 + r, [P["Двор"], P["Площадка"], P["Сквер"]][rng.randi() % 3], "sit", dx), S(17.5 + r, hm, "sofa"), S(22, hm, "bed")]
			"student":
				s = [S(6, hm, "bed"), S(8.2 + r, metro, "away"), S(15 + r, P["Площадка"], "idle", dx), S(17 + r, e1, "idle", dx),
					S(19 + r, hk, "sit"), S(20.5 + r, hm, "sofa")]
			"worker":
				s = [S(6, hm, "bed"), S(7.0 + r, metro, "away"), S(17.4 + r, e1, "idle", dx), S(18.5 + r, P["Гаражи"], "smoke", dx),
					S(19.3 + r, hk, "stove"), S(21 + r, hm, "sofa")]
			"courier":
				s = [S(6, hm, "sofa"), S(8.5, e1, "idle"), S(9.6, P["Универсам"], "idle"), S(10.7, e2, "idle"), S(12, P["Кафе"], "eat"),
					S(13.2, P["Остановка"], "idle"), S(14.4, e1, "idle"), S(15.6, P["Гаражи"], "idle"), S(17, hk, "stove"), S(19, hm, "sofa")]
				p.base_speed = 64.0
			"tramp":
				# бродяга живёт в дренаже: знает подземелье и видит, кто туда спускается
				p.keys.append("grate")
				s = [S(0, P["Лежанка"], "sit"), S(8.5 + r, P["Насосная"], "idle"), S(10 + r, P["Гаражи"], "smoke", dx),
					S(12.5 + r, P["Универсам"], "idle", dx), S(14 + r, P["Сквер"], "sit", dx), S(18.5 + r, P["Гаражи"], "smoke", dx),
					S(20.5 + r, P["Лежанка"], "sit")]
				p.base_speed = 34.0
				commuter = false
			"teacher":
				s = [S(6, hm, "sofa"), S(8.0, metro, "away"), S(16 + r, P["Универсам"], "shop", dx), S(17 + r, hk, "stove"), S(20, hm, "sofa")]
			"office":
				var desk: Dictionary
				var wname := "Гранит"
				if gi < desks_g.size():
					desk = desks_g[gi]
					gi += 1
				else:
					desk = desks_n[ni]
					ni += 1
					wname = "НИИ"
				p.set_meta("work", wname)
				if commuter:
					s = [S(6, metro, "away"), S(8.4 + r, desk, "desk"), S(12.8 + r, lunch, "eat", dx), S(13.6 + r, desk, "desk"),
						S(17.8 + r, metro, "away")]
				else:
					s = [S(6, hm, "sofa"), S(8.0 + r, e1, "idle", dx), S(8.9 + r, desk, "desk"), S(12.8 + r, lunch, "eat", dx), S(13.6 + r, desk, "desk"),
						S(17.6 + r, e2, "idle", dx), S(18.6 + r, hk, "stove"), S(20 + r, hm, "sofa"), S(23, hm, "bed")]
			_:
				s = [S(6, hm, "sofa"), S(9 + r, e1, "idle", dx), S(10.5 + r, hk, "stove"), S(13 + r, P["Универсам"], "shop", dx),
					S(14 + r, hm, "sofa"), S(16 + r, e2, "idle", dx), S(18 + r, hk, "stove"), S(20 + r, hm, "sofa"), S(23, hm, "bed")]
		if commuter and role != "office":
			for e in s:
				if e["area"] == "M" and e["act"] in ["sofa", "bed", "stove", "sit"]:
					e["act"] = "away"
		p.brain.sched = s
		_place_at_goal(p)
		# разговорчивые соседи и коллеги знают о цели
		var nb := not home.is_empty() and int(p.home.get("bid", -1)) == int(case.p["home_bid"])
		var colleague: bool = role == "office" and p.get_meta("work", "") == ("Гранит" if case.p["work"] == "Офис" else "НИИ")
		if nb or colleague or role == "tramp" or (role == "pensioner" and rng.randf() < 0.5):
			var gl := case.gossip_line()
			gossip_people[p.pid] = [gl[0], Case.voiced(gl[1], p.female)]
	# цель
	var tp := _new_person(case.p["look"], "office", case.p["female"])
	tp.first = case.p["first"]
	tp.last = case.p["last"]
	tp.gait = case.p["sig"]
	tp.base_speed = 44.0
	tp.keys.append("apt%d_%d" % [case.p["home_bid"], case.p["apt"]])
	tp.home = {"bid": case.p["home_bid"], "f": case.p["home_f"], "apt": case.p["apt"]}
	tp.brain.sched = case.brain_sched(case.p["sched"])
	tp.brain.is_target = true
	case.target = tp
	_place_at_goal(tp)
	# двойники
	for i in int(Game.d("decoys")):
		var lk2 := case.decoy_look(i)
		var dp := _new_person(lk2, "office", case.p["female"])
		dp.gait = case.decoy_gait(i)
		dp.base_speed = 44.0
		dp.brain.sched = case.decoy_sched(i)
		dp.set_meta("decoy", true)
		_place_at_goal(dp)
		case.decoys.append(dp)


func bname(b: Dictionary) -> String:
	## Как жители называют дом: «Гранит» или «кирпичная двенадцатиэтажка».
	if b["name"] != "":
		return "«%s»" % b["name"]
	var adj: String = {"panel": "панельная", "brick": "кирпичная", "sbrick": "кирпичная", "stucco": "жёлтая"}.get(b["mat"], "серая")
	var words := {5: "пяти", 6: "шести", 7: "семи", 8: "восьми", 9: "девяти", 10: "десяти", 11: "одиннадцати", 12: "двенадцати",
		13: "тринадцати", 14: "четырнадцати", 15: "пятнадцати", 16: "шестнадцати"}
	return "%s %sэтажка" % [adj, words.get(int(b["n"]), "много")]


func _cap(t: String) -> String:
	return t.substr(0, 1).to_upper() + t.substr(1)


func _make_rumours() -> Array:
	var out := []
	for b in city.buildings:
		if b["kind"] == "res" and b["basement"]:
			out.append(["lock%d" % b["id"], "Слух: ключи", "%s: в подвале ящик с ключами от крыши. Замок — смех один." % _cap(bname(b))])
		if b.get("lift_broken", false):
			out.append(["lift%d" % b["id"], "Слух: лифт", "%s: лифт опять стоит. Все пешком по лестнице." % _cap(bname(b))])
		for f in b["bridge_r"]:
			var nb := city.building_at(float(int(b["x0"]) + int(b["w"]) + 6) * K.T)
			if not nb.is_empty():
				out.append(["br%d_%d" % [b["id"], f], "Слух: переход", "Между домами переход на %d-м этаже: %s и %s. Можно пройти, не выходя на улицу." % [int(f) + 1, bname(b), bname(nb)]])
	out.append(["pump", "Слух: насосная", "В дренаже, в насосной, ящик обходчика. Там ключи от решёток коллектора и от служебки метро."])
	out.append(["jan", "Слух: дворник", "У дворника ключи от всех подвалов и чердаков. С утра он во дворе метёт."])
	out.append(["guard", "Слух: охрана", "Охранник «Гранита» в пол-одиннадцатого курит на задворках. Пост в это время пустой."])
	out.append(["steam", "Слух: коллектор", "В коллекторе трубы гнилые, паром бьёт. Не суйся туда без нужды."])
	for pt in city.portals:
		if pt["kind"] == "passage":
			out.append(["pass", "Слух: подвалы", "Подвалы соседних домов насквозь проходные. Можно уйти, не показываясь на улице."])
			break
	for pt in city.portals:
		if pt["kind"] == "roofladder":
			out.append(["roofl", "Слух: крыши", "Мальчишки с крыши на крышу по лестницам лазают. Высоко, а им хоть бы что."])
			break
	return out


func _place_at_goal(p: Person) -> void:
	var g := p.brain.current_goal(env.hour)
	if g.is_empty():
		return
	p.brain.goal = g
	if g["act"] == "away":
		p.area = "M"
		p.set_inside(true)
		var a: Dictionary = city.areas["M"]
		p.global_position = Vector2(float(a["x0"]) + 60, float(a["y"]))
		p.brain._go_away()
		return
	p.area = g["area"]
	var a2: Dictionary = city.areas[p.area]
	p.set_inside(a2["inside"])
	p.global_position = Vector2(clampf(float(g["x"]) + rng.randf_range(-20, 20), float(a2["x0"]), float(a2["x1"])), float(a2["y"]) - 1)
	p.brain.arrived = false


func _items_in_home() -> void:
	## Улики в квартире цели и ключ под ковриком.
	var rm: Dictionary = case.p["living"]
	var rk: Dictionary = case.p["kitchen"]
	var y := float(rm["y"])
	var i := 0
	for it in case.item_cards():
		var host_rm: Dictionary = rm if i % 2 == 0 else rk
		var x := lerpf(float(host_rm["x0"]) + 18, float(host_rm["x1"]) - 18, rng.randf())
		x = city.unwall(x, y, (float(host_rm["x0"]) + float(host_rm["x1"])) / 2.0)
		var s := Res.prop_sprite(it[0])
		s.position = Vector2(x, y - (22 if i % 3 == 0 else 0))
		s.visibility_layer = K.V_INNER
		city.furn.add_child(s)
		city.objs.append({"kind": "clue", "node": s, "x": x, "y": y, "card": it[1], "name": it[2], "text": it[3], "inside": true,
			"bid": case.p["home_bid"], "f": case.p["home_f"], "taken": false})
		i += 1


func _birds() -> void:
	for pl in ["Сквер", "Двор", "Гаражи"]:
		for i in 3:
			var b := Bird.new()
			b.setup("pigeon" if pl != "Гаражи" else "crow", Vector2(float(city.places[pl]["x"]) + rng.randf_range(-60, 60), K.floor_y(0)))
			city.sprops.add_child(b)
			birds.append(b)


func _start_body() -> void:
	## Дух спускается в случайного прохожего на улице.
	var cands := people.filter(func(p): return p.state == "ok" and not p.inside and p != case.target and not p.has_meta("decoy"))
	if cands.is_empty():
		cands = people.filter(func(p): return p.state == "ok" and p != case.target)
	var sq: float = city.places["Сквер"]["x"]
	cands.sort_custom(func(a, b): return absf(a.global_position.x - sq) < absf(b.global_position.x - sq))
	player.enter(cands[0], true)


# ======================= цикл =======================

func _process(dt: float) -> void:
	if over or paused:
		return
	var sp := env.speed if player.host else minf(env.speed, 1.0)
	env.tick(dt)
	t_total += dt
	for p in people:
		if p.brain:
			p.brain.tick(dt)
	_underworld(dt)
	pstats["max_susp"] = maxf(float(pstats["max_susp"]), susp)
	if player.host:
		pstats["body_s"] = float(pstats["body_s"]) + dt
	else:
		pstats["spirit_s"] = float(pstats["spirit_s"]) + dt
		pstats["min_density"] = minf(float(pstats["min_density"]), player.density)
	grudge_t -= dt
	if grudge_t <= 0.0:
		grudge_t = 1.5
		_grudges()
	perc_t -= dt
	if perc_t <= 0.0:
		perc_t = 0.2
		_perceive(0.2)
	lamp_t -= dt
	if lamp_t <= 0.0:
		lamp_t = 0.5
		_lamps(false)
	_doors(dt)
	_cars(dt)
	_train(dt)
	_witnesses(dt)
	_police(dt)
	_exit(dt)
	_events(dt)
	_target_watch(dt)
	if player.host:
		case.regen(dt * sp)
	_check_end()
	var fp := player.focus_pos()
	# взгляд вперёд: сдвиг камеры по направлению движения нарастает плавно и только на ходу,
	# поворот на месте камеру не дёргает
	var mv := player.host.velocity.x if player.host else player.spirit.velocity.x
	if absf(mv) > 6.0:
		look_x = move_toward(look_x, signf(mv) * 36.0, dt * 30.0)
	view.cam_target = fp + Vector2(look_x, -64.0)
	var inside := player.focus_inside()
	view.viewer_inside = inside
	view.viewer_bid = city.building_at(fp.x).get("id", -1) if inside and fp.y < K.floor_y(0) + 4 else -1
	view.viewer_under = fp.y > K.floor_y(0) + 8
	_audio(dt)


func _audio(dt: float) -> void:
	var under := view.viewer_under
	var ins := view.viewer_inside
	Sfx.loop_level("city", 0.0 if under else (0.18 if ins else 0.4), dt)
	Sfx.loop_level("rain", env.rain * (0.15 if ins or under else 0.5), dt)
	Sfx.loop_level("under", 0.35 if under else 0.0, dt)
	Sfx.loop_level("spirit", 0.5 if not player.host else 0.0, dt)
	Sfx.music(_music_theme(), dt)
	Sfx.loop_level("heart", clampf((susp - 40.0) / 60.0, 0.0, 1.0) * 0.7 if player.host else clampf((40.0 - player.density) / 40.0, 0.0, 1.0) * 0.6, dt)
	var high := player.focus_pos().y < K.floor_y(4)
	Sfx.loop_level("wind", 0.25 if high and not ins else 0.0, dt)


# ======================= двери, свет =======================

func _doors(dt: float) -> void:
	for d in city.doors:
		if d["open"] and float(d["t_close"]) > 0.0:
			d["t_close"] = float(d["t_close"]) - dt
			if float(d["t_close"]) <= 0.0:
				# не закрывать, если кто-то стоит в проёме
				var busy := false
				for p in people:
					if p.inside and absf(p.global_position.x - float(d["x"])) < 10 and absf(p.global_position.y - float(d["y"])) < 20:
						busy = true
				if player.host and absf(player.host.global_position.x - float(d["x"])) < 10 and absf(player.host.global_position.y - float(d["y"])) < 20:
					busy = true
				if busy:
					d["t_close"] = 1.0
				else:
					city.set_door(d, false)


func door_between(p: Person, x0: float, x1: float) -> Dictionary:
	if not p.inside:
		return {}
	var a := minf(x0, x1)
	var b := maxf(x0, x1)
	var y := p.global_position.y
	var best := {}
	var bd := 1e9
	for d in city.doors:
		if d["open"]:
			continue
		if absf(float(d["y"]) - y) > 20:
			continue
		var dx := float(d["x"])
		if dx > a - 2 and dx < b + 2:
			var dd := absf(dx - x0)
			if dd < bd:
				bd = dd
				best = d
	return best


func open_door(d: Dictionary, by: Person) -> void:
	if d["open"]:
		d["t_close"] = 3.0
		return
	city.set_door(d, true)
	d["t_close"] = 3.0
	Sfx.play_at("door", Vector2(float(d["x"]), float(d["y"])), player.focus_pos(), -6.0)


func portal_unlocked(pt: Dictionary) -> bool:
	return pt.get("opened", false)


func _music_theme() -> String:
	## Тема по времени суток; тревога — свидетель, милиция, звонок на выход, подозрение или тающий дух.
	var ringing := false
	for o in city.objs:
		if o["kind"] == "payphone" and o["ring"]:
			ringing = true
			break
	var alarmed := witnesses.any(func(w): return not w["done"])
	if ringing or alarmed or police_state != "" and police_state != "gone" or susp > 60.0 or (not player.host and player.density < 25.0):
		return "tension"
	var h := fmod(env.hour, 24.0)
	if h >= 5.0 and h < 11.0:
		return "morning"
	if h >= 11.0 and h < 17.0:
		return "day"
	if h >= 17.0 and h < 22.0:
		return "evening"
	return "night"


func _underworld(dt: float) -> void:
	## Коллектор живёт: пар бьёт из труб, крысы бегают вдоль стен.
	for st in city.steams:
		st["t"] = float(st["t"]) - dt
		if float(st["t"]) <= 0.0:
			st["on"] = not st["on"]
			st["t"] = randf_range(1.6, 2.6) if st["on"] else randf_range(5.0, 10.0)
			(st["node"] as Sprite2D).visible = st["on"]
			if st["on"]:
				Sfx.play_at("steam", Vector2(float(st["x"]), float(st["y"])), player.focus_pos(), -8.0)
		if st["on"]:
			var sp := st["node"] as Sprite2D
			sp.frame = int(t_total * 10.0) % sp.hframes
	for r in city.rats:
		var n := r["node"] as Sprite2D
		var x := n.position.x + float(r["v"]) * dt
		if x < float(r["x0"]) or x > float(r["x1"]):
			r["v"] = -float(r["v"])
			x = clampf(x, float(r["x0"]), float(r["x1"]))
		n.position.x = x
		n.flip_h = float(r["v"]) < 0.0
		n.frame = int(t_total * 8.0) % n.hframes


func _grudges() -> void:
	## Обиды живут дольше тела: дух ушёл, а человек получает за то, чего не помнит.
	for pid in talk_mem:
		var m: Dictionary = talk_mem[pid]
		if (m["grudge"] as Dictionary).is_empty():
			continue
		var q: Person = people[int(pid)]
		if q.state != "ok" or q.host:
			continue
		for hk in m["grudge"]:
			var b: Person = people[int(hk)]
			if b.host or b.state != "ok" or b.area != q.area or grudge_said.has("%s:%s" % [pid, hk]):
				continue
			if b.global_position.distance_to(q.global_position) > 60.0:
				continue
			grudge_said["%s:%s" % [pid, hk]] = true
			q.facing = 1 if b.global_position.x > q.global_position.x else -1
			q.say(["Явил%s… После того, как %s!" % ["ась" if b.female else "ся", m["grudge"][hk]], "Глаза бы мои тебя не видели."][rng.randi() % 2], 3.5, Color(1.0, 0.75, 0.6))
			var bb := b
			get_tree().create_timer(1.6).timeout.connect(func(): if is_instance_valid(bb) and bb.state == "ok": bb.say(["Я? Что я сделал%s?" % ("а" if bb.female else ""), "Вы о чём вообще?", "Не помню такого…"][randi() % 3], 3.0))


func steam_at(pos: Vector2) -> bool:
	for st in city.steams:
		if st["on"] and absf(pos.x - float(st["x"])) < 18.0 and absf(pos.y - float(st["y"])) < 40.0:
			return true
	return false


func _lamps(force: bool) -> void:
	var on := env.lamps_on()
	var h := fmod(env.hour, 24.0)
	for l in city.lamps:
		var lit := true
		if l["outer"]:
			lit = on
		elif l["kind"] == "room":
			lit = _room_lit(l, h)
		if float(l["off_t"]) > t_total:
			lit = false
		if l.get("broken", false):
			# битая лампа в коллекторе: изредка вспыхивает
			lit = fmod(t_total * 1.3 + float((l["pos"] as Vector2).x) * 0.01, 6.0) < 0.5
		if l["bid"] >= 0:
			for bo in blackouts:
				if int(bo["bid"]) == int(l["bid"]) and float(bo["until"]) > t_total:
					lit = false
		if lit != l["on"] or force:
			l["on"] = lit
			(l["light"] as Sprite2D).visible = lit
			if l["node"] and (l["node"] as Sprite2D).hframes > 1:
				(l["node"] as Sprite2D).frame = 1 if lit else 0


func _room_lit(l: Dictionary, h: float) -> bool:
	if not l.has("room"):
		return env.night > 0.2
	var rm: Dictionary = city.rooms[int(l["room"])]
	var k: String = rm["kind"]
	if k in ["office", "lobby", "security"]:
		return h >= 8.0 and h < 19.5 and env.night > 0.2 or (k in ["lobby", "security"] and env.night > 0.2)
	if k in ["store", "pharmacy", "cafe", "kitchen_cafe", "metro"]:
		return env.night > 0.15 and h >= 7.5 and h < 21.0
	if k in ["storage"]:
		return false
	# квартиры: свет, если кто-то дома и темно
	if env.night < 0.25:
		return false
	if rm.has("occ_t") and float(rm["occ_t"]) > t_total:
		return true
	var seed_v := int(rm["id"]) * 7919
	var on_h := 18.0 + float(seed_v % 7) * 0.4
	var off_h := 22.0 + float(seed_v % 5) * 0.5
	return (seed_v % 10) < 6 and (h >= on_h and h < off_h or h < 6.5 and (seed_v % 10) < 1)


func light_at(pos: Vector2, inside: bool) -> float:
	## Насколько освещена точка (0 темно .. 1 светло): для глаз прохожих и камер.
	var v := 0.0
	if not inside:
		v = 1.0 - env.night * 0.85
	else:
		if pos.y > K.floor_y(0) + 8:
			v = 0.1
		else:
			v = 1.0 - env.night * 0.8
	for l in city.lamps:
		if not l["on"] or bool(l["outer"]) != (not inside) and l["kind"] != "room":
			continue
		var lp: Vector2 = l["pos"]
		if absf(lp.x - pos.x) > 420.0:
			continue
		var r := float(l["r"])
		if l["kind"] == "room" and l.has("room"):
			var rm: Dictionary = city.rooms[int(l["room"])]
			if inside and pos.x >= float(rm["x0"]) and pos.x <= float(rm["x1"]) and absf(pos.y - float(rm["y"])) < 70:
				v = maxf(v, 0.85)
			continue
		var d := lp.distance_to(pos)
		if d < r:
			v = maxf(v, 1.0 - d / r * 0.6)
	return clampf(v, 0.0, 1.0)


func lamp_burn(pos: Vector2, inside: bool) -> float:
	## Свет, который жжёт духа: фонари и голые лампы (комнатный свет не жжёт).
	var burn := 0.0
	for l in city.lamps:
		if not l["on"] or not l["hurt"]:
			continue
		if bool(l["outer"]) == inside and l["kind"] != "bulb":
			continue
		var lp: Vector2 = l["pos"]
		if absf(lp.x - pos.x) > 300.0:
			continue
		var r := float(l["r"]) * 0.75
		var d := lp.distance_to(pos)
		if d < r and pos.y > lp.y - 10:
			burn = maxf(burn, 1.0 - d / r * 0.5)
	return burn


func sun_on(pos: Vector2, inside: bool) -> bool:
	if inside or env.sun_k < 0.2 or env.rain > 0.3:
		return false
	if pos.y > K.floor_y(0):
		return false
	for poly in View.LightBase.shadow_polys(city, env):
		if Geometry2D.is_point_in_polygon(pos, PackedVector2Array(poly)):
			return false
	# под балконом, козырьком, мостком
	var sp := city.get_world_2d().direct_space_state
	var q := PhysicsRayQueryParameters2D.create(pos, pos - env.sun_dir * 120.0, K.L_PLATFORM | K.L_COMMON)
	var hit := sp.intersect_ray(q)
	return hit.is_empty()


# ======================= восприятие =======================

func can_see(npc: Person, pos: Vector2, inside: bool, area: String, rng_mult: float = 1.0) -> bool:
	if not npc.is_active() or npc.host:
		return false
	if npc.inside != inside:
		return false
	if inside and npc.area != area:
		return false
	var eye := npc.head_pos()
	var d := eye.distance_to(pos)
	var lit := light_at(pos, inside)
	var r := lerpf(70.0, 230.0, lit) * rng_mult
	if npc.pose == "sit":
		r *= 0.8
	if d > r:
		return false
	var dx := pos.x - eye.x
	if d > 24.0 and dx * npc.facing < -6.0 and npc.look_t <= 0.0:
		return false
	var sp := city.get_world_2d().direct_space_state
	var mask := K.L_INTERIOR | K.L_DOOR if inside else K.L_COMMON
	var q := PhysicsRayQueryParameters2D.create(eye, pos, mask)
	return sp.intersect_ray(q).is_empty()


func _perceive(dt: float) -> void:
	var host := player.host
	var acts := player.suspicious_acts() if host else []
	var seen_by := 0
	var why := ""
	for p in people:
		if not p.is_active() or p.host or p.brain == null or p.brain.away:
			continue
		# тела на виду
		for q in people:
			if q.state == "dead" and not q.has_meta("found") and not q.has_meta("stashed") and q.visible:
				if can_see(p, q.center(), q.inside, q.area, 0.75):
					q.set_meta("found", true)
					p.brain.see_body(q)
					body_found(q, p)
			elif q.state == "ko" and not q.host and q.visible and p.brain.react.is_empty() and q != p:
				if can_see(p, q.center(), q.inside, q.area, 0.6) and rng.randf() < 0.1:
					p.brain.react = {"kind": "look", "pos": q.global_position, "t": 5.0, "area": p.area}
					p.say("Вам плохо?", 2.0)
		if host and not acts.is_empty():
			if can_see(p, host.center(), host.inside, host.area):
				seen_by += 1
				why = acts[0][1]
				for a in acts:
					susp += float(a[0]) * dt * float(Game.d("susp_mult")) * _skill_mult(a)
				if p.brain.is_target:
					target_alert += 8.0 * dt
		# слежка: цель замечает одно и то же лицо
		if host and p.brain.is_target and host != p:
			if can_see(p, host.center(), host.inside, host.area, 0.8) and host.global_position.distance_to(p.global_position) < 150:
				var k: float = p.brain.seen_host.get(host.pid, 0.0) + dt * (0.5 if host.prof in ["courier", "guard", "janitor", "police"] else 1.0)
				p.brain.seen_host[host.pid] = k
				if k > 25.0:
					p.brain.seen_host[host.pid] = 0.0
					target_alert += 34.0
					p.say(["Опять этот…", "Что вам нужно?", "Следит, что ли…"][rng.randi() % 3], 2.5)
		# дух глазами животных — только собака
	if seen_by == 0 or acts.is_empty():
		susp = maxf(0.0, susp - dt * 3.0)
	susp = clampf(susp, 0.0, 100.0)
	susp_why = why
	# подтверждение записей: игрок видит цель
	_confirm(dt)


func _skill_mult(a: Array) -> float:
	var host := player.host
	if a[1] == "бежит" and host.prof == "courier":
		return 0.0
	if host.prof == "student":
		return 0.6
	return 1.0


func _confirm(_dt: float) -> void:
	var t := case.target
	if t == null or not t.is_active() or t.brain.away:
		return
	var eye := player.focus_pos() + Vector2(0, -20)
	var ins := player.focus_inside()
	if ins != t.inside:
		return
	var d := eye.distance_to(t.center())
	var face_r := 120.0 * (2.0 if player.host and player.host.prof in ["cashier", "vendor"] else 1.0)
	if d > face_r:
		return
	var sp := city.get_world_2d().direct_space_state
	var q := PhysicsRayQueryParameters2D.create(eye, t.center(), K.L_INTERIOR | K.L_DOOR if ins else K.L_COMMON)
	if not sp.intersect_ray(q).is_empty():
		return
	if light_at(t.center(), t.inside) < 0.25:
		return
	# подтверждаем только известные записи, связанные с тем, что видно
	var gname: String = t.brain.goal.get("name", "")
	for c in case.cards:
		if not c["known"] or c["kind"] != "clue":
			continue
		var ok := false
		match c["id"]:
			"portrait":
				ok = d < 70.0
			"gait":
				ok = absf(t.velocity.x) > 10.0 and d < 110.0
			_:
				ok = c["place"] == gname and t.brain.arrived
		if ok and float(c["clar"]) < 95.0:
			var before := float(c["clar"])
			c["clar"] = 100.0
			if before < 70.0:
				hud.voice("ПАМЯТЬ", "Вот оно. Снова ясно: %s." % c["title"].to_lower(), K.GOLD)
				Sfx.play("memory", -8.0)


# ======================= шум и события людей =======================

func footstep(p: Person) -> void:
	if p.host:
		var loud := 40.0 if p.mode == "walk" else (90.0 if p.mode == "run" else 10.0)
		if p.mode != "sneak":
			Sfx.play("step_hard" if not p.inside else "step", -16.0 if p.mode == "walk" else -10.0)
		if loud > 50.0:
			noise_at(p.global_position, loud, p, "step")


func noise_at(pos: Vector2, loud: float, src: Node, kind: String) -> void:
	for p in people:
		if p == src or not p.is_active() or p.host or p.brain == null:
			continue
		var d: float = p.global_position.distance_to(pos)
		if d < loud and (p.inside == (city.area_at(pos, true) != "") or not p.inside):
			if p.inside and p.area != city.area_at(pos, true) and d > loud * 0.4:
				continue
			p.brain.hear(pos, loud - d, kind)
	if dog:
		dog.hear(pos, loud)


func fall_hurt(p: Person, h: float) -> void:
	Sfx.play_at("thud", p.global_position, player.focus_pos(), 0.0)
	noise_at(p.global_position, 160.0, p, "fall")
	if h > 300.0:
		kill(p, "fall", null)
	else:
		p.knock_out(10.0 if not p.host else 3.0)
		if p.host:
			susp += 15.0
			hud.voice("ТЕЛО", "Больно. Колено хрустнуло.", Color(0.9, 0.6, 0.5))


func portal_used(p: Person, pt: Dictionary, dir: int = 1) -> void:
	if pt["kind"] == "lift":
		var b: Dictionary = city.buildings[int(pt["bid"])]
		var doors: Dictionary = b.get("lift_doors", {})
		var fa := int(city.areas[pt["a"]]["f"])
		var fb := int(city.areas[pt["b"]]["f"])
		for f in [fa, fb]:
			if doors.has(f):
				var s: Sprite2D = doors[f]
				s.frame = 2
				get_tree().create_timer(1.6).timeout.connect(func(): if is_instance_valid(s): s.frame = 0)
		if p.host:
			Sfx.play("door", -16.0)
		return
	if pt["kind"] in ["ladder", "shaft", "manhole"] and p.host:
		Sfx.play("step", -8.0)
	if pt["kind"] in ["entrance", "backdoor"] and pt.has("sprite") and pt["sprite"]:
		var s: Sprite2D = pt["sprite"]
		s.frame = 1
		get_tree().create_timer(1.2).timeout.connect(func(): if is_instance_valid(s): s.frame = 0)
	if p.host and pt["kind"] in ["entrance", "backdoor"]:
		Sfx.play("door", -10.0)


func inside_changed(p: Person) -> void:
	pass


func transit_done(p: Person) -> void:
	if p.host:
		player.after_transit()


func npc_arrived(p: Person, goal: Dictionary) -> void:
	# свет в квартире
	if p.inside:
		var rm := city.room_at(p.area, p.global_position.x)
		if not rm.is_empty():
			rm["occ_t"] = t_total + 240.0
	if p.brain.is_target:
		pass


func npc_left(p: Person) -> void:
	if p == case.target and target_spooked >= 3 and not case.target_dead:
		fail("Цель уехала из района. Дело закрыто без тебя.")


func woke_up(p: Person) -> void:
	# оглушённый ничего не помнит о последних минутах
	for w in witnesses:
		if w["who"] == p:
			w["done"] = true
			case.clear_tail("witness%d" % p.pid)
	p.say("Где я?..", 2.5)


func free_spot(who: Person, x: float) -> float:
	## Ближайшее свободное место у точки сбора: шаг 16 px в обе стороны, очередь к таксофону — в одну.
	var taken := []
	for q in people:
		if q == who or q.state != "ok" or q.area != who.area or not q.brain:
			continue
		var qx: float = q.brain.slot_x if not is_inf(q.brain.slot_x) else (q.global_position.x if q.brain.arrived else INF)
		if not is_inf(qx) and absf(qx - x) < 120.0:
			taken.append(qx)
	var a: Dictionary = city.areas.get(who.area, {})
	for k in 15:
		var off := float((k + 1) / 2) * 16.0 * (1.0 if k % 2 == 1 else -1.0)
		var cx := x + off
		if not a.is_empty() and (cx < float(a["x0"]) or cx > float(a["x1"])):
			continue
		var free := true
		for tx in taken:
			if absf(float(tx) - cx) < 13.0:
				free = false
				break
		if free:
			return cx + randf_range(-2.0, 2.0)
	return x + randf_range(-60.0, 60.0)


func nearest_payphone(pos: Vector2) -> Dictionary:
	var best := {}
	var bd := 1e9
	for o in city.objs:
		if o["kind"] == "payphone":
			var d := absf(float(o["x"]) - pos.x)
			if d < bd:
				bd = d
				best = o
	return best


func try_talk(p: Person) -> void:
	if not p.brain.arrived or p.pose in ["sit", "work"] and rng.randf() < 0.5:
		return
	for q in people:
		if q == p or q.host or not q.is_active() or q.brain == null or q.brain.away or not q.brain.arrived:
			continue
		if q.area != p.area or absf(q.global_position.x - p.global_position.x) > 46:
			continue
		p.facing = 1 if q.global_position.x > p.global_position.x else -1
		q.facing = -p.facing
		var line := _smalltalk(p)
		var reply := _smalltalk(q)
		if gossip_people.has(p.pid) and rng.randf() < 0.5:
			var g: Array = gossip_people[p.pid]
			line = g[1]
			_overhear(p, g)
		p.say(line, 4.0)
		if p.pose == "":
			p.pose = "talk"
		get_tree().create_timer(2.2).timeout.connect(func():
			if is_instance_valid(q) and q.is_active():
				q.say(reply, 3.5)
			if is_instance_valid(p) and p.pose == "talk":
				p.pose = "")
		return


func _overhear(p: Person, g: Array) -> void:
	var fp := player.focus_pos()
	if player.focus_inside() != p.inside:
		return
	if fp.distance_to(p.global_position) > 130.0:
		return
	if player.focus_inside() and player.focus_area() != p.area:
		return
	var first := case.learn(g[0], 80.0, "подслушал")
	if first:
		hud.card_toast(case.card(g[0]), "Подслушано")


const SMALL := ["Опять дождь обещали.", "Свет вчера опять отключали.", "В «Универсам» колбасу завезли.", "Троллейбус не ходит, пешком пришлось.",
	"Лифт третий день стоит.", "Сосед опять сверлит.", "Холодно в этом году рано.", "Говорят, в НИИ сокращение.",
	"Ты видел, что в газете пишут?", "Да ну его.", "Ага.", "Вот и я говорю.", "Ну и дела.", "Не знаю, не знаю…",
	"В подвале опять трубу прорвало.", "Кошка опять на крыше орёт.", "Куда катимся…", "На заводе премию не дали."]


func _smalltalk(_p: Person) -> String:
	return SMALL[rng.randi() % SMALL.size()]


# ======================= убийства и свидетели =======================

func kill(victim: Person, how: String, by: Person) -> void:
	if victim.state == "dead":
		return
	victim.die(how)
	stats["kills"] += 1
	var accident := how in ["car", "fall", "pot"]
	var pos := victim.center()
	Sfx.play_at("thud", pos, player.focus_pos(), -2.0)
	if victim == case.target:
		case.target_dead = true
		case.dead_how = how
		hud.voice("КУРАТОР", "Цель снята. Теперь уходи чисто.", K.GOLD)
		_schedule_exit()
		if not accident:
			case.add_tail("body", "Тело цели на виду. Спрятать: мусорный бак, шкаф, подвал.")
			victim.set_meta("needs_hide", true)
		if by and how == "hands":
			by.set_meta("executor", true)
			case.add_tail("executor", "Тело-исполнитель очнётся рядом с трупом. Уведи его подальше, прежде чем выйти.")
	else:
		stats["extra_dead"] += 1
		hud.voice("КУРАТОР", "Лишний труп. Это заметят.", Color(0.9, 0.5, 0.45))
	# свидетели
	for p in people:
		if p == victim or p == by or p.host or not p.is_active():
			continue
		if can_see(p, pos, victim.inside, victim.area, 1.1):
			if accident:
				p.brain.see_body(victim)
				victim.set_meta("found", true)
			else:
				add_witness(p, "видел убийство")
	# камеры
	for c in city.cams:
		if c["on"] and _cam_sees(c, pos, victim.inside):
			case.add_tail("cam%d" % city.cams.find(c), "Камера у входа видела, как это было. Стереть запись на пульте охраны.")
	if accident:
		case.clear_tail("body")
		victim.set_meta("accident", true)


func add_witness(p: Person, what: String) -> void:
	for w in witnesses:
		if w["who"] == p and not w["done"]:
			return
	pstats["witness"] = int(pstats["witness"]) + 1
	witnesses.append({"who": p, "t": float(Game.d("witness_t")), "what": what, "done": false})
	case.add_tail("witness%d" % p.pid, "Свидетель (%s). Вселись в него, оглуши — или он позовёт милицию." % what)
	p.brain.scare(p.global_position + Vector2(-p.facing * 20, 0), 3.0)
	p.say("!", 2.0, Color(1.0, 0.4, 0.3))


func _witnesses(dt: float) -> void:
	for w in witnesses:
		if w["done"]:
			continue
		var p: Person = w["who"]
		if p.host or p.state == "ko":
			continue
		if p.state == "dead":
			w["done"] = true
			continue
		w["t"] = float(w["t"]) - dt
		if float(w["t"]) <= 0.0:
			w["done"] = true
			p.brain.react = {"kind": "alarm", "pos": p.global_position, "t": 40.0, "area": p.area}
			p.mode = "run"
			p.say("Милиция! Я всё видел!", 3.0, Color(1.0, 0.5, 0.4))
			alarm_count += 1


func _cam_sees(c: Dictionary, pos: Vector2, inside: bool) -> bool:
	if inside != bool(c["inside"]):
		return false
	var cp: Vector2 = c["pos"]
	var d := pos - cp
	if d.length() > float(c["range"]):
		return false
	if d.x * float(c["dir"]) < 0:
		return false
	return light_at(pos, inside) > 0.2


func cams_check(pos: Vector2, inside: bool, what: String) -> void:
	for c in city.cams:
		if c["on"] and _cam_sees(c, pos, inside):
			case.add_tail("cam%d" % city.cams.find(c), "Камера записала: %s. Стереть запись на пульте охраны." % what)


func body_found(body: Person, by: Person) -> void:
	if body.has_meta("accident"):
		hud.voice("ЧУТЬЁ", "Нашли. Несчастный случай — так и запишут.", Color(0.8, 0.8, 0.75))
		_call_police(body.global_position, false)
		return
	hud.voice("ЧУТЬЁ", "Тело нашли. Сейчас приедут.", Color(1.0, 0.55, 0.45))
	alarm_count += 1
	_call_police(body.global_position, true)


func police_called(body, caller: Person) -> void:
	_call_police(caller.global_position if body == null else (body as Person).global_position, true)


func _call_police(pos: Vector2, crime: bool) -> void:
	if police_state != "":
		return
	police_state = "coming"
	police_t = 60.0
	police_target = pos
	if crime:
		case.add_tail("police", "Вызвали милицию. Не попадайся им на глаза с телом.")


func _police(dt: float) -> void:
	if police_state == "coming":
		police_t -= dt
		if police_t <= 0.0:
			police_state = "here"
			police_t = 240.0
			_spawn_police()
	elif police_state == "here":
		police_t -= dt
		if police_car:
			police_car.modulate = Color(1, 1, 1) if int(t_total * 4) % 2 == 0 else Color(0.7, 0.8, 1.3)
		if police_t <= 0.0:
			police_state = ""
			for c in police:
				c.queue_free()
				people.erase(c)
			police.clear()
			case.clear_tail("police")
			if police_car:
				police_car.queue_free()
				police_car = null
			Sfx.loop_level("heart", 0.0, 1.0)


func _spawn_police() -> void:
	var x := clampf(police_target.x, 200.0, city.width * K.T - 200.0)
	police_car = Res.prop_sprite("police_car")
	police_car.position = Vector2(x + 40, K.floor_y(0) + 30)
	police_car.visibility_layer = K.V_OUTER
	city.front.add_child(police_car)
	Sfx.play_at("siren", police_car.position, player.focus_pos(), -6.0)
	for i in 2:
		var lk := Looks.random_look(rng, false, 1, "police")
		var c := _new_person(lk, "police", false)
		c.first = "Сержант" if i == 0 else "Лейтенант"
		c.global_position = Vector2(x + 30 + i * 16, K.floor_y(0) - 1)
		c.area = "S"
		c.set_inside(false)
		var tarea := city.area_at(police_target, police_target.y < K.floor_y(0) - 4 or police_target.y > K.floor_y(0) + 4)
		if tarea == "":
			tarea = "S"
		c.brain.sched = [{"h": 0.0, "area": tarea, "x": police_target.x + i * 20 - 10, "act": "idle"}]
		c.brain.goal = {}
		c.base_speed = 58.0
		for b in city.buildings:
			c.keys.append("apt%d" % b["id"])
		police.append(c)


func _schedule_exit() -> void:
	var phones := city.objs.filter(func(o): return o["kind"] == "payphone")
	var ph: Dictionary = phones[rng.randi() % phones.size()]
	var h0 := _round5(env.hour + rng.randf_range(0.45, 0.7))
	exit_ring = {"phone": ph, "h0": h0, "h1": h0 + 0.25, "tries": 1}
	hud.voice("КУРАТОР", "Таксофон %s. Позвоню в %s. Сними трубку." % [ph["name"], K.fmt_time(h0)], K.GOLD)
	case.line = exit_ring


func _exit(dt: float) -> void:
	if exit_ring.is_empty():
		return
	var ph: Dictionary = exit_ring["phone"]
	var ringing := env.hour >= float(exit_ring["h0"]) and env.hour < float(exit_ring["h1"])
	ph["ring"] = ringing
	(ph["node"] as Sprite2D).frame = (1 + int(t_total * 6) % 2) if ringing else 0
	if ringing and fmod(t_total, 2.0) < dt:
		Sfx.play_at("ring", Vector2(float(ph["x"]), float(ph["y"])), player.focus_pos(), -2.0)
	if env.hour >= float(exit_ring["h1"]):
		if int(exit_ring["tries"]) >= 3:
			fail("Ты не снял трубку. Служба тебя списала.")
			return
		var phones := city.objs.filter(func(o): return o["kind"] == "payphone" and o != ph)
		ph["ring"] = false
		(ph["node"] as Sprite2D).frame = 0
		var nph: Dictionary = phones[rng.randi() % phones.size()]
		var h0 := _round5(env.hour + 0.5)
		exit_ring = {"phone": nph, "h0": h0, "h1": h0 + 0.25, "tries": int(exit_ring["tries"]) + 1}
		hud.voice("КУРАТОР", "Пропустил. Последний раз: таксофон %s, %s." % [nph["name"], K.fmt_time(h0)], Color(0.95, 0.6, 0.4))


func _round5(h: float) -> float:
	## Время звонка — ровно на пять минут, чтобы часы и слова куратора совпадали.
	return ceil(h * 12.0 - 0.001) / 12.0


func answer_phone(ph: Dictionary) -> void:
	if exit_ring.is_empty() or ph != exit_ring["phone"] or not ph["ring"]:
		return
	Sfx.play("pickup")
	finish(false)


func emergency_line() -> void:
	## «Сворачиваюсь»: уйти через любой таксофон, дело провалено, но служба не теряет тебя.
	finish(true)


# ======================= цель =======================

func _target_watch(dt: float) -> void:
	var t := case.target
	if t == null or case.target_dead or not t.is_active():
		return
	target_alert = maxf(0.0, target_alert - dt * 0.4)
	if target_alert >= 100.0:
		target_alert = 30.0
		target_spooked += 1
		match target_spooked:
			1:
				t.say("Мне нужно домой.", 3.0)
				hud.voice("ЧУТЬЁ", "Цель насторожилась. Не мелькай.", Color(1.0, 0.7, 0.4))
				t.brain.react = {"kind": "goto", "pos": Vector2(float(case.place("Дом")["x"]), 0), "area": case.place("Дом")["area"], "t": 120.0}
			2:
				hud.voice("ЧУТЬЁ", "Цель напугана. Ещё раз — и уедет.", Color(1.0, 0.55, 0.4))
				t.base_speed = 58.0
			3:
				hud.voice("ЧУТЬЁ", "Уезжает! Метро!", Color(1.0, 0.4, 0.35))
				t.brain.react = {"kind": "goto", "pos": Vector2(float(city.places["Метро"]["x"]), 0), "area": "M", "t": 300.0}
				t.brain.sched = [{"h": 0.0, "area": "M", "x": float(city.places["Метро"]["x"]), "act": "away"}]


# ======================= транспорт =======================

func _cars(dt: float) -> void:
	car_t -= dt
	if car_t <= 0.0:
		car_t = rng.randf_range(4.0, 11.0)
		var dir := 1 if rng.randf() < 0.5 else -1
		var nm := "car%d" % (rng.randi() % 5)
		if rng.randf() < 0.12:
			nm = "trolley"
		if rng.randf() < 0.05:
			nm = "ambulance"
		var s := Res.prop_sprite(nm)
		var w := float(city.width * K.T)
		s.position = Vector2(-120.0 if dir > 0 else w + 120.0, K.floor_y(0) + 30 + (0 if dir > 0 else 2))
		s.flip_h = dir < 0
		s.visibility_layer = K.V_OUTER
		s.z_index = 1 if dir > 0 else 0
		city.front.add_child(s)
		var hl := city._light(city.lights_out, s.position, Vector2(80, 30), Color(1, 0.9, 0.7), 0.0, "car")
		cars.append({"s": s, "dir": dir, "v": rng.randf_range(150, 230) * (0.6 if nm == "trolley" else 1.0), "hl": hl, "stop": nm == "trolley", "stopped": 0.0})
	var w2 := float(city.width * K.T)
	var bus_x: float = city.places["Остановка"]["x"]
	for c in cars.duplicate():
		var s: Sprite2D = c["s"]
		if c["stop"] and float(c["stopped"]) < 6.0 and absf(s.position.x - bus_x) < 6:
			c["stopped"] = float(c["stopped"]) + dt
			continue
		s.position.x += float(c["v"]) * dt * int(c["dir"])
		var hl: Sprite2D = c["hl"]
		hl.position = s.position + Vector2(40 * int(c["dir"]), -12)
		hl.visible = env.night > 0.3
		hl.modulate = Color(0.45, 0.4, 0.3)
		if absf(s.position.x - player.focus_pos().x) < 300 and fmod(t_total, 3.0) < dt:
			Sfx.play_at("car", s.position, player.focus_pos(), -10.0)
		if s.position.x < -200 or s.position.x > w2 + 200:
			s.queue_free()
			hl.queue_free()
			cars.erase(c)


func car_near(x: float, within: float) -> bool:
	for c in cars:
		var s: Sprite2D = c["s"]
		var dx := (x - s.position.x) * int(c["dir"])
		if dx > 0 and dx < within:
			return true
	return false


func _train(dt: float) -> void:
	train_t -= dt
	var a: Dictionary = city.areas["M"]
	var y := float(a["y"]) + 6
	if train.is_empty() and train_t <= 0.0:
		var s := Res.prop_sprite("metro_car")
		s.visibility_layer = K.V_INNER
		s.z_index = K.Z_PEOPLE + 5
		s.position = Vector2(float(a["x0"]) - 300, y + 4)
		city.furn.add_child(s)
		var s2 := Res.prop_sprite("metro_car")
		s2.visibility_layer = K.V_INNER
		s2.z_index = K.Z_PEOPLE + 5
		s2.position = s.position + Vector2(-194, 0)
		city.furn.add_child(s2)
		train = {"s": [s, s2], "phase": "in", "t": 0.0, "stop_x": (float(a["x0"]) + float(a["x1"])) / 2.0 + 100}
		if player.focus_pos().y > K.floor_y(0) + 100:
			Sfx.play("train", -6.0)
	if train.is_empty():
		return
	var ss: Array = train["s"]
	var lead: Sprite2D = ss[0]
	match train["phase"]:
		"in":
			var dx := float(train["stop_x"]) - lead.position.x
			var v := clampf(dx * 1.2, 30.0, 260.0)
			for s in ss:
				s.position.x += v * dt
			if dx < 2.0:
				train["phase"] = "stop"
				train["t"] = 9.0
				_train_stop()
		"stop":
			train["t"] = float(train["t"]) - dt
			if float(train["t"]) <= 0.0:
				train["phase"] = "out"
		"out":
			for s in ss:
				s.position.x += minf(300.0, 40.0 + (lead.position.x - float(train["stop_x"])) * 1.5) * dt
			if lead.position.x > float(a["x1"]) + 600:
				for s in ss:
					s.queue_free()
				train = {}
				train_t = rng.randf_range(40.0, 70.0)


func _train_stop() -> void:
	## Поезд: кто ждёт отъезда — уезжает, кто должен вернуться — выходит.
	for p in people:
		if p.brain == null or p.host:
			continue
		var g: Dictionary = p.brain.current_goal(env.hour)
		if p.brain.away and not g.is_empty() and g["act"] != "away":
			p.brain.come_back()
		elif not p.brain.away and p.area == "M" and not g.is_empty() and g["act"] == "away" and p.brain.arrived:
			p.brain._go_away()


# ======================= события =======================

func _events(dt: float) -> void:
	events_t -= dt
	if events_t > 0.0:
		return
	events_t = rng.randf_range(200.0, 320.0)
	if rng.randf() < 0.5:
		var b: Dictionary = city.buildings[rng.randi() % city.buildings.size()]
		blackouts.append({"bid": b["id"], "until": t_total + 60.0})
		hud.voice("ГОРОД", "Свет мигнул и погас: %s." % (b["name"] if b["name"] != "" else "дом у %s" % ("сквера" if rng.randf() < 0.5 else "гаражей")), Color(0.75, 0.78, 0.82))
		for c in city.cams:
			if int(c["bid"]) == int(b["id"]):
				c["off_until"] = t_total + 60.0


func cams_tick() -> void:
	for c in city.cams:
		var on := float(c.get("off_until", 0.0)) < t_total
		c["on"] = on
		(c["node"] as Sprite2D).frame = 1 if on else 0


# ======================= конец дела =======================

func _check_end() -> void:
	if over:
		return
	cams_tick()
	if player.host and susp >= 100.0:
		fail("Тебя раскрыли: видели, как тело %s." % susp_why if susp_why != "" else "Тебя раскрыли.")
		return
	if env.hour >= 26.0:
		fail("Ночь кончилась. Дело закрыли без тебя.")
		return
	if case.memory() < 4.0:
		fail("Ты забыл, зачем пришёл. Память пуста.")


func fail(why: String) -> void:
	if over:
		return
	over = true
	result = {"ok": false, "why": why}
	_finish_result()


func finish(emergency: bool) -> void:
	if over:
		return
	over = true
	var tails := case.open_tails()
	var grade := "чисто"
	if not case.target_dead:
		result = {"ok": false, "why": "Сорвался по экстренной линии. Цель жива." if emergency else "Цель жива."}
		_finish_result()
		return
	if tails.size() > 0:
		grade = "шумно"
	if alarm_count > 0 or tails.size() > 2:
		grade = "грязно"
	result = {"ok": true, "grade": grade, "tails": tails, "how": case.dead_how, "alarms": alarm_count, "extra": stats["extra_dead"]}
	_finish_result()


func _write_stats() -> void:
	## Строка в playstats.csv рядом с настройками: по ней подбираются цены памяти, таяние, свидетели.
	var path := "user://playstats.csv"
	var cols := ["date", "version", "seed", "difficulty", "ok", "grade", "why", "hour_start", "hour_end", "real_min", "body_min", "spirit_min",
		"memory_end", "spent_enter", "spent_enter_fast", "spent_thrown", "spent_claws", "thrown", "jumps", "claws", "talks", "witnesses",
		"alarms", "max_susp", "min_density", "extra_dead"]
	var claws := 0.0
	for k in case.spent:
		if str(k).begins_with("claw_"):
			claws += float(case.spent[k])
	var row := [Time.get_datetime_string_from_system(), ProjectSettings.get_setting("application/config/version", ""), case_seed, Game.difficulty,
		result.get("ok", false), result.get("grade", ""), str(result.get("why", "")).replace(";", ","), "%.2f" % start_h, "%.2f" % env.hour,
		"%.1f" % (t_total / 60.0), "%.1f" % (float(pstats["body_s"]) / 60.0), "%.1f" % (float(pstats["spirit_s"]) / 60.0), "%.0f" % case.memory(),
		"%.1f" % float(case.spent.get("enter", 0.0)), "%.1f" % float(case.spent.get("enter_fast", 0.0)), "%.1f" % float(case.spent.get("thrown", 0.0)),
		"%.1f" % claws, pstats["thrown"], stats["jumps"], stats["claws"], pstats["talks"], pstats["witness"], alarm_count,
		"%.0f" % float(pstats["max_susp"]), "%.0f" % float(pstats["min_density"]), stats["extra_dead"]]
	var exists := FileAccess.file_exists(path)
	var f := FileAccess.open(path, FileAccess.READ_WRITE if exists else FileAccess.WRITE)
	if f == null:
		return
	if exists:
		f.seek_end()
	else:
		f.store_line(";".join(cols))
	f.store_line(";".join(row.map(func(v): return str(v))))
	f.close()


func _finish_result() -> void:
	result["hour"] = env.hour
	result["target"] = case.p["first"] + " " + case.p["last"]
	result["female"] = bool(case.p["female"])
	result["curator"] = case.curator["name"]
	result["seed"] = case_seed
	_write_stats()
	hud.end_flash(result)
	get_tree().create_timer(2.5).timeout.connect(func(): main.show_result(result))


