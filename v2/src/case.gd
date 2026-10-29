class_name Case
extends RefCounted
## Дело: цель, её расписание, двойники, записи на доске и их выцветание.
## Записи: чёткая (70+), дымка (40–70), искажение (15–40), пустота (<15).

var rng := RandomNumberGenerator.new()
var city: City
var p := {}                     # профиль цели
var cards: Array = []
var fmt := {}
var target: Person
var decoys: Array = []
var target_dead := false
var dead_how := ""
var curator := {}
var pins_left := 1
var calls_left := 2
var line := {}                  # назначенный звонок выхода {phone, h0, h1}
var tails: Array = []           # хвосты после убийства
var mem_mult := 1.0
var known_ids := []

const MORNINGS := {
	"Киоск": {"txt": "берёт газету у киоска «Печать» в сквере", "act": "read", "dloc": "Остановка", "dtxt": "ждёт у остановки, читает расписание", "short": "газета у «Печати»"},
	"Универсам": {"txt": "покупает хлеб в «Универсаме»", "act": "shop", "dloc": "Киоск", "dtxt": "берёт газету у киоска", "short": "хлеб в «Универсаме»"},
	"Сквер": {"txt": "кормит голубей в сквере, у памятника", "act": "idle", "dloc": "Двор", "dtxt": "гуляет во дворе у высотки", "short": "голуби в сквере"},
}
const LUNCHES := {
	"Кафе": {"txt": "Обедает в кафе «Встреча» около {lt}. Всегда один{a}, у окна.", "act": "eat", "dloc": "Универсам",
		"dtxt": "Обедает в «Универсаме», у прилавка, около {lt2}.",
		"barista": "Обедает у нас, около {lt}. Всегда один{a}, всегда у окна. Суп и чай.",
		"item": ["Чек из кафе", "Кафе «Встреча», {lt}. Суп, чай. Каждый день одно и то же."],
		"gossip": "В «Встрече» {he} обедает, к {lt}. Я там пирожки беру."},
	"Сквер": {"txt": "Обедает в сквере на скамейке, около {lt}. Бутерброды из дома.", "act": "sit", "dloc": "Кафе",
		"dtxt": "Обедает в кафе «Встреча» около {lt2}.",
		"barista": "К нам не ходит, экономит. Видела в сквере на скамейке, с бутербродами, к {lt}.",
		"item": ["Обёртка от бутербродов", "Вощёная бумага, крошки. Обедает на улице — в сквере, к {lt}."],
		"gossip": "В обед {he} в сквере сидит, на скамейке, с бутербродами. К {lt}, как штык."},
}
const HABITS := {
	"Задворки": {"where": "на задворках «Гранита», у мусорных баков", "dloc": "Гаражи", "dwhere": "у гаражей"},
	"Гаражи": {"where": "у гаражей, за трансформаторной будкой", "dloc": "Задворки", "dwhere": "за «Гранитом»"},
	"Двор": {"where": "во дворе, у берёзы за домами", "dloc": "Площадка", "dwhere": "на детской площадке"},
}
const WORKS := {"Офис": "в «Граните», на третьем этаже", "НИИ": "в НИИ «Связь», на третьем этаже"}
const EVENINGS := {
	"Остановка": {"txt": "Около {et} ждёт троллейбус на остановке у метро.", "dtxt": "Около {et2} стоит на платформе метро.", "dloc": "Метро",
		"item": ["Расписание троллейбуса", "Расписание с остановки у метро. Обведено {et}."]},
	"Метро": {"txt": "Около {et} спускается в метро и ждёт на платформе, кого-то встречает.", "dtxt": "Около {et2} ждёт троллейбус на остановке.", "dloc": "Остановка",
		"item": ["Жетон метро", "Жетон и записка: «платформа, {et}». Кого-то встречает."]},
}
const SIGS := {
	"limp": {"nick": ["хромой", "хромая"], "txt": "Хромает на правую ногу, шаг неровный.",
		"haze": "{He} как будто прихрамывал{a}?", "dist": "Ходит быстро, размашисто.", "empty": "Что-то про то, как {he} ходит…",
		"item": ["Пузырёк «Кеторола»", "Обезболивающее. Рецепт: «правый коленный сустав». Вот почему {he} хромает."],
		"gossip": "Видала, как {he} ковыляет — на правую ногу, и всё встаёт, отдыхает."},
	"hunch": {"nick": ["сутулый", "сутулая"], "txt": "Сутулится, ходит медленно, руки за спиной.",
		"haze": "{He} вроде сутулил{sya}?", "dist": "Держится прямо, шаг быстрый.", "empty": "Что-то про то, как {he} держится…",
		"item": ["Пояс из собачьей шерсти", "Пояс от радикулита. Спина не разгибается — отсюда и сутулость."],
		"gossip": "Согнут{a} в три погибели, руки за спиной — идёт, как на похоронах."},
	"glance": {"nick": ["нервный", "нервная"], "txt": "Нервный: на ходу то и дело оглядывается через плечо.",
		"haze": "{He} оглядывал{sya}… или мне показалось?", "dist": "Идёт спокойно, не оборачивается.", "empty": "Что-то про то, как {he} оглядывается…",
		"item": ["Флакон корвалола", "Пустой флакон корвалола. Нервы. Вот почему {he} всё время оглядывается."],
		"gossip": "Дёрганый какой-то. Идёт — и всё через плечо зырк, зырк."},
}
const CURATORS := [
	{"name": "Ворон", "line": "Повторять не буду. Слушай один раз.", "tic": "*щёлкает ручкой*"},
	{"name": "Лиса", "line": "Всё просто, котик. Почти всё.", "tic": "*мягко смеётся*"},
	{"name": "Седой", "line": "Не торопись. Город сам тебе всё покажет.", "tic": "*кашляет*"},
	{"name": "Тихий", "line": "Говори коротко. Линию слушают.", "tic": "*пауза*"},
]


func f(s: String) -> String:
	return s.format(fmt)


func hhmm(h: float) -> String:
	var hh := int(h)
	var mm := int(round((h - hh) * 60.0 / 10.0)) * 10
	if mm == 60:
		hh += 1
		mm = 0
	return "%d:%02d" % [hh % 24, mm]


func generate(seed_v: int, c: City) -> void:
	rng.seed = seed_v
	city = c
	mem_mult = Game.d("mem_mult") * (0.7 if Game.has_perm("quiet") else 1.0)
	pins_left = int(Game.d("pins")) + (1 if Game.has_perm("pin") else 0)
	calls_left = int(Game.d("calls")) + (1 if Game.has_perm("call") else 0)
	curator = CURATORS[rng.randi() % CURATORS.size()]
	var female := rng.randf() < 0.4
	p["female"] = female
	p["first"] = (Looks.FEMALE if female else Looks.MALE)[rng.randi() % (Looks.FEMALE if female else Looks.MALE).size()]
	var sur: String = Looks.SURNAMES[rng.randi() % Looks.SURNAMES.size()]
	p["last"] = sur + "а" if female else sur
	p["look"] = Looks.random_look(rng, female, 1, "office")
	var lk: Dictionary = p["look"]
	# цель всегда в чём-то заметном: шапка и вещь
	if lk["hat"] == "":
		lk["hat"] = "beret" if female else "fedora"
	if lk["item"] == "" or lk["item"] == "paper":
		lk["item"] = ["umbrella", "briefcase", "bag"][rng.randi() % 3]
		if female and lk["item"] == "briefcase":
			lk["item"] = "bag"
	lk["torso"] = "coat" if rng.randf() < 0.7 else "parka"
	p["sig"] = SIGS.keys()[rng.randi() % SIGS.size()]
	p["morning"] = MORNINGS.keys()[rng.randi() % MORNINGS.size()]
	var lunches := LUNCHES.keys().filter(func(k): return k != p["morning"])
	p["lunch"] = lunches[rng.randi() % lunches.size()]
	p["habit"] = HABITS.keys()[rng.randi() % HABITS.size()]
	p["work"] = WORKS.keys()[rng.randi() % WORKS.size()]
	p["evening"] = EVENINGS.keys()[rng.randi() % EVENINGS.size()]
	_home()
	var sg: Dictionary = SIGS[p["sig"]]
	var nick: String = sg["nick"][1 if female else 0]
	fmt = {"He": "Она" if female else "Он", "he": "она" if female else "он", "him": "её" if female else "его",
		"a": "а" if female else "", "sya": "ась" if female else "ся", "Man": "Женщина" if female else "Мужчина",
		"man": "женщина" if female else "мужчина", "nick": nick, "Nick": nick.capitalize(),
		"hat": Looks.HAT_WORDS.get(lk["hat"], ""), "coat": Looks.coat_word(lk), "carry": Looks.ITEM_WORDS.get(lk["item"], ""),
		"name": "%s %s" % [p["first"], p["last"]], "apt": p["apt"], "fl": int(p["home_f"]) + 1, "house": p["house_word"]}
	_schedule()
	_cards()
	for id in Game.d("known"):
		learn(id, 100.0, "куратор")
		known_ids.append(id)


func _home() -> void:
	var res := city.buildings.filter(func(b): return b["kind"] == "res" and int(b["n"]) >= 5 and b["base"] == "res")
	var b: Dictionary = res[rng.randi() % res.size()]
	var fs := range(1, int(b["n"])).filter(func(ff): return b["floors"].has(ff) and (b["floors"][ff] as Array).size() > 0)
	var f: int = fs[rng.randi() % fs.size()]
	var apt: int = (b["floors"][f] as Array)[rng.randi() % (b["floors"][f] as Array).size()]
	p["home_bid"] = b["id"]
	p["home_f"] = f
	p["apt"] = apt
	var living := {}
	var kitchen := {}
	for rid in b["rooms"]:
		var rm: Dictionary = city.rooms[rid]
		if int(rm["apt"]) == apt and int(rm["f"]) == f:
			if rm["kind"] == "living":
				living = rm
			elif rm["kind"] == "kitchen":
				kitchen = rm
	p["living"] = living
	p["kitchen"] = kitchen
	var n := int(b["n"])
	var words := {5: "пяти", 6: "шести", 7: "семи", 8: "восьми", 9: "девяти", 10: "десяти", 11: "одиннадцати", 12: "двенадцати",
		13: "тринадцати", 14: "четырнадцати", 15: "пятнадцати", 16: "шестнадцати"}
	p["house_word"] = ("%sэтажке" % words[n]) if words.has(n) else ("%d-этажке" % n)
	var idx := 0
	for bb in city.buildings:
		if bb["kind"] == "res":
			idx += 1
		if bb["id"] == b["id"]:
			break
	p["house_n"] = idx


func place(key: String) -> Dictionary:
	if key == "Дом":
		var rm: Dictionary = p["living"]
		var spot: Dictionary = rm["spots"][0] if (rm["spots"] as Array).size() > 0 else {"x": (float(rm["x0"]) + float(rm["x1"])) / 2.0}
		return {"area": city.area_of_floor(int(p["home_bid"]), int(p["home_f"])), "x": float(spot["x"]), "name": "Дом"}
	if key == "Кухня":
		var rk: Dictionary = p["kitchen"]
		return {"area": city.area_of_floor(int(p["home_bid"]), int(p["home_f"])), "x": float(rk["spots"][0]["x"]), "name": "Дом"}
	if key == "Площадка":
		return city.places.get("Площадка", city.places["Двор"])
	return city.places.get(key, city.places["Сквер"])


func _schedule() -> void:
	## Расписание дня цели: утро, работа, перекур, обед, вечер, дом.
	var s: Array = []
	var h := 8.0
	var mo: Dictionary = MORNINGS[p["morning"]]
	s.append({"h": 6.0, "key": "Дом", "act": "sofa"})
	var hm := rng.randf_range(8.2, 8.7)
	s.append({"h": hm, "key": p["morning"], "act": mo["act"]})
	var hw := hm + 0.7
	s.append({"h": hw, "key": p["work"], "act": "desk"})
	var hh1 := rng.randf_range(10.3, 11.2)
	s.append({"h": hh1, "key": p["habit"], "act": "smoke"})
	s.append({"h": hh1 + 0.45, "key": p["work"], "act": "desk"})
	var hl := rng.randf_range(12.6, 13.3)
	s.append({"h": hl, "key": p["lunch"], "act": LUNCHES[p["lunch"]]["act"]})
	s.append({"h": hl + 0.8, "key": p["work"], "act": "desk"})
	var hh2 := rng.randf_range(15.4, 16.0)
	s.append({"h": hh2, "key": p["habit"], "act": "smoke"})
	s.append({"h": hh2 + 0.4, "key": p["work"], "act": "desk"})
	var he := rng.randf_range(17.6, 18.3)
	s.append({"h": he, "key": p["evening"], "act": "wait"})
	s.append({"h": he + 0.6, "key": "Кухня", "act": "stove"})
	s.append({"h": he + 1.5, "key": "Дом", "act": "sofa"})
	var hn := rng.randf_range(20.6, 21.3)
	s.append({"h": hn, "key": p["habit"], "act": "smoke"})
	s.append({"h": hn + 0.45, "key": "Дом", "act": "bed"})
	p["sched"] = s
	p["h_morning"] = hm
	p["h_lunch"] = hl
	p["h_habit"] = [hh1, hh2, hn]
	p["h_evening"] = he
	fmt["mt"] = hhmm(hm + 0.15)
	fmt["lt"] = hhmm(hl + 0.15)
	fmt["lt2"] = hhmm(hl + 1.7)
	fmt["h1"] = hhmm(hh1 + 0.1)
	fmt["h2"] = hhmm(hh2 + 0.1)
	fmt["hn"] = hhmm(hn + 0.1)
	fmt["et"] = hhmm(he + 0.15)
	fmt["et2"] = hhmm(he + 1.6)
	fmt["mtxt"] = MORNINGS[p["morning"]]["txt"]
	fmt["where"] = HABITS[p["habit"]]["where"]
	fmt["work"] = WORKS[p["work"]]


func brain_sched(key_sched: Array) -> Array:
	var out := []
	for e in key_sched:
		var pl := place(e["key"])
		out.append({"h": e["h"], "area": pl["area"], "x": float(pl["x"]) + rng.randf_range(-6, 6), "act": e["act"], "name": e["key"]})
	return out


func decoy_sched(i: int) -> Array:
	## Двойник ходит по «искажённым» местам, чтобы ложная запись вела к нему.
	var s: Array = []
	var mo: Dictionary = MORNINGS[p["morning"]]
	var lu: Dictionary = LUNCHES[p["lunch"]]
	var hb: Dictionary = HABITS[p["habit"]]
	var ev: Dictionary = EVENINGS[p["evening"]]
	var works := WORKS.keys()
	var wk: String = works[(works.find(p["work"]) + 1 + i) % works.size()]
	s.append({"h": 6.0, "key": "Сквер", "act": "idle"})
	s.append({"h": float(p["h_morning"]) + 2.4 + rng.randf_range(-0.3, 0.3), "key": mo["dloc"], "act": "idle"})
	s.append({"h": 10.0 + rng.randf_range(0, 0.5), "key": wk, "act": "desk"})
	s.append({"h": float(p["h_habit"][0]) + 2.8, "key": hb["dloc"], "act": "smoke"})
	s.append({"h": float(p["h_habit"][0]) + 3.3, "key": wk, "act": "desk"})
	s.append({"h": float(p["h_lunch"]) + 1.6, "key": lu["dloc"], "act": "eat" if lu["dloc"] == "Кафе" else "shop"})
	s.append({"h": float(p["h_lunch"]) + 2.4, "key": wk, "act": "desk"})
	s.append({"h": float(p["h_evening"]) + 1.5, "key": ev["dloc"], "act": "wait"})
	s.append({"h": float(p["h_evening"]) + 2.2, "key": "Метро", "act": "away"})
	if i % 2 == 1:
		s[0] = {"h": 6.0, "key": "Метро", "act": "away"}
	var out := []
	for e in s:
		var pl := place(e["key"])
		out.append({"h": e["h"], "area": pl["area"], "x": float(pl["x"]) + rng.randf_range(-30, 30), "act": e["act"], "name": e["key"]})
	return out


func decoy_look(i: int) -> Dictionary:
	## Похожий человек: две из трёх примет совпадают.
	var lk: Dictionary = p["look"].duplicate(true)
	var pal: Array = lk["pal"]
	match i % 3:
		0:
			var others := ["fedora", "cap", "beret", "beanie", "hood"].filter(func(h): return h != lk["hat"])
			lk["hat"] = others[rng.randi() % others.size()]
			if not p["female"] and lk["hat"] == "beret":
				lk["hat"] = "cap"
		1:
			var ci := (int(lk["coat_i"]) + 1 + rng.randi() % 6) % Looks.COAT_COLS.size()
			lk["coat_i"] = ci
			pal[Looks.TOP] = Looks.COAT_COLS[ci]
		2:
			var items := ["umbrella", "briefcase", "bag", "backpack", ""].filter(func(h): return h != lk["item"])
			lk["item"] = items[rng.randi() % items.size()]
	pal[Looks.SKIN] = Looks.SKINS[rng.randi() % Looks.SKINS.size()]
	lk["glasses"] = rng.randf() < 0.3
	return lk


func decoy_gait(i: int) -> String:
	var gs := ["", "limp", "hunch", "glance"].filter(func(g): return g != p["sig"])
	if i % 3 == 2:
		return p["sig"]
	return gs[rng.randi() % gs.size()]


# ======================= записи =======================

func _card(id: String, title: String, txt: String, haze: String, dist: String, empty: String, w: float,
		place_k: String = "", dplace: String = "", hours: Array = []) -> void:
	cards.append({"id": id, "title": title, "text": txt, "haze": haze, "dist": dist, "empty": empty, "w": w,
		"clar": 0.0, "known": false, "pinned": false, "own": true, "place": place_k, "dplace": dplace, "hours": hours, "kind": "clue",
		"src": ""})


func _cards() -> void:
	var sg: Dictionary = SIGS[p["sig"]]
	var mo: Dictionary = MORNINGS[p["morning"]]
	var lu: Dictionary = LUNCHES[p["lunch"]]
	var hb: Dictionary = HABITS[p["habit"]]
	var ev: Dictionary = EVENINGS[p["evening"]]
	var lk: Dictionary = p["look"]
	var dl := decoy_look(0)
	_card("portrait", "Портрет", f("{Man} {hat}, {coat} {carry}."), f("{Man}… {hat}? Пальто было тёмное… или светлое?"),
		f("{Man} %s, %s." % [Looks.HAT_WORDS.get(dl["hat"], ""), Looks.coat_word(dl)]), f("Что-то про {man}…"), 1.6)
	_card("gait", "Походка", f(sg["txt"]), f(sg["haze"]), f(sg["dist"]), f(sg["empty"]), 0.4)
	_card("morning", "Утро", f("Около {mt} {mtxt}."), f("Утром, около {mt}… или позже?"),
		f("Около %s %s." % [hhmm(float(p["h_morning"]) + 2.5), mo["dtxt"]]), "Что-то про утро…", 1.0,
		p["morning"], mo["dloc"], [p["h_morning"]])
	_card("work", "Работа", f("Работает {work}."), f("Работает… в «Граните»? Или в НИИ?"),
		f("Работает %s." % WORKS[WORKS.keys()[(WORKS.keys().find(p["work"]) + 1) % WORKS.size()]]), "Что-то про работу…", 0.9,
		p["work"], "", [])
	_card("lunch", "Обед", f(lu["txt"]), f("Обед… в {lt}? Или позже?"), f(lu["dtxt"]), "Что-то про обед…", 1.0,
		p["lunch"], lu["dloc"], [p["h_lunch"]])
	_card("habit", "Привычка", f("Курит один{a} {where}: около {h1}, {h2} и вечером, около {hn}."), f("Курит… {where}? Кажется."),
		f("Курит один{a} %s около %s." % [hb["dwhere"], hhmm(float(p["h_habit"][0]) + 3.0)]), "Что-то про сигареты…", 0.7,
		p["habit"], hb["dloc"], p["h_habit"])
	_card("evening", "Вечер", f(ev["txt"]), f("Вечером… где-то у метро? Около {et}?"), f(ev["dtxt"]), "Что-то про вечер…", 1.0,
		p["evening"], ev["dloc"], [p["h_evening"]])
	_card("home", "Дом", f("Живёт в {house}, {fl}-й этаж, кв. {apt}."), f("Квартира… {apt}? Или около того."),
		f("Живёт в доме у гаражей, кв. %d." % (int(p["apt"]) + 3)), "Что-то про дом…", 1.0, "Дом", "", [])


func card(id: String) -> Dictionary:
	for c in cards:
		if c["id"] == id:
			return c
	return {}


func learn(id: String, clar: float = 100.0, src: String = "") -> bool:
	## Новая или подтверждённая запись. true — если узнали впервые.
	var c := card(id)
	if c.is_empty():
		return false
	var first: bool = not c["known"]
	c["known"] = true
	c["clar"] = maxf(float(c["clar"]), clar)
	if src != "":
		c["src"] = src
	return first


func add_foreign(id: String, title: String, txt: String, useful: Dictionary = {}) -> Dictionary:
	for c in cards:
		if c["id"] == id:
			return c
	var c := {"id": id, "title": title, "text": txt, "haze": txt.substr(0, txt.length() / 2) + "…", "dist": txt, "empty": "Чьё-то воспоминание…",
		"w": 1.25, "clar": 100.0, "known": true, "pinned": false, "own": false, "place": "", "dplace": "", "hours": [], "kind": "foreign",
		"use": useful, "src": "чужая память"}
	cards.append(c)
	return c


func add_tail(id: String, txt: String) -> void:
	for t in tails:
		if t["id"] == id:
			return
	tails.append({"id": id, "text": txt, "done": false})


func clear_tail(id: String) -> void:
	for t in tails:
		if t["id"] == id:
			t["done"] = true


func open_tails() -> Array:
	return tails.filter(func(t): return not t["done"])


func stage(c: Dictionary) -> String:
	var v := float(c["clar"])
	if v >= 70.0:
		return "clear"
	if v >= 40.0:
		return "haze"
	if v >= 15.0:
		return "dist"
	return "empty"


func text(c: Dictionary) -> String:
	match stage(c):
		"clear": return c["text"]
		"haze": return c["text"] + "\n" + c["haze"] if float(c["clar"]) > 55.0 else c["haze"]
		"dist": return c["dist"]
	return c["empty"]


func cur_place(c: Dictionary) -> String:
	## Место, куда ведёт запись сейчас (искажённая ведёт не туда).
	if stage(c) == "dist" and c["dplace"] != "":
		return c["dplace"]
	if stage(c) == "empty":
		return ""
	return c["place"]


func memory() -> float:
	var n := 0
	var s := 0.0
	for c in cards:
		if c["known"] and c["own"]:
			n += 1
			s += float(c["clar"])
	if n == 0:
		return 100.0
	return s / n


func spend(cost: float) -> void:
	## Цена памяти: бьёт по всем известным записям с их весом.
	var k := cost * mem_mult
	for c in cards:
		if not c["known"]:
			continue
		var w := float(c["w"]) * rng.randf_range(0.8, 1.2)
		if c["pinned"]:
			w *= 0.35
		c["clar"] = maxf(0.0, float(c["clar"]) - k * w)


func regen(dt: float) -> void:
	## В теле память медленно возвращается: 1 пункт за 12 секунд.
	for c in cards:
		if c["known"] and c["own"]:
			c["clar"] = minf(100.0, float(c["clar"]) + dt / 12.0)


func forecast(cost: float) -> int:
	## Сколько записей ухудшат стадию при такой цене.
	var n := 0
	for c in cards:
		if not c["known"]:
			continue
		var w := float(c["w"]) * (0.35 if c["pinned"] else 1.0)
		var after := float(c["clar"]) - cost * mem_mult * w
		var tmp := {"clar": after}
		if stage(tmp) != stage(c):
			n += 1
	return n


func informant_line(prof: String) -> Array:
	## [id записи, реплика] для информатора.
	var mo: Dictionary = MORNINGS[p["morning"]]
	var lu: Dictionary = LUNCHES[p["lunch"]]
	match prof:
		"vendor":
			if p["morning"] == "Киоск":
				return ["morning", f("{Nick}, {hat}? Газету берёт, каждое утро к {mt}. Встанет, постоит…")]
			return ["morning", f("{Nick}, {hat}? Газет не берёт. По утрам, к {mt}, {mtxt} — сам видел.")]
		"barista":
			return ["lunch", f(lu["barista"])]
		"guard":
			if p["work"] == "Офис":
				return ["habit", f("Наш-то, {nick}, опять курит {where}. К {h1} и после обеда, к {h2}. Говорил же — не положено.")]
			return ["work", f("Не наш. В НИИ работает, на третьем. А курит {where} — видел с поста, к {h1}.")]
		"janitor":
			return ["home", f("{Nick}-то? В {house}, {fl}-й этаж, кв. {apt}. Ключ под ковриком держит, дурень.")]
		"pensioner":
			var opts := [["gait", f(SIGS[p["sig"]]["gossip"])], ["portrait", f("{Nick}-то этот? Всегда {hat}, {coat}, {carry}.")],
				["evening", f(EVENINGS[p["evening"]]["txt"])]]
			return opts[rng.randi() % opts.size()]
		"cashier":
			return ["portrait", f("Помню. {Man} {hat}, {coat}. Берёт одно и то же, сдачу не считает.")]
	return []


func gossip_line() -> Array:
	var opts := [["gait", f(SIGS[p["sig"]]["gossip"])], ["lunch", f(LUNCHES[p["lunch"]]["gossip"])],
		["habit", f("Курит {he} {where}. К {h1}, и вечером ещё.")], ["home", f("Так {he} из {house}, кв. {apt}.")],
		["morning", f("Каждое утро {mtxt}, к {mt}. Как часы.")]]
	return opts[rng.randi() % opts.size()]


func item_cards() -> Array:
	## Улики в квартире цели: [предмет, id записи, название, текст].
	var sg: Dictionary = SIGS[p["sig"]]
	var lu: Dictionary = LUNCHES[p["lunch"]]
	var ev: Dictionary = EVENINGS[p["evening"]]
	return [["photo", "portrait", "Фото в рамке", f("{He}, {hat}, {coat}. Снят{a} у входа в «Универсам».")],
		["pills", "gait", f(sg["item"][0]), f(sg["item"][1])],
		["clue", "lunch", f(lu["item"][0]), f(lu["item"][1])],
		["clue", "evening", f(ev["item"][0]), f(ev["item"][1])],
		["clue", "habit", "Пачка «Примы»", f("Сигареты и спички. Курит {where}.")]]
