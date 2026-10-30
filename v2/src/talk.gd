class_name Talk
extends RefCounted
## Разговор с прохожим: меню снизу, пиксельный портрет, темы, настроение и терпение собеседника.
## Характер (черты) и отношение к телу, в котором ты сейчас, решают, ответит ли он и что скажет.

const TRAITS := {
	"chatty": {"name": "болтлив", "mood": 15.0, "pat": 3},
	"gloomy": {"name": "угрюм", "mood": -15.0, "pat": -1},
	"wary": {"name": "подозрителен", "mood": -5.0, "pat": 0},
	"kind": {"name": "добродушен", "mood": 12.0, "pat": 1},
	"busy": {"name": "занят", "mood": 0.0, "pat": -2},
	"deaf": {"name": "глуховат", "mood": 5.0, "pat": 1},
	"timid": {"name": "пуглив", "mood": 0.0, "pat": 0},
}
const WORK_ACTS := ["work", "cashier", "barista", "guard", "desk"]
const DIRS := ["Кафе", "Аптека", "Универсам", "Метро", "Киоск", "Сквер", "Двор", "Гаражи"]
const LIFE := ["Пенсию опять задержали. А цены-то, цены!", "Внук не звонит. Всё работа у него, работа…",
	"Давление скачет, как погода. Врачиха говорит — возраст.", "Раньше тут сирень была. Вырубили, гараж поставили.",
	"Сосед сверху заливает, третий раз за год.", "В очереди за молоком час стоял{a}, а оно кончилось."]
const BUY := {"vendor": "Газету, пожалуйста.", "cashier": "Пачку чая, пожалуйста.", "barista": "Стакан чаю.", "pharm": "Что-нибудь от головы."}

static var portraits := {}      # pid -> ImageTexture

var world: Node
var pl: PlayerCtl
var case: Case
var q: Person                   # собеседник
var host: Person                # тело, которым говоришь
var mem: Dictionary             # память собеседника о разговорах
var node := "root"
var line := ""                  # последняя реплика собеседника
var opts: Array = []            # [{text, id, arg}]
var close_t := -1.0             # >0: разговор закроется через столько секунд
var rel := ["незнакомец", 0.0]


func _init(w: Node, ctl: PlayerCtl, who: Person) -> void:
	world = w
	pl = ctl
	case = w.case
	q = who
	host = ctl.host
	mem = mem_for(w, q)
	rel = _relation()
	var hk := str(host.pid)
	if not (mem["mood"] as Dictionary).has(hk):
		mem["mood"][hk] = clampf(45.0 + _trait_sum("mood") + float(rel[1]) + float(mem["mood_adj"].get(hk, 0.0)) + randf_range(-8, 8), 0.0, 95.0)
	# терпение восстанавливается, если давно не говорили
	if not (mem["pat"] as Dictionary).has(hk) or world.env.hour - float(mem["last"].get(hk, -9.0)) > 1.0:
		var pat := 4 + int(_trait_sum("pat")) + (2 if rel[1] > 0.0 else 0)
		if q.brain and q.brain.arrived and q.brain.goal.get("act", "") in WORK_ACTS:
			pat -= 2
		mem["pat"][hk] = maxi(2, pat)
	mem["last"][hk] = world.env.hour
	q.brain.react = {"kind": "talk", "pos": host.global_position, "t": 9999.0, "area": q.area, "who": host}
	q.move_x = 0.0
	q.pose = ""
	if q == case.target:
		world.target_alert += 10.0
	if world.greet_wait.has(q.pid):
		world.greet_wait.erase(q.pid)
	if mem["grudge"].has(hk):
		# обида на это тело держится весь день
		mem["mood"][hk] = minf(mood(), 25.0)
		line = _pick(["Опять ты? После того, как ты %s?" % mem["grudge"][hk], "С тобой я разговаривать не буду. Ты %s." % mem["grudge"][hk]])
	elif mem["fond"].has(hk) and mood() >= 20.0:
		line = _pick(["А, это вы! Помню-помню: %s." % mem["fond"][hk], "Здравствуйте ещё раз. Вы ведь %s." % mem["fond"][hk]])
	elif mood() < 20.0:
		line = _pick(["Некогда мне.", "Отстаньте.", "Чего надо?", "Не до вас сейчас."])
	elif rel[0] in ["сосед", "семья", "коллега"]:
		line = _pick(["О, %s! Чего тебе?" % host.first, "А, это ты. Ну, говори.", "%s? Что-то случилось?" % host.first])
	else:
		line = _pick(["Да?", "Слушаю.", "Вы что-то хотели?", "М-м?"])
	_build()


# ======================= память и характер =======================

static func mem_for(w: Node, q: Person) -> Dictionary:
	## Память человека о разговорах: черты, настроение к каждому телу, обиды и добрые дела.
	var m: Dictionary = w.talk_mem.get(q.pid, {})
	if m.is_empty():
		m = _new_mem(w, q)
		w.talk_mem[q.pid] = m
	return m


static func remember(w: Node, q: Person, body: Person, kind: String, why: String, dmood: float) -> void:
	## Запомнить тело: kind — "grudge" (обида) или "fond" (доброе). Держится весь день.
	var m := mem_for(w, q)
	m[kind][str(body.pid)] = why
	var hk := str(body.pid)
	if (m["mood"] as Dictionary).has(hk):
		m["mood"][hk] = clampf(float(m["mood"][hk]) + dmood, 0.0, 100.0)
	else:
		m["mood_adj"][hk] = float(m["mood_adj"].get(hk, 0.0)) + dmood


static func _new_mem(w: Node, q: Person) -> Dictionary:
	var rng := RandomNumberGenerator.new()
	rng.seed = int(w.case_seed) * 7919 + q.pid * 104729
	var tr := []
	var keys := TRAITS.keys()
	var n := 1 if rng.randf() < 0.6 else 2
	while tr.size() < n:
		var k: String = keys[rng.randi() % keys.size()]
		if k == "deaf" and q.age < 2:
			continue
		if not (k in tr) and not (k == "chatty" and "gloomy" in tr) and not (k == "gloomy" and "chatty" in tr):
			tr.append(k)
	if q.prof == "pensioner" and not ("chatty" in tr) and rng.randf() < 0.5:
		tr.append("chatty")
	return {"traits": tr, "mood": {}, "pat": {}, "last": {}, "asked": {}, "smoked": {}, "greet": {}, "bought": {},
		"grudge": {}, "fond": {}, "mood_adj": {}}


func has_trait(k: String) -> bool:
	return k in mem["traits"]


func _trait_sum(field: String) -> float:
	var s := 0.0
	for k in mem["traits"]:
		s += float(TRAITS[k][field])
	return s


func memory_words() -> String:
	var hk := str(host.pid)
	if mem["grudge"].has(hk):
		return "помнит обиду: " + str(mem["grudge"][hk])
	if mem["fond"].has(hk):
		return "помнит доброе: " + str(mem["fond"][hk])
	return ""


func trait_words() -> String:
	var out := []
	for k in mem["traits"]:
		out.append(TRAITS[k]["name"])
	return ", ".join(out)


func _relation() -> Array:
	if q.home.has("bid") and host.home.has("bid") and int(q.home["bid"]) == int(host.home["bid"]):
		if int(q.home.get("apt", -1)) == int(host.home.get("apt", -2)) and int(q.home.get("f", -1)) == int(host.home.get("f", -2)):
			return ["семья", 30.0]
		return ["сосед", 18.0]
	if q.has_meta("work") and host.has_meta("work") and q.get_meta("work") == host.get_meta("work"):
		return ["коллега", 15.0]
	if host.prof == "police":
		return ["милиция", 8.0]
	if host.prof == q.prof:
		return ["свой брат", 10.0]
	if q.prof in ["vendor", "cashier", "barista", "pharm"]:
		return ["покупатель", 4.0]
	return ["незнакомец", 0.0]


func mood() -> float:
	return float(mem["mood"][str(host.pid)])


func _mood_add(v: float) -> void:
	mem["mood"][str(host.pid)] = clampf(mood() + v, 0.0, 100.0)


func patience() -> int:
	return int(mem["pat"][str(host.pid)])


func _asked(id: String) -> int:
	var k := "%d:%s" % [host.pid, id]
	return int(mem["asked"].get(k, 0))


func _mark(id: String) -> void:
	var k := "%d:%s" % [host.pid, id]
	mem["asked"][k] = int(mem["asked"].get(k, 0)) + 1


func _pick(a: Array) -> String:
	return a[randi() % a.size()]


func _a() -> String:
	return "а" if q.female else ""


func _ha() -> String:
	return "а" if host.female else ""


# ======================= меню =======================

func _build() -> void:
	opts = []
	match node:
		"root":
			if mood() < 20.0:
				if not mem["smoked"].has(str(host.pid)):
					opts.append({"text": "Угостить сигаретой", "id": "smoke"})
				opts.append({"text": "Хитрость…", "id": "go", "arg": "trick"})
				return
			if not mem["greet"].has(str(host.pid)):
				opts.append({"text": "Поздороваться", "id": "greet"})
			else:
				opts.append({"text": "Как жизнь?", "id": "small"})
			opts.append({"text": _target_q(), "id": "target"})
			opts.append({"text": "Что слышно в районе?", "id": "rumour"})
			opts.append({"text": "Как пройти…", "id": "go", "arg": "dirs"})
			opts.append({"text": "Который час?", "id": "time"})
			if not mem["smoked"].has(str(host.pid)):
				opts.append({"text": "Угостить сигаретой", "id": "smoke"})
			var po := _prof_opt()
			if not po.is_empty():
				opts.append(po)
			if Case.CLUE_Q.has(q.prof) and _asked("clue") == 0:
				opts.append({"text": Case.CLUE_Q[q.prof], "id": "clue"})
			opts.append({"text": "Хитрость…", "id": "go", "arg": "trick"})
		"dirs":
			for nm in DIRS:
				if world.city.places.has(nm):
					opts.append({"text": nm, "id": "dir", "arg": nm})
			opts.append({"text": "Назад", "id": "go", "arg": "root"})
		"trick":
			opts.append({"text": "Позвать за собой: «Помогите, там…»", "id": "lure"})
			opts.append({"text": "Отвлечь: «Вас там зовут!»", "id": "distract"})
			opts.append({"text": "Пригрозить", "id": "threat"})
			opts.append({"text": "Назад", "id": "go", "arg": "root"})


func _target_q() -> String:
	var c := case.card("portrait")
	if c.get("known", false) and case.stage(c) in ["clear", "haze"]:
		return case.f("Не видели: {man}, {hat}?")
	return case.f("Спросить про {nick}")


func _prof_opt() -> Dictionary:
	match q.prof:
		"guard":
			return {"text": "Попросить ключ от крыши", "id": "guard_key"}
		"janitor":
			return {"text": "Попросить ключ от подвала", "id": "jan_key"}
		"tramp":
			return {"text": "Расспросить про подземку", "id": "under"}
		"vendor", "cashier", "barista", "pharm":
			if not mem["bought"].has(str(host.pid)):
				return {"text": "Купить что-нибудь", "id": "buy"}
		"pensioner":
			return {"text": "Выслушать про жизнь", "id": "life"}
		"office":
			return {"text": "Спросить про работу", "id": "work"}
	return {}


# ======================= ход разговора =======================

func choose(i: int) -> void:
	if close_t > 0.0 or i < 0 or i >= opts.size():
		return
	var o: Dictionary = opts[i]
	if o["id"] == "go":
		node = o["arg"]
		_build()
		Sfx.play("ui", -12.0)
		return
	# глуховатый переспрашивает — вопрос не засчитан
	if has_trait("deaf") and randf() < 0.25 and o["id"] != "greet":
		_say(_pick(["Что? Говорите громче!", "А? Не расслышал%s." % _a(), "Чего-чего?"]))
		return
	_answer(o)
	mem["pat"][str(host.pid)] = patience() - (0 if o["id"] in ["life", "buy", "smoke"] else 1)
	if close_t < 0.0 and (patience() <= 0 or mood() < 5.0):
		line += " " + _pick(["Всё, мне пора.", "Некогда мне болтать.", "Ладно, пойду я."])
		close_t = 2.6
	node = "root"
	_build()


func bye() -> void:
	if close_t > 0.0:
		return
	_say(_pick(["Ну, бывай.", "До свидания.", "Угу.", "Всего доброго."]))
	close_t = 1.2


func _say(t: String) -> void:
	line = t
	q.pose = "talk"


func _need(v: float) -> bool:
	## Хватает ли настроения на ответ. Отказ портит настроение.
	if mood() >= v:
		return true
	_mood_add(-4.0)
	_say(_pick(["А вам зачем?", "Не ваше дело.", "Не знаю я ничего.", "Идите, гражданин, куда шли.", "Не буду я об этом."]))
	return false


func _answer(o: Dictionary) -> void:
	match o["id"]:
		"greet":
			mem["greet"][str(host.pid)] = true
			if rel[0] in ["сосед", "семья"]:
				_mood_add(6.0)
				_say(_pick(["И тебе не хворать, %s." % host.first, "Здравствуй, здравствуй."]))
			elif has_trait("gloomy"):
				_mood_add(1.0)
				_say("Ну, здрасьте.")
			else:
				_mood_add(4.0)
				_say(_pick(["Здравствуйте.", "Добрый день.", "Здрасьте."]))
		"small":
			_mark("small")
			if _asked("small") > 2:
				_mood_add(-5.0)
				_say("Вы мне зубы не заговаривайте.")
				return
			_mood_add(5.0 if has_trait("chatty") or has_trait("kind") else 1.0)
			_say(world.SMALL[randi() % world.SMALL.size()])
		"time":
			_mood_add(1.0)
			var tm := K.fmt_time(world.env.hour)
			_say(("Часы себе купите. %s." % tm) if has_trait("gloomy") else _pick(["Сейчас %s." % tm, "%s, если мои не врут." % tm]))
		"smoke":
			mem["smoked"][str(host.pid)] = true
			mem["fond"][str(host.pid)] = "угостили меня сигаретой"
			if q.prof == "pensioner" and q.female:
				_mood_add(6.0)
				_say("Не курю я, милок. Но спасибо, что предложил.")
			else:
				_mood_add(20.0 if has_trait("gloomy") else 15.0)
				_say(_pick(["О, спасибо. Давно не курил%s." % _a(), "Не откажусь.", "Вот это по-нашему."]))
		"target":
			_ask_target()
		"rumour":
			if not _need(30.0):
				return
			_rumour()
		"dir":
			if not _need(8.0):
				return
			_direction(o["arg"])
		"buy":
			mem["bought"][str(host.pid)] = true
			mem["fond"][str(host.pid)] = "у меня покупали"
			_mood_add(12.0)
			_say(_pick(["Пожалуйста. С вас двадцать копеек.", "Держите. Сдачи нет, извините.", "Вот. Приходите ещё."]))
		"life":
			_mood_add(16.0)
			mem["fond"][str(host.pid)] = "меня выслушали"
			mem["pat"][str(host.pid)] = patience() + 2
			_say(_pick(LIFE).replace("{a}", _a()))
		"work":
			_ask_work()
		"clue":
			_prof_clue()
		"guard_key":
			_guard_key()
		"jan_key":
			_janitor_key()
		"under":
			_underground()
		"lure":
			_lure()
		"distract":
			_distract()
		"threat":
			_threat()


func _ask_target() -> void:
	if q == case.target:
		world.target_alert += 25.0
		_say(_pick(["Это вы про меня? Мы знакомы?", "Странные вы вопросы задаёте.", "Я вас не знаю."]))
		_mood_add(-15.0)
		return
	if _asked("target") > 0:
		_mood_add(-5.0)
		_say("Я же сказал%s уже." % _a())
		return
	var need := 40.0 + (15.0 if has_trait("wary") else 0.0) + (10.0 if has_trait("gloomy") else 0.0) - (10.0 if has_trait("chatty") else 0.0)
	if not _need(need):
		return
	_mark("target")
	if has_trait("wary"):
		_mood_add(-8.0)
	var key := "%d:%d" % [q.pid, host.pid]
	var ln := case.informant_line(q.prof)
	if ln.is_empty() and world.gossip_people.has(q.pid):
		ln = world.gossip_people[q.pid]
	if not ln.is_empty():
		ln = [ln[0], Case.voiced(ln[1], q.female)]
	if not ln.is_empty() and not world.told.has(key):
		world.told[key] = true
		_say(ln[1])
		_learn(ln[0], 90.0, "со слов: %s" % pl._who_word(q), ln[1])
		return
	# видел похожего — но мог перепутать с двойником
	if randf() < (0.75 if has_trait("chatty") else 0.5):
		var who: Person = case.target
		if case.decoys.size() > 0 and randf() < 0.3:
			who = case.decoys[randi() % case.decoys.size()]
		var where := _where_word(who)
		_say(_pick(["Видел%s похож%s. %s." % [_a(), "ую" if case.p["female"] else "его", where],
			"Был%s тут так%s. %s." % ["а" if case.p["female"] else "", "ая" if case.p["female"] else "ой", where]]))
		return
	_say(_pick(["Не знаю такого.", "Не припомню.", "Тут много кто ходит."]))


func _where_word(who: Person) -> String:
	var g: Dictionary = who.brain.goal if who.brain else {}
	var nm: String = g.get("name", "")
	if nm == "Дом" or nm == "":
		if who.area == "S":
			return "Шёл%s по улице, %s" % ["а" if case.p["female"] else "", "в сторону %s" % _side_word(who.global_position.x)]
		if who.area == "M":
			return "В метро спустил%s" % ("ась" if case.p["female"] else "ся")
		return "Зашёл%s в дом" % ("ла" if case.p["female"] else "")
	return "Кажется, к «%s» направлял%s" % [nm, "ась" if case.p["female"] else "ся"] if nm in ["Кафе", "Аптека", "Универсам", "Офис", "НИИ"] else "Видел%s у места «%s»" % [_a(), nm]


func _side_word(x: float) -> String:
	var mid := float(world.city.width * K.T) / 2.0
	return "метро" if absf(x - float(world.city.places["Метро"]["x"])) < mid * 0.5 else ("сквера" if x < mid else "гаражей")


func _learn(id: String, clar: float, src: String, txt: String) -> void:
	var first := case.learn(id, clar, src)
	if first:
		world.hud.card_toast(case.card(id), "Со слов", txt)
	else:
		world.hud.voice("ПАМЯТЬ", "Совпадает. Запись снова ясна.", K.GOLD)


func _rumour() -> void:
	var pool: Array = world.rumours
	var free := pool.filter(func(r): return not world.rumours_told.has(r[0]))
	if free.is_empty() or _asked("rumour") > 0:
		_say(world.SMALL[randi() % world.SMALL.size()])
		return
	_mark("rumour")
	var r: Array = free[randi() % free.size()]
	world.rumours_told[r[0]] = true
	_say(r[2])
	var c := case.add_foreign("r_" + str(r[0]), r[1], r[2])
	c["src"] = "слух: %s" % pl._who_word(q)
	world.hud.card_toast(c, "Слух")


func _direction(nm: String) -> void:
	var p: Dictionary = world.city.places[nm]
	var dx := float(p["x"]) - host.global_position.x
	var m := int(round(absf(dx) / 16.0 * 1.5 / 10.0)) * 10
	var side := "направо" if dx > 0 else "налево"
	if m < 15:
		_say("%s? Да вот же, рядом." % nm)
	elif nm == "Метро":
		_say("Метро — %s, метров %d. Вход с улицы, под буквой «М»." % [side, m])
	else:
		_say(_pick(["%s? Это %s, метров %d." % [nm, side, m], "Идите %s, метров %d — не промахнётесь." % [side, m]]))
	world.hud.mark_place(float(p["x"]), nm)


func _prof_clue() -> void:
	## Вопрос по профессии: у каждого своё особое знание о цели.
	if q == case.target:
		_ask_target()
		return
	if not _need(45.0 + (15.0 if has_trait("wary") else 0.0) - (10.0 if has_trait("chatty") else 0.0)):
		return
	_mark("clue")
	var c := case.prof_clue(q.prof)
	if c.is_empty() or randf() < 0.15:
		_say(_pick(["Да кто их всех упомнит.", "Не обращал%s внимания." % _a()]))
		return
	var t := Case.voiced(c[1], q.female)
	_say(t)
	_learn(c[0], float(c[2]), "со слов: %s" % pl._who_word(q), t)


func _ask_work() -> void:
	if not _need(35.0):
		return
	var wn: String = q.get_meta("work", "")
	var tw := "Гранит" if case.p["work"] == "Офис" else "НИИ"
	if wn == tw and _asked("work") == 0:
		_mark("work")
		var t := case.f("{Nick}? Да, у нас работает. Сидит как все, с девяти.")
		_say(t)
		_learn("work", 85.0, "со слов: коллега", t)
		return
	_mark("work")
	_say(_pick(["Работа как работа. Бумаги.", "Сокращения обещают. Сидим, ждём.", "Начальник опять на совещании."]))


func _guard_key() -> void:
	var bid := int(q.get_meta("post", -1))
	var need := 70.0 - (20.0 if rel[0] == "коллега" else 0.0) - (15.0 if host.prof == "police" else 0.0)
	if bid < 0 or ("roof%d" % bid) in host.keys:
		_say("Ключ у вас и так есть.")
		return
	if not _need(need):
		return
	_mark("guard_key")
	host.keys.append("roof%d" % bid)
	_say(_pick(["Ладно, держите. Только вернёте к вечеру.", "Бери. Только я тебе ничего не давал."]))
	pl.say("Ключ от крыши.")
	Sfx.play("pickup", -6.0)


func _janitor_key() -> void:
	var b: Dictionary = world.city.building_at(host.global_position.x)
	if b.is_empty() and host.home.has("bid"):
		b = world.city.buildings[int(host.home["bid"])]
	if b.is_empty():
		_say("От какого подвала-то? Тут их много.")
		return
	var k := "base%d" % b["id"]
	if k in host.keys:
		_say("У тебя ж свой есть.")
		return
	if not _need(60.0 - (15.0 if rel[0] in ["сосед", "семья"] else 0.0)):
		return
	host.keys.append(k)
	_say(_pick(["Трубу опять прорвало? На, держи.", "Только дверь за собой запри."]))
	pl.say("Ключ от подвала.")
	Sfx.play("pickup", -6.0)


func _underground() -> void:
	if not _need(25.0):
		return
	if _asked("under") == 0:
		_mark("under")
		var t := "Из коллектора вниз — скобы, к дренажу. Там вода, течёт к насосной. Кинешь что — унесёт, и не найдут."
		_say(t)
		var c := case.add_foreign("r_under", "Слух: подземка", t)
		c["src"] = "слух: бродяга"
		world.hud.card_toast(c, "Слух")
		return
	if mood() >= 55.0 and not ("grate" in host.keys):
		host.keys.append("grate")
		_say("На, ключ от решёток. У меня запасной. Только ты меня не видел%s." % ("а" if host.female else ""))
		pl.say("Ключ от решёток коллектора.")
		Sfx.play("pickup", -6.0)
		return
	_say(_pick(["Больше ничего не скажу. Самому жить надо.", "Под землёй тихо. Наверху — шумно. Вот и всё."]))


func _lure() -> void:
	if not _need(50.0 - (10.0 if has_trait("kind") else 0.0) + (15.0 if has_trait("wary") else 0.0)):
		return
	_say(_pick(["Что случилось? Пойдём, покажешь.", "Где? Ну, веди."]))
	close_t = 1.0
	world.talk_after = {"kind": "follow", "who": q, "t": 45.0}


func _distract() -> void:
	if has_trait("wary") or not _need(20.0):
		if has_trait("wary"):
			_mood_add(-10.0)
			mem["grudge"][str(host.pid)] = "морочил%s мне голову" % _ha()
			_say("Никто меня не зовёт. Что вы мне голову морочите?")
		return
	_mood_add(-6.0)
	_say(_pick(["Кто? Где?", "Меня? Сейчас…"]))
	close_t = 0.8
	world.talk_after = {"kind": "distract", "who": q, "t": 12.0}


func _threat() -> void:
	var ch := 0.35 + (0.4 if has_trait("timid") else 0.0) + (0.3 if host.prof == "police" else 0.0) - (0.25 if q.prof in ["guard", "police"] else 0.0)
	if q.age == 2:
		ch += 0.1
	world.susp += 25.0
	mem["grudge"][str(host.pid)] = "мне угрожал%s" % _ha()
	mem["fond"].erase(str(host.pid))
	if randf() < ch:
		_mood_add(-60.0)
		if q.prof == "guard" and q.has_meta("post"):
			host.keys.append("roof%d" % int(q.get_meta("post")))
			host.keys.append("sec%d" % int(q.get_meta("post")))
			_say("Ладно, ладно! Вот ключи, только не трогайте!")
		elif q.prof == "janitor":
			host.keys.append("grate")
			for b in world.city.buildings:
				if not (("base%d" % b["id"]) in host.keys):
					host.keys.append("base%d" % b["id"])
			_say("Забирай связку! Всё забирай!")
		else:
			var ln := case.informant_line(q.prof)
			if ln.is_empty() and world.gossip_people.has(q.pid):
				ln = world.gossip_people[q.pid]
			if not ln.is_empty():
				ln = [ln[0], Case.voiced(ln[1], q.female)]
				_say(ln[1])
				_learn(ln[0], 75.0, "под угрозой", ln[1])
			else:
				_say("Ничего не знаю, честное слово! Отпустите!")
		close_t = 2.4
		world.talk_after = {"kind": "scare", "who": q, "t": 8.0}
		return
	_mood_add(-40.0)
	world.susp += 25.0
	world.susp_why = "угрожал прохожему"
	_say(_pick(["Милиция! Хулиганы!", "Ты мне угрожаешь?! Сейчас позову кого надо!"]))
	world.noise_at(host.global_position, 140.0, host, "shout")
	close_t = 1.6
	world.talk_after = {"kind": "scare", "who": q, "t": 6.0}


# ======================= кадр =======================

func tick(dt: float) -> bool:
	## false — разговор окончен.
	if not is_instance_valid(q) or q.state != "ok" or pl.host != host or host.state != "ok":
		return false
	if q.area != host.area or q.global_position.distance_to(host.global_position) > 90.0:
		return false
	q.facing = 1 if host.global_position.x > q.global_position.x else -1
	host.facing = -q.facing
	if close_t > 0.0:
		close_t -= dt
		if close_t <= 0.0:
			return false
	return true


func end() -> void:
	if is_instance_valid(q) and q.brain and q.brain.react.get("kind", "") == "talk":
		q.brain.react["t"] = 0.0
		q.pose = ""


# ======================= портрет =======================

static func portrait(p: Person) -> ImageTexture:
	if portraits.has(p.pid):
		return portraits[p.pid]
	var tex := ImageTexture.create_from_image(_draw_portrait(p.look))
	portraits[p.pid] = tex
	return tex


static func _draw_portrait(lk: Dictionary) -> Image:
	## 32×36: плечи, лицо, причёска, борода, очки, шапка — из палитры внешности.
	var W := 32
	var H := 36
	var img := Image.create(W, H, false, Image.FORMAT_RGBA8)
	var bg := Color(0.16, 0.16, 0.18)
	img.fill(bg)
	var pal: Array = lk.get("pal", Looks.pal_default())
	var skin: Color = pal[Looks.SKIN]
	var hair: Color = pal[Looks.HAIR]
	var top: Color = pal[Looks.TOP]
	var top2: Color = pal[Looks.TOP2]
	var hatc: Color = pal[Looks.HAT]
	var acc: Color = pal[Looks.ACC]
	var female: bool = lk.get("female", false)
	var hs: String = lk.get("hair", "short")
	var hat: String = lk.get("hat", "")
	var cx := 16
	var cy := 16
	# плечи и одежда
	for y in range(27, H):
		var half := 9 + (y - 27)
		for x in range(cx - half, cx + half):
			if x >= 0 and x < W:
				img.set_pixel(x, y, top.darkened(0.12) if x > cx + half - 4 else top)
	var torso: String = lk.get("torso", "coat")
	if torso in ["coat", "jacket"]:
		for y in range(27, H):
			var k := (y - 27) / 2
			for x in range(cx - 2 - k, cx + 2 + k):
				img.set_pixel(x, y, top2)
		for y in range(28, H):
			img.set_pixel(cx, y, top.darkened(0.3))
	elif torso == "sweater":
		for x in range(cx - 4, cx + 4):
			img.set_pixel(x, 27, top.lightened(0.15))
	# шея
	for y in range(23, 28):
		for x in range(cx - 3, cx + 3):
			img.set_pixel(x, y, skin.darkened(0.18))
	if lk.get("scarf", false):
		for y in range(25, 29):
			for x in range(cx - 6, cx + 6):
				img.set_pixel(x, y, acc)
	# длинные волосы позади головы
	if hs in ["long", "bob", "curly"] and hat != "hood" and hat != "kerchief":
		var bottom := 27 if hs == "long" else 21
		for y in range(8, bottom):
			for x in range(cx - 9, cx + 9):
				img.set_pixel(x, y, hair.darkened(0.1))
	# лицо
	for y in range(6, 25):
		for x in range(cx - 8, cx + 8):
			var dx := (float(x) + 0.5 - cx) / 7.2
			var dy := (float(y) + 0.5 - cy) / 9.4
			if dx * dx + dy * dy <= 1.0:
				img.set_pixel(x, y, skin.darkened(0.14) if dx > 0.45 else skin)
	# уши
	for y in range(14, 18):
		img.set_pixel(cx - 8, y, skin.darkened(0.1))
		img.set_pixel(cx + 7, y, skin.darkened(0.2))
	# глаза, брови, нос, рот
	var eye := Color(0.12, 0.1, 0.1)
	for x in [cx - 4, cx - 3, cx + 2, cx + 3]:
		img.set_pixel(x, 15, eye)
	img.set_pixel(cx - 3, 14, Color(0.95, 0.94, 0.9))
	img.set_pixel(cx + 3, 14, Color(0.95, 0.94, 0.9))
	if hs != "bald" or lk.get("age", 1) == 2:
		for x in [cx - 5, cx - 4, cx - 3, cx + 2, cx + 3, cx + 4]:
			img.set_pixel(x, 13, hair.darkened(0.2))
	img.set_pixel(cx, 17, skin.darkened(0.22))
	img.set_pixel(cx, 18, skin.darkened(0.3))
	var lip := skin.darkened(0.35) if not female else Color(0.62, 0.3, 0.3)
	for x in range(cx - 2, cx + 2):
		img.set_pixel(x, 21, lip)
	if lk.get("age", 1) == 2:
		img.set_pixel(cx - 5, 18, skin.darkened(0.2))
		img.set_pixel(cx + 4, 18, skin.darkened(0.25))
	# причёска сверху
	if hs != "bald":
		for y in range(5, 11):
			for x in range(cx - 8, cx + 8):
				var dx2 := (float(x) + 0.5 - cx) / 8.0
				var dy2 := (float(y) + 0.5 - 12.0) / 7.0
				if dx2 * dx2 + dy2 * dy2 <= 1.0 and (y < 9 or absf(dx2) > 0.7):
					img.set_pixel(x, y, hair)
		if hs == "curly":
			for x in range(cx - 8, cx + 8, 2):
				img.set_pixel(x, 4, hair)
		if hs == "bun":
			for y in range(1, 5):
				for x in range(cx - 2, cx + 2):
					img.set_pixel(x, y, hair)
		if hs == "pony":
			for y in range(9, 20):
				img.set_pixel(cx + 8, y, hair)
	# борода
	var beard: String = lk.get("beard", "")
	if beard == "mustache":
		for x in range(cx - 3, cx + 3):
			img.set_pixel(x, 20, hair.darkened(0.1))
	elif beard == "stubble":
		for y in range(19, 24):
			for x in range(cx - 6, cx + 6):
				if (x + y) % 2 == 0 and img.get_pixel(x, y) != bg:
					img.set_pixel(x, y, skin.darkened(0.3))
	elif beard == "full":
		for y in range(18, 26):
			for x in range(cx - 7, cx + 7):
				if img.get_pixel(x, y) != bg and not (y == 21 and absi(x - cx + 1) < 2):
					img.set_pixel(x, y, hair.darkened(0.05))
	# очки
	if lk.get("glasses", false):
		var met := Color(0.25, 0.25, 0.28)
		for x in range(cx - 6, cx + 6):
			img.set_pixel(x, 14 if x != cx - 1 and x != cx else 15, met)
		for y in [15, 16]:
			for x in [cx - 6, cx - 1, cx, cx + 5]:
				img.set_pixel(x, y, met)
		for x in range(cx - 6, cx + 6):
			if x != cx - 1 and x != cx:
				img.set_pixel(x, 17, met)
	# головной убор
	match hat:
		"fedora":
			_rect(img, cx - 10, 7, 20, 2, hatc.darkened(0.15))
			_rect(img, cx - 6, 2, 12, 5, hatc)
			_rect(img, cx - 6, 5, 12, 1, acc)
		"cap":
			_rect(img, cx - 7, 3, 14, 5, hatc)
			_rect(img, cx, 7, 10, 2, hatc.darkened(0.25))
		"ushanka":
			_rect(img, cx - 9, 2, 18, 6, hatc)
			_rect(img, cx - 10, 7, 3, 9, hatc.darkened(0.1))
			_rect(img, cx + 7, 7, 3, 9, hatc.darkened(0.2))
			_rect(img, cx - 9, 2, 18, 1, hatc.lightened(0.2))
		"beanie":
			_rect(img, cx - 8, 3, 16, 6, hatc)
			_rect(img, cx - 8, 8, 16, 1, hatc.darkened(0.2))
			_rect(img, cx - 1, 1, 2, 2, hatc.lightened(0.2))
		"beret":
			_rect(img, cx - 9, 4, 16, 3, hatc)
			_rect(img, cx - 7, 3, 12, 1, hatc)
		"helmet":
			_rect(img, cx - 8, 2, 16, 7, hatc)
			_rect(img, cx - 10, 8, 20, 1, hatc.darkened(0.2))
		"hood", "kerchief":
			var hc := top if hat == "hood" else acc
			for y in range(3, 27):
				for x in range(cx - 11, cx + 11):
					var dx3 := (float(x) + 0.5 - cx) / 10.5
					var dy3 := (float(y) + 0.5 - 14.0) / 11.5
					var inner_x := (float(x) + 0.5 - cx) / 7.0
					var inner_y := (float(y) + 0.5 - 16.0) / 8.5
					if dx3 * dx3 + dy3 * dy3 <= 1.0 and inner_x * inner_x + inner_y * inner_y > 1.0 and y < 26:
						img.set_pixel(x, y, hc if x < cx + 6 else hc.darkened(0.15))
			if hat == "kerchief":
				_rect(img, cx - 2, 24, 4, 3, acc.darkened(0.2))
	# контур
	var out := img.duplicate() as Image
	for y in H:
		for x in W:
			if img.get_pixel(x, y) != bg:
				continue
			for d in [Vector2i(1, 0), Vector2i(-1, 0), Vector2i(0, 1), Vector2i(0, -1)]:
				var nx: int = x + d.x
				var ny: int = y + d.y
				if nx >= 0 and ny >= 0 and nx < W and ny < H and img.get_pixel(nx, ny) != bg:
					out.set_pixel(x, y, Color(0.06, 0.06, 0.07))
					break
	return out


static func _rect(img: Image, x: int, y: int, w: int, h: int, c: Color) -> void:
	for yy in range(maxi(0, y), mini(img.get_height(), y + h)):
		for xx in range(maxi(0, x), mini(img.get_width(), x + w)):
			img.set_pixel(xx, yy, c)
