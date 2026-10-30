extends Node
## Состояние между делами: сложность, настройки, служба (уровень, репутация, допуски), подсказки.

const SAVE := "user://faceless2.cfg"
const DIFFS := {
	"Стажёр": {
		"desc": "Куратор знает много: портрет, походку и утро. Память тает медленнее, двойников трое, свидетель молчит полторы минуты.",
		"known": ["portrait", "gait", "morning"], "mem_mult": 0.7, "witness_t": 90.0, "susp_mult": 0.7,
		"hour_s": 200.0, "decoys": 3, "people": 200, "calls": 3, "pins": 2, "cams": 2, "density_mult": 0.8,
	},
	"Оператор": {
		"desc": "Только портрет и утренняя привычка. Обычная цена памяти, пятеро похожих, свидетель молчит минуту с небольшим.",
		"known": ["portrait", "morning"], "mem_mult": 1.0, "witness_t": 70.0, "susp_mult": 1.0,
		"hour_s": 180.0, "decoys": 5, "people": 240, "calls": 2, "pins": 1, "cams": 4, "density_mult": 1.0,
	},
	"Призрак": {
		"desc": "Лица нет. Только где цель бывает утром. Память тает быстро, похожих семеро, свидетель зовёт милицию меньше чем через минуту.",
		"known": ["morning"], "mem_mult": 1.35, "witness_t": 50.0, "susp_mult": 1.3,
		"hour_s": 160.0, "decoys": 7, "people": 280, "calls": 1, "pins": 1, "cams": 6, "density_mult": 1.25,
	},
}
const RANKS := ["стажёр службы", "оператор III класса", "оператор II класса", "оператор I класса", "старший оператор", "тень"]
const PERMS := {
	"pin": {"name": "Лишняя булавка", "cost": 2, "desc": "+1 булавка на доске: запись тает втрое медленнее."},
	"call": {"name": "Ещё звонок куратору", "cost": 2, "desc": "+1 звонок с таксофона: восстанавливает выцветшую запись."},
	"claws": {"name": "Цепкие клешни", "cost": 3, "desc": "Клешни вне тела стоят на четверть меньше памяти."},
	"dense": {"name": "Плотный дух", "cost": 3, "desc": "Вне тела плотность тает на треть медленнее."},
	"quiet": {"name": "Тихий вход", "cost": 4, "desc": "Вход в тело на 30% дешевле."},
}

var difficulty := "Оператор"
var level := 1
var reputation := 0
var cases_closed := 0
var cases_failed := 0
var perms: Array = []
var hints_seen := {}
var volume := 0.8
var music := 0.6
var fullscreen := false
var ui_big := false
var seed_once := 0
var last_result := {}
var stats := {"kills": 0, "jumps": 0, "bodies_hidden": 0, "witness": 0}


func _ready() -> void:
	load_cfg()
	_apply_window()


func d(key: String):
	return DIFFS[difficulty][key]


func rank() -> String:
	return RANKS[clampi(level - 1, 0, RANKS.size() - 1)]


func has_perm(p: String) -> bool:
	return p in perms


func hint_once(id: String) -> bool:
	if hints_seen.has(id):
		return false
	hints_seen[id] = true
	return true


func load_cfg() -> void:
	var c := ConfigFile.new()
	if c.load(SAVE) != OK:
		return
	difficulty = c.get_value("svc", "difficulty", difficulty)
	level = c.get_value("svc", "level", 1)
	reputation = c.get_value("svc", "rep", 0)
	cases_closed = c.get_value("svc", "closed", 0)
	cases_failed = c.get_value("svc", "failed", 0)
	perms = c.get_value("svc", "perms", [])
	stats = c.get_value("svc", "stats", stats)
	last_result = {"seed": c.get_value("svc", "last_seed", 0)}
	hints_seen = c.get_value("ui", "hints", {})
	volume = c.get_value("ui", "volume", 0.8)
	music = c.get_value("ui", "music", 0.6)
	fullscreen = c.get_value("ui", "fullscreen", false)
	ui_big = c.get_value("ui", "big", false)


func save_cfg() -> void:
	var c := ConfigFile.new()
	c.set_value("svc", "difficulty", difficulty)
	c.set_value("svc", "level", level)
	c.set_value("svc", "rep", reputation)
	c.set_value("svc", "closed", cases_closed)
	c.set_value("svc", "failed", cases_failed)
	c.set_value("svc", "perms", perms)
	c.set_value("svc", "stats", stats)
	c.set_value("svc", "last_seed", int(last_result.get("seed", 0)))
	c.set_value("ui", "hints", hints_seen)
	c.set_value("ui", "volume", volume)
	c.set_value("ui", "music", music)
	c.set_value("ui", "fullscreen", fullscreen)
	c.set_value("ui", "big", ui_big)
	c.save(SAVE)


func _apply_window() -> void:
	if fullscreen:
		DisplayServer.window_set_mode(DisplayServer.WINDOW_MODE_FULLSCREEN)
	AudioServer.set_bus_volume_db(0, linear_to_db(maxf(0.001, volume)))


func toggle_fullscreen() -> void:
	fullscreen = not fullscreen
	DisplayServer.window_set_mode(DisplayServer.WINDOW_MODE_FULLSCREEN if fullscreen else DisplayServer.WINDOW_MODE_WINDOWED)
	save_cfg()


func reset_service() -> void:
	level = 1
	reputation = 0
	cases_closed = 0
	cases_failed = 0
	perms = []
	hints_seen = {}
	save_cfg()


func _unhandled_input(e: InputEvent) -> void:
	if e is InputEventKey and e.pressed and not e.echo and e.keycode == KEY_F11:
		toggle_fullscreen()
