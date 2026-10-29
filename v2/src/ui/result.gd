extends Control
## Итог дела: печать, оценка, хвосты, репутация. Дальше — следующее дело или меню.

var main: Node
var res := {}
var t := 0.0
var btns: Array = []
var rep_gain := 0
var lines: Array = []

const PAPER := Color(0.88, 0.85, 0.77)
const DIM := Color(0.6, 0.58, 0.53)
const RED := Color(0.9, 0.38, 0.32)
const HOW := {"hands": "задушен руками исполнителя", "choke": "задушен невидимой рукой", "car": "сбит машиной", "fall": "упал с крыши",
	"pot": "убит упавшим горшком"}


func _ready() -> void:
	set_anchors_preset(Control.PRESET_FULL_RECT)
	var ok: bool = res.get("ok", false)
	if ok:
		rep_gain = {"чисто": 3, "шумно": 2, "грязно": 1}.get(res.get("grade", ""), 1)
		Game.cases_closed += 1
		lines.append("Цель: %s — %s." % [res.get("target", ""), HOW.get(res.get("how", ""), "мертва")])
		var tails: Array = res.get("tails", [])
		if tails.is_empty():
			lines.append("Хвостов нет.")
		else:
			for tl in tails:
				lines.append("Хвост: " + String(tl["text"]))
		if int(res.get("alarms", 0)) > 0:
			lines.append("Тревог поднято: %d." % int(res["alarms"]))
		if int(res.get("extra", 0)) > 0:
			lines.append("Лишних трупов: %d." % int(res["extra"]))
	else:
		rep_gain = 0
		Game.cases_failed += 1
		lines.append(String(res.get("why", "")))
		lines.append("Цель: %s." % res.get("target", ""))
	Game.reputation += rep_gain
	Game.level = 1 + int(Game.cases_closed / 2)
	Game.last_result = res
	Game.save_cfg()
	Sfx.play("stamp", -2.0)


func _process(dt: float) -> void:
	t += dt
	queue_redraw()


func _f(n: String) -> Font:
	return Res.font(n)


func _draw() -> void:
	draw_rect(Rect2(0, 0, 1920, 1080), K.INK)
	var ok: bool = res.get("ok", false)
	var paper := Rect2(460, 80, 1000, 860)
	draw_rect(paper.grow(8), Color(0.3, 0.24, 0.16))
	draw_rect(paper, Color(0.87, 0.83, 0.73))
	var ink := Color(0.16, 0.14, 0.12)
	var x := paper.position.x + 60
	draw_string(_f("Oswald"), Vector2(x, 170), "ДЕЛО №%d · КУРАТОР %s" % [int(res.get("seed", 0)), String(res.get("curator", "")).to_upper()], HORIZONTAL_ALIGNMENT_LEFT, -1, 34, ink)
	draw_string(_f("PT_Sans-Web-Bold"), Vector2(x, 214), "Закрыто в %s." % _hhmm(float(res.get("hour", 0.0))), HORIZONTAL_ALIGNMENT_LEFT, -1, 24, Color(ink, 0.7))
	var y := 290.0
	for ln in lines:
		var h := _f("Caveat").get_multiline_string_size(ln, HORIZONTAL_ALIGNMENT_LEFT, 880, 36).y
		draw_multiline_string(_f("Caveat"), Vector2(x, y), ln, HORIZONTAL_ALIGNMENT_LEFT, 880, 36, -1, Color(0.12, 0.12, 0.3))
		y += h + 12
	# печать
	var a := clampf(t / 0.35, 0.0, 1.0)
	var col := Color(0.15, 0.4, 0.2) if ok else Color(0.7, 0.18, 0.14)
	var stamp: String = ("ЗАКРЫТО · " + String(res.get("grade", "")).to_upper()) if ok else "ПРОВАЛ"
	draw_set_transform(Vector2(1180, 760), -0.18, Vector2.ONE * lerpf(2.0, 1.0, a))
	draw_rect(Rect2(-260, -60, 520, 110), Color(col, 0.85 * a), false, 6.0)
	draw_string(_f("Oswald"), Vector2(-260, 18), stamp, HORIZONTAL_ALIGNMENT_CENTER, 520, 44, Color(col, 0.85 * a))
	draw_set_transform(Vector2.ZERO, 0.0, Vector2.ONE)
	draw_string(_f("PT_Sans-Web-Bold"), Vector2(x, 880), "Репутация +%d → %d.  %s, уровень %d." % [rep_gain, Game.reputation, Game.rank().capitalize(), Game.level],
		HORIZONTAL_ALIGNMENT_LEFT, -1, 24, ink)
	btns.clear()
	_button(Rect2(460, 970, 480, 70), "Следующее дело", "next")
	_button(Rect2(980, 970, 480, 70), "В меню (допуски — в «Службе»)", "menu")


func _hhmm(h: float) -> String:
	var hh := int(h)
	return "%d:%02d" % [hh % 24, int((h - hh) * 60.0)]


func _button(r: Rect2, label: String, id: String) -> void:
	var hov := r.has_point(get_local_mouse_position())
	draw_rect(r, Color(K.GOLD, 0.92) if hov else Color(0, 0, 0, 0.55))
	draw_rect(r, Color(K.GOLD, 0.6), false, 2.0)
	draw_string(_f("Oswald"), r.position + Vector2(0, 48), label, HORIZONTAL_ALIGNMENT_CENTER, r.size.x, 30, K.INK if hov else PAPER)
	btns.append([r, id])


func _gui_input(e: InputEvent) -> void:
	if e is InputEventMouseButton and e.pressed and e.button_index == MOUSE_BUTTON_LEFT and t > 0.6:
		for b in btns:
			if (b[0] as Rect2).has_point(e.position):
				_click(b[1])


func _unhandled_input(e: InputEvent) -> void:
	if t > 0.6 and e is InputEventKey and e.pressed and not e.echo:
		if e.physical_keycode in [KEY_ENTER, KEY_SPACE]:
			_click("next")
		elif e.physical_keycode == KEY_ESCAPE:
			_click("menu")


func _click(id: String) -> void:
	Sfx.play("ui", -6.0)
	if id == "next":
		main.show_brief(randi() % 900000 + 1000)
	else:
		main.show_menu()
