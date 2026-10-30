extends Control
## Главное меню: логотип, город в разрезе на фоне, сложность, служба и допуски, управление.

var main: Node
var logo: Texture2D
var t := 0.0
var btns: Array = []           # [Rect2, id]
var panel := "diff"            # diff, service, help
var rng := RandomNumberGenerator.new()
var city_shape: Array = []     # [x, w, h, окна]
var spirit_x := 0.0
var seed_text := ""            # номер дела, набранный в панели «Дело по номеру»

const PAPER := Color(0.88, 0.85, 0.77)
const DIM := Color(0.6, 0.58, 0.53)


func _ready() -> void:
	set_anchors_preset(Control.PRESET_TOP_LEFT)
	size = Vector2(1920, 1080)  # родитель не Control: без размера клики не доходят
	logo = load("res://assets/ui/logo.png")
	rng.seed = 1979
	var x := -40.0
	while x < 2000.0:
		var w := rng.randf_range(120, 260)
		var h := rng.randf_range(220, 520)
		var wins := []
		for r in int(h / 46):
			for c in int(w / 36):
				if rng.randf() < 0.55:
					wins.append([Vector2(x + 14 + c * 36, 1080 - h + 20 + r * 46), rng.randf() < 0.25, rng.randf() * 10.0])
		city_shape.append([x, w, h, wins])
		x += w + rng.randf_range(10, 60)
	Sfx.loop_level("city", 0.25, 1.0)


func _process(dt: float) -> void:
	t += dt
	spirit_x = fmod(t * 40.0, 2200.0) - 100.0
	Sfx.music("evening", dt)
	queue_redraw()


func _f(n: String) -> Font:
	return Res.font(n)


func _draw() -> void:
	draw_rect(Rect2(0, 0, 1920, 1080), K.INK)
	# небо
	for i in 22:
		draw_rect(Rect2(0, i * 50, 1920, 50), Color(0.07 + i * 0.004, 0.07 + i * 0.004, 0.09 + i * 0.005))
	# город сбоку
	for b in city_shape:
		var x: float = b[0]
		var w: float = b[1]
		var h: float = b[2]
		draw_rect(Rect2(x, 1080 - h, w, h), Color(0.06, 0.065, 0.075))
		for wn in b[3]:
			var lit: bool = wn[1] and sin(t * 0.3 + float(wn[2])) > -0.6
			draw_rect(Rect2(wn[0], Vector2(18, 26)), Color(0.85, 0.7, 0.35, 0.75) if lit else Color(0.1, 0.11, 0.13))
	# дух плывёт над крышами
	var sy := 1080.0 - 560.0 + sin(t * 1.3) * 12.0
	for i in 5:
		var a := 0.12 - i * 0.02
		draw_circle(Vector2(spirit_x - i * 14, sy + i * 3), 16.0 - i * 2, Color(0.65, 0.8, 0.95, a))
	draw_texture_rect(logo, Rect2(430, 80, 1060, 220), false, Color(1, 1, 1, 0.92 + 0.08 * sin(t * 2.0)))
	draw_string(_f("Oswald"), Vector2(0, 350), "БЕЗ ЛИЦА · 2.3.1 · ВИД СБОКУ", HORIZONTAL_ALIGNMENT_CENTER, 1920, 30, K.GOLD)
	_buttons()
	_panel()
	draw_string(_f("PT_Sans-Web-Bold"), Vector2(0, 1050), "%s · уровень %d · репутация %d" % [Game.rank(), Game.level, Game.reputation],
		HORIZONTAL_ALIGNMENT_RIGHT, 1880, 22, DIM)


func _button(r: Rect2, label: String, id: String, active := false) -> void:
	var hov := r.has_point(get_local_mouse_position())
	draw_rect(r, Color(K.GOLD, 0.92) if hov else (Color(1, 1, 1, 0.1) if active else Color(0, 0, 0, 0.55)))
	draw_rect(r, Color(K.GOLD, 0.6), false, 2.0)
	draw_string(_f("Oswald"), r.position + Vector2(24, r.size.y * 0.5 + 12), label, HORIZONTAL_ALIGNMENT_LEFT, -1, 32, K.INK if hov else PAPER)
	btns.append([r, id])


func _buttons() -> void:
	btns.clear()
	var items := [["new", "Новое дело"], ["seed", "Дело по номеру"], ["diff", "Сложность: %s" % Game.difficulty], ["service", "Служба и допуски"],
		["help", "Управление"], ["full", "Полный экран"], ["quit", "Выход"]]
	for i in items.size():
		_button(Rect2(160, 430 + i * 84, 520, 66), items[i][1], items[i][0], panel == items[i][0])


func _panel() -> void:
	var r := Rect2(800, 430, 960, 490)
	draw_rect(r, Color(0, 0, 0, 0.6))
	draw_rect(Rect2(r.position, Vector2(6, r.size.y)), K.GOLD)
	var x := r.position.x + 40
	var y := r.position.y + 60
	var body := _f("PT_Sans-Web-Bold")
	match panel:
		"diff":
			draw_string(_f("Oswald"), Vector2(x, y), "СЛОЖНОСТЬ", HORIZONTAL_ALIGNMENT_LEFT, -1, 34, K.GOLD)
			y += 30
			for k in Game.DIFFS:
				var rr := Rect2(x, y, 260, 52)
				var on: bool = Game.difficulty == k
				var hov := rr.has_point(get_local_mouse_position())
				draw_rect(rr, Color(K.GOLD, 0.9) if on else (Color(1, 1, 1, 0.12) if hov else Color(1, 1, 1, 0.04)))
				draw_string(_f("Oswald"), rr.position + Vector2(18, 36), k, HORIZONTAL_ALIGNMENT_LEFT, -1, 28, K.INK if on else PAPER)
				btns.append([rr, "d:" + k])
				x += 290
			x = r.position.x + 40
			y += 100
			draw_multiline_string(body, Vector2(x, y), Game.DIFFS[Game.difficulty]["desc"], HORIZONTAL_ALIGNMENT_LEFT, 880, 28, -1, PAPER)
			y += 140
			draw_multiline_string(body, Vector2(x, y), "Город сбоку: дома в разрезе, этажи, подвалы, коллектор и метро. Ты — дух без лица: вселяйся в людей, найди цель по выцветающим записям, сними её и уйди через звонок таксофона.", HORIZONTAL_ALIGNMENT_LEFT, 880, 24, -1, DIM)
		"service":
			draw_string(_f("Oswald"), Vector2(x, y), "СЛУЖБА", HORIZONTAL_ALIGNMENT_LEFT, -1, 34, K.GOLD)
			y += 46
			draw_string(body, Vector2(x, y), "%s.  Закрыто дел: %d, провалено: %d.  Очков репутации: %d." % [Game.rank().capitalize(), Game.cases_closed, Game.cases_failed, Game.reputation], HORIZONTAL_ALIGNMENT_LEFT, -1, 24, PAPER)
			y += 30
			for k in Game.PERMS:
				var pm: Dictionary = Game.PERMS[k]
				var rr := Rect2(x, y, 880, 58)
				var have := Game.has_perm(k)
				var can := not have and Game.reputation >= int(pm["cost"])
				var hov := rr.has_point(get_local_mouse_position()) and can
				draw_rect(rr, Color(K.GOLD, 0.85) if hov else Color(1, 1, 1, 0.05))
				var c := K.INK if hov else (K.GOLD if have else (PAPER if can else DIM))
				draw_string(_f("Oswald"), rr.position + Vector2(16, 26), pm["name"] + ("  ✓" if have else "  · %d очк." % pm["cost"]), HORIZONTAL_ALIGNMENT_LEFT, -1, 24, c)
				draw_string(body, rr.position + Vector2(16, 50), pm["desc"], HORIZONTAL_ALIGNMENT_LEFT, -1, 19, c)
				if can:
					btns.append([rr, "p:" + k])
				y += 66
			var rs := Rect2(r.end.x - 300, r.end.y - 60, 270, 44)
			var hov2 := rs.has_point(get_local_mouse_position())
			draw_rect(rs, Color(0.8, 0.3, 0.25, 0.9) if hov2 else Color(1, 1, 1, 0.05))
			draw_string(body, rs.position + Vector2(16, 30), "Начать службу заново", HORIZONTAL_ALIGNMENT_LEFT, -1, 20, PAPER)
			btns.append([rs, "reset"])
		"seed":
			draw_string(_f("Oswald"), Vector2(x, y), "ДЕЛО ПО НОМЕРУ", HORIZONTAL_ALIGNMENT_LEFT, -1, 34, K.GOLD)
			y += 30
			draw_multiline_string(body, Vector2(x, y + 20), "Номер дела задаёт район, цель и людей. Тот же номер — тот же город: можно переиграть удачный район или проверить ошибку.", HORIZONTAL_ALIGNMENT_LEFT, 880, 24, -1, DIM)
			y += 110
			var fr := Rect2(x, y, 420, 64)
			draw_rect(fr, Color(1, 1, 1, 0.06))
			draw_rect(fr, Color(K.GOLD, 0.6), false, 2.0)
			var cur := "_" if int(t * 2.0) % 2 == 0 else " "
			draw_string(_f("Oswald"), fr.position + Vector2(20, 46), "№ " + seed_text + cur, HORIZONTAL_ALIGNMENT_LEFT, -1, 36, PAPER)
			var go := Rect2(x + 450, y, 300, 64)
			var hov3 := go.has_point(get_local_mouse_position())
			draw_rect(go, Color(K.GOLD, 0.92) if hov3 else Color(0, 0, 0, 0.55))
			draw_rect(go, Color(K.GOLD, 0.6), false, 2.0)
			draw_string(_f("Oswald"), go.position + Vector2(0, 44), "Начать (Enter)", HORIZONTAL_ALIGNMENT_CENTER, 300, 28, K.INK if hov3 else PAPER)
			btns.append([go, "seed_go"])
			y += 110
			var last := int(Game.last_result.get("seed", 0)) if Game.last_result is Dictionary else 0
			if last > 0:
				var lr := Rect2(x, y, 560, 52)
				var hov4 := lr.has_point(get_local_mouse_position())
				draw_rect(lr, Color(K.GOLD, 0.85) if hov4 else Color(1, 1, 1, 0.05))
				draw_string(_f("Oswald"), lr.position + Vector2(16, 36), "Прошлое дело: №%d" % last, HORIZONTAL_ALIGNMENT_LEFT, -1, 26, K.INK if hov4 else PAPER)
				btns.append([lr, "seed_last"])
			draw_string(body, Vector2(x, r.end.y - 30), "Цифры — набрать номер, Backspace — стереть.", HORIZONTAL_ALIGNMENT_LEFT, -1, 20, DIM)
		"help":
			draw_string(_f("Oswald"), Vector2(x, y), "УПРАВЛЕНИЕ", HORIZONTAL_ALIGNMENT_LEFT, -1, 34, K.GOLD)
			y += 20
			var hl: Array = load("res://src/ui/hud.gd").HELP
			for h in hl:
				y += 32
				if h[1] == "":
					draw_string(_f("Oswald"), Vector2(x, y), h[0], HORIZONTAL_ALIGNMENT_LEFT, -1, 22, K.GOLD)
				else:
					draw_string(_f("Oswald"), Vector2(x, y), h[0], HORIZONTAL_ALIGNMENT_LEFT, -1, 20, PAPER)
					draw_string(body, Vector2(x + 170, y), h[1], HORIZONTAL_ALIGNMENT_LEFT, 720, 19, Color(PAPER, 0.85))


func _gui_input(e: InputEvent) -> void:
	if e is InputEventMouseButton and e.pressed and e.button_index == MOUSE_BUTTON_LEFT:
		for b in btns:
			if (b[0] as Rect2).has_point(e.position):
				_click(b[1])
				return


func _unhandled_input(e: InputEvent) -> void:
	if not (e is InputEventKey and e.pressed and not e.echo):
		return
	var kc: int = e.physical_keycode
	if panel == "seed":
		if kc >= KEY_0 and kc <= KEY_9 and seed_text.length() < 9:
			seed_text += str(kc - KEY_0)
			return
		if kc >= KEY_KP_0 and kc <= KEY_KP_9 and seed_text.length() < 9:
			seed_text += str(kc - KEY_KP_0)
			return
		if kc == KEY_BACKSPACE:
			seed_text = seed_text.substr(0, maxi(0, seed_text.length() - 1))
			return
		if kc in [KEY_ENTER, KEY_KP_ENTER]:
			_click("seed_go")
			return
	if kc in [KEY_ENTER, KEY_SPACE]:
		_click("new")


func _click(id: String) -> void:
	Sfx.play("ui", -6.0)
	if id.begins_with("d:"):
		Game.difficulty = id.substr(2)
		Game.save_cfg()
		return
	if id.begins_with("p:"):
		var k := id.substr(2)
		Game.reputation -= int(Game.PERMS[k]["cost"])
		Game.perms.append(k)
		Game.save_cfg()
		Sfx.play("ui_ok", -4.0)
		return
	match id:
		"new":
			Sfx.loop_level("city", 0.0, 1.0)
			var s := Game.seed_once if Game.seed_once != 0 else randi() % 900000 + 1000
			Game.seed_once = 0
			main.show_brief(s)
		"diff", "service", "help", "seed":
			panel = id
		"seed_go":
			if seed_text.is_valid_int() and int(seed_text) > 0:
				Sfx.loop_level("city", 0.0, 1.0)
				main.show_brief(int(seed_text))
		"seed_last":
			Sfx.loop_level("city", 0.0, 1.0)
			main.show_brief(int(Game.last_result.get("seed", 1000)))
		"full":
			Game.toggle_fullscreen()
		"quit":
			get_tree().quit()
		"reset":
			Game.reset_service()
