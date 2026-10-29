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
	Color(0.27, 0.32, 0.27), Color(0.45, 0.22, 0.2), Color(0.5, 0.44, 0.34), Color(0.28, 0.28, 0.32)]
const COAT_NAMES := ["тёмное", "светлое", "синее", "коричневое", "зелёное", "бордовое", "бежевое", "серое"]
const HAT_COLS := [Color(0.2, 0.18, 0.17), Color(0.45, 0.42, 0.38), Color(0.55, 0.2, 0.2), Color(0.25, 0.27, 0.35), Color(0.4, 0.33, 0.25)]
const HAIR_COLS := [Color(0.13, 0.11, 0.1), Color(0.35, 0.24, 0.15), Color(0.55, 0.42, 0.25), Color(0.6, 0.6, 0.58), Color(0.25, 0.2, 0.18)]
const SKINS := [Color(0.86, 0.69, 0.58), Color(0.8, 0.62, 0.5), Color(0.9, 0.75, 0.65), Color(0.72, 0.55, 0.43)]

const HAT_WORDS := {"fedora": "в шляпе", "cap": "в кепке", "beret": "в берете", "ushanka": "в ушанке", "hood": "в капюшоне",
	"beanie": "в вязаной шапке", "kerchief": "в платке", "police": "в фуражке", "helmet": "в каске", "": "без шапки"}
const TORSO_WORDS := {"coat": "пальто", "jacket": "пиджак", "parka": "куртка", "sweater": "свитер", "shirt": "рубашка",
	"uniform": "форма", "apron": "фартук", "robe": "халат"}
const ITEM_WORDS := {"briefcase": "с портфелем", "umbrella": "с зонтом", "bag": "с сумкой", "backpack": "с рюкзаком",
	"paper": "с газетой", "cane": "с тростью", "": ""}


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


static func random_look(rng: RandomNumberGenerator, female: bool, age: int, prof: String) -> Dictionary:
	var l := {"female": female, "age": age, "pal": pal_default()}
	var pal: Array = l["pal"]
	pal[SKIN] = SKINS[rng.randi() % SKINS.size()]
	pal[HAIR] = HAIR_COLS[rng.randi() % HAIR_COLS.size()] if age < 2 else Color(0.62, 0.62, 0.6)
	var ci := rng.randi() % COAT_COLS.size()
	pal[TOP] = COAT_COLS[ci]
	l["coat_i"] = ci
	pal[BOTTOM] = [Color(0.18, 0.18, 0.2), Color(0.25, 0.25, 0.3), Color(0.3, 0.27, 0.22), Color(0.2, 0.22, 0.26)][rng.randi() % 4]
	var hi := rng.randi() % HAT_COLS.size()
	pal[HAT] = HAT_COLS[hi]
	pal[ACC] = [Color(0.3, 0.25, 0.2), Color(0.15, 0.15, 0.16), Color(0.45, 0.2, 0.18), Color(0.25, 0.3, 0.4)][rng.randi() % 4]
	pal[TOP2] = [Color(0.85, 0.84, 0.8), Color(0.6, 0.65, 0.7), Color(0.75, 0.7, 0.6)][rng.randi() % 3]
	if female:
		l["hair"] = ["bob", "long", "bun", "pony", "curly"][rng.randi() % 5]
		l["hat"] = ["", "", "beret", "beanie", "hood"][rng.randi() % 5]
		if age == 2:
			l["hat"] = "kerchief" if rng.randf() < 0.6 else ""
			l["hair"] = "bun"
		l["legs"] = "skirt" if rng.randf() < 0.55 else "pants"
		l["beard"] = ""
	else:
		l["hair"] = ["short", "short", "curly", "bald"][rng.randi() % 4] if age > 0 else ["short", "curly", "long"][rng.randi() % 3]
		l["hat"] = ["", "", "fedora", "cap", "ushanka", "beanie", "hood"][rng.randi() % 7]
		l["legs"] = "pants"
		l["beard"] = ["", "", "", "mustache", "stubble", "full"][rng.randi() % 6] if age > 0 else ""
	l["torso"] = ["coat", "coat", "jacket", "parka", "sweater"][rng.randi() % 5]
	l["glasses"] = rng.randf() < (0.35 if age == 2 else 0.18)
	l["scarf"] = rng.randf() < 0.3
	l["item"] = ["", "", "briefcase", "bag", "umbrella", "backpack", "paper"][rng.randi() % 7]
	if age == 2 and rng.randf() < 0.5:
		l["item"] = "cane"
	if female and l["item"] == "briefcase":
		l["item"] = "bag"
	_uniform(l, prof, rng)
	return l


static func _uniform(l: Dictionary, prof: String, rng: RandomNumberGenerator) -> void:
	var pal: Array = l["pal"]
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
	if item in ["backpack", "bag"]:
		out.append("item_" + item)
	out.append("armb")
	out.append("legs_" + str(l.get("legs", "pants")))
	out.append("body")
	out.append("torso_" + str(l.get("torso", "coat")))
	if l.get("scarf", false):
		out.append("scarf")
	var hat: String = l.get("hat", "")
	var hair: String = l.get("hair", "short")
	if not (hat in ["hood", "kerchief", "ushanka", "helmet"] and hair in ["short", "bald", "curly"]):
		out.append("hair_" + hair)
	if l.get("beard", "") != "":
		out.append("beard_" + str(l["beard"]))
	if l.get("glasses", false):
		out.append("glasses")
	if hat != "":
		out.append("hat_" + hat)
	out.append("armf")
	if item != "" and not item in ["backpack", "bag"]:
		out.append("item_" + item)
	return out


const COAT_FORMS := [["тёмное", "тёмная", "тёмный"], ["светлое", "светлая", "светлый"], ["синее", "синяя", "синий"],
	["коричневое", "коричневая", "коричневый"], ["зелёное", "зелёная", "зелёный"], ["бордовое", "бордовая", "бордовый"],
	["бежевое", "бежевая", "бежевый"], ["серое", "серая", "серый"]]
const TORSO_GENDER := {"пальто": 0, "куртка": 1, "форма": 1, "рубашка": 1, "пиджак": 2, "свитер": 2, "фартук": 2, "халат": 2}


static func coat_word(l: Dictionary) -> String:
	var ci: int = l.get("coat_i", 0)
	var tw: String = TORSO_WORDS.get(l.get("torso", "coat"), "пальто")
	return "%s %s" % [COAT_FORMS[ci][TORSO_GENDER.get(tw, 0)], tw]


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
	var s := ", ".join(parts.slice(1))
	return "%s %s" % [who, s]
