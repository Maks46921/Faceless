class_name Looks
## Внешность людей: слои одежды, цвета, описание словами, профессии и имена.

const SKIN := 0
const HAIR := 1
const TOP := 2
const BOTTOM := 3
const SHOES := 4
const HAT := 5
const ACC := 6
const EYE := 7
const WHITE := 8
const METAL := 9
const TOP2 := 10
const ACC2 := 11

const MALE := ["Андрей", "Сергей", "Дмитрий", "Алексей", "Игорь", "Олег", "Павел", "Виктор", "Николай", "Юрий",
	"Михаил", "Артём", "Константин", "Геннадий", "Степан", "Борис", "Роман"]
const FEMALE := ["Ирина", "Ольга", "Наталья", "Елена", "Марина", "Светлана", "Татьяна", "Анна", "Галина", "Вера",
	"Людмила", "Юлия", "Ксения", "Нина", "Лариса"]
const SURNAMES := ["Савельев", "Кузнецов", "Лебедев", "Морозов", "Павлов", "Семёнов", "Голубев", "Виноградов",
	"Богданов", "Воробьёв", "Фёдоров", "Михайлов", "Беляев", "Тарасов", "Белов", "Комаров", "Орлов", "Киселёв",
	"Макаров", "Андреев", "Ковалёв", "Ильин", "Гусев", "Титов", "Баранов", "Куликов", "Сорокин", "Захаров", "Борисов"]

## Профессии: навык, голос, форма, служебный доступ.
const PROFS := {
	"office": {"name": "служащий", "voice": "КОНТОРА", "skill": "pass", "greet": "Отчёты, пропуск, девять ноль-ноль. Тут меня знают."},
	"guard": {"name": "охранник", "voice": "ОХРАНА", "skill": "keys", "greet": "Пост сдал, пост принял. Ключ от комнаты охраны — на поясе."},
	"barista": {"name": "буфетчица", "voice": "БУФЕТ", "skill": "cafe", "greet": "Кофе, суп, пирожки. Я всех тут знаю по заказу."},
	"pharm": {"name": "провизор", "voice": "МЕДИК", "skill": "med", "greet": "Пульс, зрачки, походка. Тело всегда выдаёт болезнь."},
	"cashier": {"name": "продавщица", "voice": "ПРОДАВЕЦ", "skill": "faces", "greet": "Лица запоминаю с одного раза. Работа такая."},
	"vendor": {"name": "киоскёр", "voice": "ПРОДАВЕЦ", "skill": "faces", "greet": "Газеты, сигареты, сплетни. Кто что берёт — всё помню."},
	"janitor": {"name": "дворник", "voice": "ДВОР", "skill": "keys", "greet": "Ключи от подвалов и чердаков. Метла не спрашивает пропуск."},
	"pensioner": {"name": "пенсионер", "voice": "СПЛЕТНИ", "skill": "gossip", "greet": "Сижу, смотрю. Всё вижу, всё знаю."},
	"student": {"name": "студент", "voice": "СТУДЕНТ", "skill": "quiet", "greet": "Меня никто не замечает. Удобно."},
	"worker": {"name": "рабочий", "voice": "ЭЛЕКТРИК", "skill": "wires", "greet": "Щитки, провода, рубильники. Свет — дело простое."},
	"courier": {"name": "курьер", "voice": "КУРЬЕР", "skill": "run", "greet": "Бегом — это нормально. Курьера никто не провожает взглядом."},
	"police": {"name": "милиционер", "voice": "МИЛИЦИЯ", "skill": "badge", "greet": "Форма открывает двери. И закрывает рты."},
	"teacher": {"name": "учительница", "voice": "УЧИТЕЛЬ", "skill": "errors", "greet": "Ошибки видно сразу. Особенно чужие."},
	"tramp": {"name": "бродяга", "voice": "ПОДЗЕМКА", "skill": "quiet", "greet": "Бродягу не замечают. А я знаю каждый люк и каждую решётку."},
	"resident": {"name": "жилец", "voice": "ЖИЛЕЦ", "skill": "", "greet": "Обычный человек. Ничего особенного."},
}

const COAT_COLS := [Color(0.17, 0.17, 0.19), Color(0.6, 0.6, 0.57), Color(0.22, 0.24, 0.3), Color(0.35, 0.3, 0.26),
	Color(0.27, 0.32, 0.27), Color(0.45, 0.22, 0.2), Color(0.5, 0.44, 0.34), Color(0.28, 0.28, 0.32),
	Color(0.09, 0.09, 0.1), Color(0.42, 0.52, 0.62), Color(0.58, 0.47, 0.2), Color(0.36, 0.38, 0.22), Color(0.6, 0.17, 0.15),
	Color(0.43, 0.36, 0.48)]
const COAT_NAMES := ["тёмное", "светлое", "синее", "коричневое", "зелёное", "бордовое", "бежевое", "серое",
	"чёрное", "голубое", "горчичное", "оливковое", "красное", "сиреневое"]
const HAT_COLS := [Color(0.2, 0.18, 0.17), Color(0.45, 0.42, 0.38), Color(0.55, 0.2, 0.2), Color(0.25, 0.27, 0.35), Color(0.4, 0.33, 0.25),
	Color(0.1, 0.1, 0.11), Color(0.3, 0.38, 0.3), Color(0.62, 0.58, 0.5), Color(0.38, 0.22, 0.32)]
const HAIR_COLS := [Color(0.13, 0.11, 0.1), Color(0.35, 0.24, 0.15), Color(0.55, 0.42, 0.25), Color(0.6, 0.6, 0.58), Color(0.25, 0.2, 0.18),
	Color(0.5, 0.25, 0.14), Color(0.72, 0.62, 0.42), Color(0.2, 0.14, 0.1), Color(0.42, 0.36, 0.3)]
const SKINS := [Color(0.86, 0.69, 0.58), Color(0.8, 0.62, 0.5), Color(0.9, 0.75, 0.65), Color(0.72, 0.55, 0.43),
	Color(0.93, 0.8, 0.7), Color(0.66, 0.5, 0.38), Color(0.84, 0.66, 0.52)]
const BOTTOM_COLS := [Color(0.18, 0.18, 0.2), Color(0.25, 0.25, 0.3), Color(0.3, 0.27, 0.22), Color(0.2, 0.22, 0.26),
	Color(0.12, 0.12, 0.13), Color(0.36, 0.33, 0.3), Color(0.26, 0.2, 0.18), Color(0.3, 0.32, 0.36)]
const DENIM := [Color(0.2, 0.28, 0.42), Color(0.26, 0.34, 0.48), Color(0.17, 0.2, 0.28)]
const SHOE_COLS := [Color(0.13, 0.12, 0.11), Color(0.25, 0.16, 0.1), Color(0.08, 0.08, 0.09), Color(0.32, 0.22, 0.16), Color(0.3, 0.12, 0.1)]
const ACC_COLS := [Color(0.3, 0.25, 0.2), Color(0.15, 0.15, 0.16), Color(0.45, 0.2, 0.18), Color(0.25, 0.3, 0.4),
	Color(0.55, 0.48, 0.3), Color(0.32, 0.4, 0.3), Color(0.6, 0.55, 0.5), Color(0.4, 0.28, 0.4)]
## Телосложение: m обычное, s невысокое худое, t высокое, h плотное, k коренастое (листы tools/art2x/gen_chars2x.py)
const BUILD_H := {"m": 1.0, "s": 0.88, "t": 1.12, "h": 1.0, "k": 0.9}

const HAT_WORDS := {"fedora": "в шляпе", "cap": "в кепке", "beret": "в берете", "ushanka": "в ушанке", "hood": "в капюшоне",
	"beanie": "в вязаной шапке", "kerchief": "в платке", "police": "в фуражке", "helmet": "в каске", "flatcap": "в кепке-восьмиклинке",
	"fur_hat": "в меховой шапке", "": "без шапки"}
const TORSO_WORDS := {"coat": "пальто", "jacket": "пиджак", "parka": "куртка", "sweater": "свитер", "shirt": "рубашка",
	"uniform": "форма", "apron": "фартук", "robe": "халат", "trench": "плащ", "suit": "костюм", "tracksuit": "спортивный костюм",
	"cardigan": "кофта", "fur": "шуба", "dress": "платье"}
const ITEM_WORDS := {"briefcase": "с портфелем", "umbrella": "с зонтом", "bag": "с сумкой", "backpack": "с рюкзаком",
	"paper": "с газетой", "cane": "с тростью", "stringbag": "с авоськой", "": ""}
const BUILD_WORDS := {"s": "невысокий, худой", "t": "высокий", "h": "полный", "k": "коренастый", "m": ""}


static func pal_default() -> Array:
	var p := []
	p.resize(12)
	p[SKIN] = SKINS[0]
	p[HAIR] = HAIR_COLS[0]
	p[TOP] = COAT_COLS[0]
	p[BOTTOM] = Color(0.18, 0.18, 0.2)
	p[SHOES] = Color(0.13, 0.12, 0.11)
	p[HAT] = HAT_COLS[0]
	p[ACC] = Color(0.3, 0.25, 0.2)
	p[EYE] = Color(0.08, 0.08, 0.1)
	p[WHITE] = Color(0.88, 0.87, 0.82)
	p[METAL] = Color(0.6, 0.62, 0.65)
	p[TOP2] = Color(0.85, 0.84, 0.8)
	p[ACC2] = Color(0.2, 0.18, 0.2)
	return p


static func pick_w(rng: RandomNumberGenerator, opts: Array) -> Variant:
	## Взвешенный выбор: [[значение, вес], …]
	var tot := 0.0
	for o in opts:
		tot += float(o[1])
	var r := rng.randf() * tot
	for o in opts:
		r -= float(o[1])
		if r <= 0.0:
			return o[0]
	return opts[opts.size() - 1][0]


static func _tone(c: Color, rng: RandomNumberGenerator, k: float) -> Color:
	## Тот же цвет, но у каждого свой оттенок: ткань выгорела, покрашена в другой партии.
	var v := rng.randf_range(-k, k)
	var c2 := c.lightened(v) if v > 0.0 else c.darkened(-v)
	return Color(clampf(c2.r + rng.randf_range(-0.02, 0.02), 0, 1), clampf(c2.g + rng.randf_range(-0.02, 0.02), 0, 1), clampf(c2.b + rng.randf_range(-0.02, 0.02), 0, 1))


static func random_look(rng: RandomNumberGenerator, female: bool, age: int, prof: String) -> Dictionary:
	var l := {"female": female, "age": age, "pal": pal_default()}
	var pal: Array = l["pal"]
	pal[SKIN] = _tone(SKINS[rng.randi() % SKINS.size()], rng, 0.04)
	pal[HAIR] = _tone(HAIR_COLS[rng.randi() % HAIR_COLS.size()], rng, 0.06) if age < 2 else Color(0.62, 0.62, 0.6).darkened(rng.randf() * 0.2)
	var ci := rng.randi() % COAT_COLS.size()
	pal[TOP] = _tone(COAT_COLS[ci], rng, 0.07)
	l["coat_i"] = ci
	pal[BOTTOM] = _tone(BOTTOM_COLS[rng.randi() % BOTTOM_COLS.size()], rng, 0.05)
	pal[HAT] = _tone(HAT_COLS[rng.randi() % HAT_COLS.size()], rng, 0.05)
	pal[ACC] = _tone(ACC_COLS[rng.randi() % ACC_COLS.size()], rng, 0.06)
	pal[TOP2] = [Color(0.85, 0.84, 0.8), Color(0.6, 0.65, 0.7), Color(0.75, 0.7, 0.6), Color(0.3, 0.32, 0.4), Color(0.7, 0.62, 0.45),
		Color(0.55, 0.25, 0.22)][rng.randi() % 6]
	pal[ACC2] = [Color(0.2, 0.18, 0.2), Color(0.45, 0.2, 0.2), Color(0.25, 0.3, 0.45), Color(0.3, 0.28, 0.22), Color(0.55, 0.5, 0.42)][rng.randi() % 5]
	pal[SHOES] = SHOE_COLS[rng.randi() % SHOE_COLS.size()]
	# телосложение: старики ниже и плотнее, молодые тоньше
	if age == 0:
		l["build"] = pick_w(rng, [["m", 4], ["s", 3], ["t", 3], ["h", 1]])
	elif age == 2:
		l["build"] = pick_w(rng, [["m", 3], ["s", 2], ["k", 3], ["h", 2], ["t", 1]])
	else:
		l["build"] = pick_w(rng, [["m", 5], ["s", 2], ["t", 2], ["h", 2], ["k", 2]])
	if female:
		l["hair"] = pick_w(rng, [["bob", 3], ["long", 2], ["bun", 2], ["pony", 2], ["curly", 1], ["perm", 2], ["braid", 1], ["side", 1]])
		l["hat"] = pick_w(rng, [["", 5], ["beret", 2], ["beanie", 1], ["hood", 1], ["kerchief", 1], ["fur_hat", 1]])
		if age == 2:
			l["hat"] = "kerchief" if rng.randf() < 0.5 else ("fur_hat" if rng.randf() < 0.3 else "")
			l["hair"] = pick_w(rng, [["bun", 3], ["perm", 3], ["bob", 1]])
		l["legs"] = pick_w(rng, [["skirt", 6], ["pants", 3], ["jeans", 2 if age == 0 else 0.3]])
		l["beard"] = ""
		l["torso"] = pick_w(rng, [["coat", 4], ["jacket", 1], ["parka", 2], ["sweater", 2], ["trench", 1], ["cardigan", 2], ["fur", 1.5], ["dress", 1.5]])
	else:
		if age == 0:
			l["hair"] = pick_w(rng, [["short", 3], ["curly", 1], ["long", 1], ["crop", 2], ["side", 2]])
		elif age == 2:
			l["hair"] = pick_w(rng, [["receding", 3], ["bald", 2], ["short", 2], ["side", 1]])
		else:
			l["hair"] = pick_w(rng, [["short", 4], ["curly", 1], ["bald", 1], ["crop", 2], ["side", 2], ["receding", 1]])
		l["hat"] = pick_w(rng, [["", 5], ["fedora", 2], ["cap", 1], ["flatcap", 1.5], ["ushanka", 1], ["beanie", 1], ["hood", 0.6], ["fur_hat", 0.6]])
		l["legs"] = pick_w(rng, [["pants", 5], ["jeans", 2.5 if age == 0 else 0.6]])
		l["beard"] = pick_w(rng, [["", 7], ["mustache", 2], ["stubble", 2], ["full", 1], ["goatee", 0.8]]) if age > 0 else pick_w(rng, [["", 6], ["stubble", 1]])
		l["torso"] = pick_w(rng, [["coat", 4], ["jacket", 2], ["parka", 2], ["sweater", 2], ["trench", 1.2], ["suit", 1], ["tracksuit", 0.8 if age == 0 else 0.3], ["shirt", 0.6]])
	l["shoes"] = "boots" if rng.randf() < (0.5 if l["legs"] == "skirt" else 0.3) else "low"
	if l["legs"] == "jeans":
		pal[BOTTOM] = DENIM[rng.randi() % DENIM.size()]
	l["glasses"] = rng.randf() < (0.35 if age == 2 else 0.18)
	l["scarf"] = rng.randf() < 0.3
	# черты лица для портрета: форма лица, глаза, нос, рот, брови
	l["face"] = pick_w(rng, [[0, 4], [1, 3 if build_wide(l) else 1.5], [2, 2]])
	l["eyes"] = rng.randi() % 3
	l["nose"] = pick_w(rng, [[0, 3], [1, 2], [2, 2]])
	l["mouth"] = rng.randi() % 2
	l["brows"] = 1 if (not female and rng.randf() < 0.55) else (1 if rng.randf() < 0.15 else 0)
	l["item"] = pick_w(rng, [["", 4], ["briefcase", 1], ["bag", 1], ["umbrella", 1], ["backpack", 1], ["paper", 1], ["stringbag", 1]])
	if age == 2 and rng.randf() < 0.5:
		l["item"] = "cane"
	if female and l["item"] == "briefcase":
		l["item"] = "bag"
	# узор ткани: клетка, полоска, твид, ёлочка
	match l["torso"]:
		"sweater", "tracksuit":
			l["pattern"] = pick_w(rng, [[0, 6], [2, 3], [5, 1]])
		"shirt":
			l["pattern"] = pick_w(rng, [[0, 3], [1, 2], [3, 3]])
		"coat", "trench":
			l["pattern"] = pick_w(rng, [[0, 8], [4, 2], [3, 1]])
		"jacket", "suit":
			l["pattern"] = pick_w(rng, [[0, 6], [1, 1], [4, 2], [5, 1]])
		"dress", "cardigan":
			l["pattern"] = pick_w(rng, [[0, 4], [3, 1], [2, 1]])
		_:
			l["pattern"] = 0
	_uniform(l, prof, rng)
	return l


static func class_style(l: Dictionary, cls: int, rng: RandomNumberGenerator) -> void:
	## Класс по этажу: низ башни одет попроще и потёртее, верх — строго и дорого.
	var pal: Array = l["pal"]
	if l.get("torso", "") in ["uniform", "robe", "apron"]:
		return
	if cls == 2:
		l["torso"] = pick_w(rng, [["coat", 3], ["trench", 2], ["suit", 2 if not l["female"] else 0], ["fur", 2 if l["female"] else 0]])
		l["legs"] = "pants" if l["legs"] == "jeans" else l["legs"]
		if not l["female"] and l["age"] > 0:
			l["hat"] = ["fedora", "fedora", ""][rng.randi() % 3]
		elif l["female"] and l["age"] > 0:
			l["hat"] = ["beret", "", ""][rng.randi() % 3]
		if l["age"] == 1:
			l["item"] = "briefcase" if not l["female"] else "bag"
		l["glasses"] = l["glasses"] or rng.randf() < 0.2
		l["scarf"] = true
		pal[TOP] = (pal[TOP] as Color).darkened(0.15)
		pal[BOTTOM] = Color(0.14, 0.14, 0.17)
	elif cls == 0:
		if l["torso"] in ["coat", "suit", "trench", "fur"]:
			l["torso"] = ["parka", "sweater", "jacket", "tracksuit", "cardigan"][rng.randi() % 5]
		if not l["female"] and l["hat"] == "fedora":
			l["hat"] = ["cap", "ushanka", "beanie"][rng.randi() % 3]
		if l["item"] == "briefcase":
			l["item"] = "bag"
		var c: Color = pal[TOP]
		pal[TOP] = c.lerp(Color(c.v, c.v, c.v), 0.35)


static func _uniform(l: Dictionary, prof: String, rng: RandomNumberGenerator) -> void:
	var pal: Array = l["pal"]
	if prof in ["police", "guard", "barista", "pharm", "cashier", "janitor", "worker", "tramp", "courier"]:
		l["pattern"] = 0
		if l["legs"] == "skirt" and prof in ["police", "guard", "janitor", "worker", "tramp", "courier"]:
			l["legs"] = "pants"
	match prof:
		"police":
			l["torso"] = "uniform"; l["hat"] = "police"; l["legs"] = "pants"; l["item"] = ""
			pal[TOP] = Color(0.3, 0.36, 0.45); pal[BOTTOM] = Color(0.26, 0.31, 0.4); pal[HAT] = Color(0.3, 0.36, 0.45); pal[ACC2] = Color(0.7, 0.18, 0.15)
		"guard":
			l["torso"] = "uniform"; l["hat"] = "cap"; l["legs"] = "pants"; l["item"] = ""
			pal[TOP] = Color(0.12, 0.12, 0.13); pal[BOTTOM] = Color(0.12, 0.12, 0.13); pal[HAT] = Color(0.12, 0.12, 0.13); pal[ACC2] = Color(0.55, 0.5, 0.3)
		"barista":
			l["torso"] = "apron"; l["hat"] = ""; l["item"] = ""; pal[TOP2] = Color(0.85, 0.84, 0.8); pal[TOP] = Color(0.45, 0.25, 0.22)
		"pharm":
			l["torso"] = "robe"; l["hat"] = ""; l["item"] = ""; pal[TOP] = Color(0.86, 0.86, 0.84)
		"cashier":
			l["torso"] = "robe"; l["hat"] = ""; l["item"] = ""; pal[TOP] = Color(0.4, 0.5, 0.62)
		"vendor":
			l["torso"] = "parka"; l["item"] = ""
		"janitor":
			l["torso"] = "parka"; l["hat"] = "ushanka" if not l["female"] else "kerchief"; l["item"] = ""
			pal[TOP] = Color(0.75, 0.42, 0.15)
		"worker":
			l["torso"] = "parka"; l["hat"] = "helmet"; pal[HAT] = Color(0.85, 0.65, 0.15); pal[TOP] = Color(0.3, 0.35, 0.4); l["item"] = "bag"
		"tramp":
			l["torso"] = "parka"; l["hat"] = "ushanka"; l["item"] = "bag"; l["glasses"] = false
			pal[TOP] = Color(0.3, 0.28, 0.22); pal[BOTTOM] = Color(0.24, 0.22, 0.2)
			if not l["female"]:
				l["beard"] = "full"
		"courier":
			l["torso"] = "parka"; l["item"] = "backpack"; l["hat"] = "cap"; pal[TOP] = Color(0.25, 0.4, 0.55)
		"office":
			if rng.randf() < 0.6:
				l["torso"] = "coat" if rng.randf() < 0.5 else "jacket"
				if not l["female"]:
					l["item"] = "briefcase"
		"student":
			l["item"] = "backpack"; l["torso"] = ["parka", "jacket", "sweater"][rng.randi() % 3]
		"pensioner":
			if l["age"] < 2:
				l["age"] = 2
			if rng.randf() < 0.5:
				l["item"] = "cane"


static func layers(l: Dictionary, raining: bool = false) -> Array:
	var out := []
	var item: String = l.get("item", "")
	if item == "umbrella" and raining:
		item = "umbrella_open"
	var torso := str(l.get("torso", "coat"))
	var puffy := torso in ["parka", "fur"]
	if item in ["backpack", "bag"]:
		out.append("item_" + item)
	out.append("armb_puffy" if puffy else "armb")
	out.append("legs_" + str(l.get("legs", "pants")))
	out.append("shoes_" + str(l.get("shoes", "low")))
	out.append("body")
	if l.get("age", 1) == 2:
		out.append("wrinkles")
	out.append("torso_" + torso)
	if l.get("scarf", false):
		out.append("scarf")
	var hat: String = l.get("hat", "")
	var hair: String = l.get("hair", "short")
	if not (hat in ["hood", "kerchief", "ushanka", "helmet", "fur_hat"] and hair in ["short", "bald", "curly", "crop", "receding", "side"]):
		out.append("hair_" + hair)
	if l.get("beard", "") != "":
		out.append("beard_" + str(l["beard"]))
	if l.get("glasses", false):
		out.append("glasses")
	if hat != "":
		out.append("hat_" + hat)
	out.append("armf_puffy" if puffy else "armf")
	if item != "" and not item in ["backpack", "bag"]:
		out.append("item_" + item)
	return out


const COAT_FORMS := [["тёмное", "тёмная", "тёмный"], ["светлое", "светлая", "светлый"], ["синее", "синяя", "синий"],
	["коричневое", "коричневая", "коричневый"], ["зелёное", "зелёная", "зелёный"], ["бордовое", "бордовая", "бордовый"],
	["бежевое", "бежевая", "бежевый"], ["серое", "серая", "серый"], ["чёрное", "чёрная", "чёрный"], ["голубое", "голубая", "голубой"],
	["горчичное", "горчичная", "горчичный"], ["оливковое", "оливковая", "оливковый"], ["красное", "красная", "красный"],
	["сиреневое", "сиреневая", "сиреневый"]]
const TORSO_GENDER := {"пальто": 0, "куртка": 1, "форма": 1, "рубашка": 1, "пиджак": 2, "свитер": 2, "фартук": 2, "халат": 2,
	"плащ": 2, "костюм": 2, "спортивный костюм": 2, "кофта": 1, "шуба": 1, "платье": 0}


static func coat_word(l: Dictionary) -> String:
	var ci: int = l.get("coat_i", 0)
	var tw: String = TORSO_WORDS.get(l.get("torso", "coat"), "пальто")
	return "%s %s" % [COAT_FORMS[ci][TORSO_GENDER.get(tw, 0)], tw]


static func build_wide(l: Dictionary) -> bool:
	return String(l.get("build", "m")) in ["h", "k"]


static func describe(l: Dictionary) -> String:
	var who := "Женщина" if l.get("female", false) else "Мужчина"
	if l.get("age", 1) == 2:
		who = "Старушка" if l.get("female", false) else "Старик"
	var parts := [who, HAT_WORDS.get(l.get("hat", ""), "")]
	parts.append(coat_word(l))
	var it: String = ITEM_WORDS.get(l.get("item", ""), "")
	if it != "":
		parts.append(it)
	if l.get("glasses", false):
		parts.append("в очках")
	if l.get("scarf", false):
		parts.append("в шарфе")
	match l.get("beard", ""):
		"mustache": parts.append("с усами")
		"full": parts.append("с бородой")
		"goatee": parts.append("с бородкой")
	var bw: String = BUILD_WORDS.get(l.get("build", "m"), "")
	if bw != "":
		parts.append(bw if not l.get("female", false) else bw.replace("ий", "ая").replace("ый", "ая").replace("ой", "ая"))
	var s := ", ".join(parts.slice(1))
	return "%s %s" % [who, s]
