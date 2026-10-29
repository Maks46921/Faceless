extends CanvasLayer
## Интерфейс дела: часы, память, плотность или подозрение, подсказки клавиш, реплики над головами,
## голоса (куратор, память, чутьё), карточки записей, полоса района, доска (Tab), карта (M), пауза (Esc).

var world: Node
var d: Control
var voices: Array = []          # {who, text, col, t}
var toasts: Array = []          # {card, src, extra, t}
var board := false
var map := false
var pause := false
var help := false
var brief := false
var brief_btn := Rect2()
var end := {}
var end_t := 0.0
var t := 0.0
var pause_btns: Array = []
var board_rects: Array = []     # [Rect2, card]
var hint_t := 2.0

const F_HEAD := "Oswald"
const F_BODY := "PT_Sans-Web-Bold"
const F_HAND := "Caveat"
const F_MONO := "PTM55FT"
const PAPER := Color(0.88, 0.85, 0.77)
const DIM := Color(0.62, 0.6, 0.55)
const RED := Color(0.9, 0.38, 0.32)
const BG := Color(0.067, 0.071, 0.078, 0.82)


func _ready() -> void:
	layer = 5
	process_mode = Node.PROCESS_MODE_ALWAYS
	d = Control.new()
	d.set_anchors_preset(Control.PRESET_FULL_RECT)
	d.mouse_filter = Control.MOUSE_FILTER_IGNORE
	d.draw.connect(_draw_all)
	add_child(d)


func modal() -> bool:
	return board or map or pause or help or brief


func open_brief() -> void:
	brief = true
	get_tree().paused = true


func _close_brief() -> void:
	brief = false
	get_tree().paused = false
	Sfx.play("ui_ok", -4.0)


func _process(dt: float) -> void:
	t += dt
	for v in voices:
		v["t"] = float(v["t"]) - dt
	voices = voices.filter(func(v): return float(v["t"]) > 0.0)
	for c in toasts:
		c["t"] = float(c["t"]) - dt
	toasts = toasts.filter(func(c): return float(c["t"]) > 0.0)
	if not end.is_empty():
		end_t += dt
	hint_t -= dt
	if hint_t <= 0.0:
		hint_t = 1.0
		_hints()
	d.queue_redraw()


func _hints() -> void:
	if world.over:
		return
	var pl: PlayerCtl = world.player
	if world.t_total > 3.0 and Game.hint_once("start"):
		voice("КУРАТОР", "%s Ты в чужом теле. Найди цель по записям — Tab. Карта — M. Время не ждёт." % world.case.curator["line"], K.GOLD, 9.0)
	elif pl.host == null and Game.hint_once("spirit"):
		voice("ПАМЯТЬ", "Без тела я таю. Солнце и фонари жгут, собаки рвут. Клешни — 1…5 и ЛКМ. F — войти в тело.", K.GOLD, 9.0)
	elif world.case.open_tails().size() > 0 and Game.hint_once("tails"):
		voice("КУРАТОР", "Хвосты подчисти до звонка: тело, камеры, свидетели. Список — на доске.", K.GOLD, 8.0)


# ======================= API для мира =======================

func voice(who: String, text: String, col: Color = PAPER, dur: float = 6.5) -> void:
	for v in voices:
		if v["text"] == text:
			v["t"] = dur
			return
	voices.append({"who": who, "text": text, "col": col, "t": dur})
	if voices.size() > 4:
		voices.pop_front()


func card_toast(c: Dictionary, src: String, extra: String = "") -> void:
	if c.is_empty():
		return
	toasts.append({"card": c, "src": src, "extra": extra, "t": 7.0})
	if toasts.size() > 2:
		toasts.pop_front()
	Sfx.play("memory", -8.0)


func body_changed() -> void:
	pass


func end_flash(res: Dictionary) -> void:
	end = res
	end_t = 0.0
	board = false
	map = false
	pause = false
	Sfx.play("stamp", 0.0)


func toggle_pause() -> void:
	if board or map or help:
		board = false
		map = false
		help = false
		return
	pause = not pause
	world.paused = pause
	get_tree().paused = pause


# ======================= ввод =======================

func _input(e: InputEvent) -> void:
	if world == null or world.over:
		return
	if brief:
		if e is InputEventKey and e.pressed and not e.echo and e.physical_keycode in [KEY_ENTER, KEY_SPACE, KEY_KP_ENTER]:
			_close_brief()
			get_viewport().set_input_as_handled()
		elif e is InputEventMouseButton and e.pressed and brief_btn.has_point(d.get_local_mouse_position()):
			_close_brief()
			get_viewport().set_input_as_handled()
		return
	if e is InputEventKey and e.pressed and not e.echo:
		match e.physical_keycode:
			KEY_ESCAPE:
				toggle_pause()
				get_viewport().set_input_as_handled()
			KEY_TAB:
				if not pause:
					board = not board
					map = false
					get_viewport().set_input_as_handled()
			KEY_M:
				if not pause:
					map = not map
					board = false
					get_viewport().set_input_as_handled()
			KEY_F1:
				help = not help
				get_viewport().set_input_as_handled()
	if e is InputEventMouseButton and e.pressed and e.button_index == MOUSE_BUTTON_LEFT:
		var mp: Vector2 = d.get_local_mouse_position()
		if board:
			for r in board_rects:
				if (r[0] as Rect2).has_point(mp):
					_pin(r[1])
					get_viewport().set_input_as_handled()
					return
		if pause:
			for b in pause_btns:
				if (b[0] as Rect2).has_point(mp):
					_pause_btn(b[1])
					get_viewport().set_input_as_handled()
					return


func _pin(c: Dictionary) -> void:
	var cs: Case = world.case
	if c["pinned"]:
		c["pinned"] = false
		cs.pins_left += 1
		Sfx.play("ui", -6.0)
	elif cs.pins_left > 0:
		c["pinned"] = true
		cs.pins_left -= 1
		Sfx.play("ui_ok", -6.0)


func _pause_btn(id: String) -> void:
	match id:
		"resume":
			toggle_pause()
		"help":
			help = true
			pause = false
			world.paused = false
			get_tree().paused = false
		"full":
			Game.toggle_fullscreen()
		"quit":
			world.paused = false
			pause = false
			get_tree().paused = false
			world.fail("Ты бросил дело.")


# ======================= рисование =======================

func _font(n: String) -> Font:
	return Res.font(n)


func _aligned(pos: Vector2, s: String, fnt: String, size: int, align: int, w: float) -> Vector2:
	## Выравнивание по точке, если ширина не задана (Godot выравнивает только внутри ширины).
	if align == HORIZONTAL_ALIGNMENT_LEFT or w > 0.0:
		return pos
	var sw := _font(fnt).get_string_size(s, HORIZONTAL_ALIGNMENT_LEFT, -1, size).x
	if align == HORIZONTAL_ALIGNMENT_RIGHT:
		return pos - Vector2(sw, 0)
	return pos - Vector2(sw / 2.0, 0)


func _text(pos: Vector2, s: String, fnt: String, size: int, col: Color, align := HORIZONTAL_ALIGNMENT_LEFT, w := -1.0) -> void:
	var p := _aligned(pos, s, fnt, size, align, w)
	d.draw_string(_font(fnt), p, s, align if w > 0.0 else HORIZONTAL_ALIGNMENT_LEFT, w if w > 0.0 else -1.0, size, col)


func _shadow_text(pos: Vector2, s: String, fnt: String, size: int, col: Color, align := HORIZONTAL_ALIGNMENT_LEFT, w := -1.0) -> void:
	var p := _aligned(pos, s, fnt, size, align, w)
	var a: int = align if w > 0.0 else HORIZONTAL_ALIGNMENT_LEFT
	var ww := w if w > 0.0 else -1.0
	d.draw_string_outline(_font(fnt), p, s, a, ww, size, 6, Color(0, 0, 0, 0.75 * col.a))
	d.draw_string(_font(fnt), p, s, a, ww, size, col)


func _wrap(pos: Vector2, s: String, fnt: String, size: int, col: Color, w: float, outline := false) -> float:
	## Многострочный текст; возвращает высоту.
	var f := _font(fnt)
	var h := f.get_multiline_string_size(s, HORIZONTAL_ALIGNMENT_LEFT, w, size).y
	if outline:
		d.draw_multiline_string_outline(f, pos, s, HORIZONTAL_ALIGNMENT_LEFT, w, size, -1, 6, Color(0, 0, 0, 0.7 * col.a))
	d.draw_multiline_string(f, pos, s, HORIZONTAL_ALIGNMENT_LEFT, w, size, -1, col)
	return h


func _bar(r: Rect2, k: float, col: Color, label: String, val: String) -> void:
	d.draw_rect(r, Color(0, 0, 0, 0.55))
	d.draw_rect(Rect2(r.position, Vector2(r.size.x * clampf(k, 0.0, 1.0), r.size.y)), col)
	d.draw_rect(r, Color(col, 0.6), false, 2.0)
	_shadow_text(r.position + Vector2(0, -8), label, F_HEAD, 22, Color(PAPER, 0.85))
	_shadow_text(r.position + Vector2(r.size.x, -8), val, F_MONO, 22, Color(PAPER, 0.85), HORIZONTAL_ALIGNMENT_RIGHT, 0)


func _draw_all() -> void:
	if world == null or world.player == null:
		return
	if not end.is_empty():
		_draw_end()
		return
	_bubbles()
	_hover()
	_top_left()
	_minimap()
	_bottom()
	_voices()
	_toasts()
	if board:
		_board()
	if map:
		_map()
	if pause:
		_pause()
	if help:
		_help()
	if brief:
		_brief()


func _top_left() -> void:
	var env: Env = world.env
	var cs: Case = world.case
	var pl: PlayerCtl = world.player
	var x := 40.0
	d.draw_rect(Rect2(20, 18, 470, 214), BG)
	d.draw_rect(Rect2(20, 18, 6, 214), K.GOLD)
	_text(Vector2(x, 72), cs.hhmm(env.hour), F_MONO, 48, PAPER)
	var w := {"clear": "ясно", "cloudy": "пасмурно", "rain": "дождь", "fog": "туман"}
	var info: String = w.get(env.weather, "")
	if env.speed > 1.0:
		info += "   ×%d ⏩" % int(env.speed)
	_text(Vector2(x + 150, 70), info, F_BODY, 22, DIM)
	var tline := "Цель: найти и снять."
	if cs.target_dead:
		tline = "Цель снята. Ждать звонка." if world.exit_ring.is_empty() else "Таксофон %s, %s." % [world.exit_ring["phone"]["name"], cs.hhmm(world.exit_ring["h0"])]
	_text(Vector2(x, 104), tline, F_BODY, 22, K.GOLD if cs.target_dead else PAPER)
	var mem := cs.memory()
	var mc := K.GOLD if mem > 45.0 else (Color(0.9, 0.62, 0.3) if mem > 25.0 else RED)
	_bar(Rect2(x, 150, 420, 14), mem / 100.0, mc, "ПАМЯТЬ", "%d" % int(mem))
	if pl.host:
		var s: float = world.susp
		var sc := Color(0.75, 0.72, 0.66) if s < 40.0 else (Color(0.95, 0.6, 0.3) if s < 75.0 else RED)
		var why: String = world.susp_why if world.susp_why != "" and s > 1.0 else ""
		_bar(Rect2(x, 206, 420, 14), s / 100.0, sc, "ПОДОЗРЕНИЕ" + ("  · " + why if why != "" else ""), "%d" % int(s))
	else:
		var dn := pl.density
		var dc := Color(0.6, 0.78, 0.95) if dn > 35.0 else RED
		var hw := ("  · жжёт: " + pl.hurt_why) if pl.hurt_why != "" else ""
		_bar(Rect2(x, 206, 420, 14), dn / 100.0, dc, "ПЛОТНОСТЬ" + hw, "%d" % int(dn))
	# хвосты
	var tails := cs.open_tails()
	var y := 262.0
	if tails.size() > 0:
		d.draw_rect(Rect2(20, 240, 470, 32 + tails.size() * 30), BG)
		_text(Vector2(x, y), "ХВОСТЫ", F_HEAD, 20, RED)
		y += 28
		for tl in tails:
			_text(Vector2(x, y), "· " + _short(tl["text"], 46), F_BODY, 19, PAPER)
			y += 30
	# свидетели
	for wt in world.witnesses:
		if wt["done"]:
			continue
		var p: Person = wt["who"]
		if not p.visible:
			continue
		var sp: Vector2 = world.view.world_to_screen(p.head_pos() + Vector2(0, -14))
		if _onscreen(sp):
			_shadow_text(sp + Vector2(0, -6), "! %d" % int(ceil(float(wt["t"]))), F_HEAD, 30, RED, HORIZONTAL_ALIGNMENT_CENTER, 0)


func _short(s: String, n: int) -> String:
	return s if s.length() <= n else s.substr(0, n - 1) + "…"


func _onscreen(p: Vector2) -> bool:
	return p.x > -40 and p.x < 1960 and p.y > -40 and p.y < 1120


func _bubbles() -> void:
	var pl: PlayerCtl = world.player
	var fp := pl.focus_pos()
	var fin := pl.focus_inside()
	for p in world.people:
		if p.bubble == "" or not p.visible or p.state == "gone":
			continue
		if absf(p.global_position.x - fp.x) > 420.0:
			continue
		if p.inside and not fin and pl.host and world.view.viewer_bid != p.bid():
			# изнутри дома снаружи не слышно, а снаружи внутрь — только рядом
			if p.global_position.distance_to(fp) > 150.0:
				continue
		var sp: Vector2 = world.view.world_to_screen(p.head_pos() + Vector2(0, -6))
		if not _onscreen(sp):
			continue
		var f := _font(F_BODY)
		var sz := f.get_multiline_string_size(p.bubble, HORIZONTAL_ALIGNMENT_LEFT, 380, 22)
		var r := Rect2(sp.x - sz.x / 2 - 12, sp.y - sz.y - 22, sz.x + 24, sz.y + 12)
		d.draw_rect(r, Color(0.07, 0.07, 0.08, 0.86))
		d.draw_rect(r, Color(p.bubble_col, 0.5), false, 2.0)
		var tri := PackedVector2Array([Vector2(sp.x - 8, r.end.y), Vector2(sp.x + 8, r.end.y), Vector2(sp.x, r.end.y + 10)])
		d.draw_colored_polygon(tri, Color(0.07, 0.07, 0.08, 0.86))
		d.draw_multiline_string(f, r.position + Vector2(12, 26), p.bubble, HORIZONTAL_ALIGNMENT_LEFT, 380, 22, -1, p.bubble_col)
	if pl.msg_t > 0.0:
		var hp: Vector2 = world.view.world_to_screen(pl.focus_pos() + Vector2(0, -60 if pl.host else -36))
		_shadow_text(hp, pl.msg, F_HAND, 34, Color(0.95, 0.9, 0.75, minf(1.0, pl.msg_t)), HORIZONTAL_ALIGNMENT_CENTER, 0)


func _hover() -> void:
	var pl: PlayerCtl = world.player
	if pl.host:
		var mark := _mark_person()
		if mark:
			var mp: Vector2 = world.view.world_to_screen(mark.head_pos() + Vector2(0, -20))
			_shadow_text(mp, "▼", F_BODY, 22, Color(K.GOLD, 0.7), HORIZONTAL_ALIGNMENT_CENTER, 0)
		return
	if pl.hover:
		var q := pl.hover
		var sp: Vector2 = world.view.world_to_screen(q.head_pos() + Vector2(0, -10))
		var who := pl._who_word(q)
		var col := RED if q == world.case.target else K.GOLD
		_shadow_text(sp, who, F_HEAD, 26, col, HORIZONTAL_ALIGNMENT_CENTER, 0)
		var r := 18.0 * 3.0
		d.draw_arc(world.view.world_to_screen(q.center()), r, 0, TAU, 32, Color(col, 0.6), 2.0)
	if pl.claw >= 0:
		var mp2: Vector2 = d.get_local_mouse_position()
		var sc: Vector2 = world.view.world_to_screen(pl.spirit.center())
		var reach := PlayerCtl.REACH * 3.0
		d.draw_arc(sc, reach, 0, TAU, 64, Color(0.6, 0.78, 0.95, 0.25), 2.0)
		var hc: Dictionary = pl.hover_claw
		if not hc.is_empty():
			var col2 := Color(0.6, 0.85, 1.0) if hc["ok"] else Color(0.6, 0.6, 0.6)
			_shadow_text(mp2 + Vector2(22, -14), hc["text"] + ("" if hc["ok"] else " — далеко"), F_BODY, 22, col2)


func _mark_person() -> Person:
	## Подсветка того, с кем можно говорить или кого душить.
	var pl: PlayerCtl = world.player
	if pl.act_q.has("who"):
		return pl.act_q["who"]
	if pl.act_e.has("who"):
		return pl.act_e["who"]
	return null


func _bottom() -> void:
	var pl: PlayerCtl = world.player
	# подсказки клавиш
	var items: Array = pl.prompts
	var x := 960.0
	var total := 0.0
	var f := _font(F_BODY)
	var widths := []
	for it in items:
		var wd := f.get_string_size(it[1], HORIZONTAL_ALIGNMENT_LEFT, -1, 22).x + 18 + _keyw(it[0])
		widths.append(wd)
		total += wd + 18
	x -= total / 2.0
	var y := 1030.0
	for i in items.size():
		var it: Array = items[i]
		var kw := _keyw(it[0])
		d.draw_rect(Rect2(x, y - 24, kw, 32), Color(K.GOLD, 0.9))
		_text(Vector2(x, y), it[0], F_HEAD, 22, K.INK, HORIZONTAL_ALIGNMENT_CENTER, kw)
		_shadow_text(Vector2(x + kw + 8, y), it[1], F_BODY, 22, PAPER)
		x += float(widths[i]) + 18
	# тело
	if pl.host:
		var p := pl.host
		d.draw_rect(Rect2(20, 940, 420, 110), BG)
		_text(Vector2(40, 980), p.full_name(), F_HEAD, 28, PAPER)
		var line := pl._who_word(p)
		if p.keys.size() > 0:
			line += "  ·  ключей: %d" % p.keys.size()
		if p.carrying:
			line += "  ·  несёт тело"
		_text(Vector2(40, 1016), line, F_BODY, 20, DIM)
		if pl.emergency_t > 0.0:
			_bar(Rect2(40, 1030, 380, 8), pl.emergency_t / 1.6, RED, "", "")
		if not pl.strangle.is_empty():
			var v: Person = pl.strangle["victim"]
			var sp: Vector2 = world.view.world_to_screen(v.head_pos() + Vector2(0, -24))
			var k := float(pl.strangle["t"]) / float(pl.strangle["need"])
			d.draw_rect(Rect2(sp.x - 60, sp.y, 120, 10), Color(0, 0, 0, 0.6))
			d.draw_rect(Rect2(sp.x - 60, sp.y, 120 * k, 10), RED)
	else:
		_claws()


func _keyw(k: String) -> float:
	return maxf(32.0, _font(F_HEAD).get_string_size(k, HORIZONTAL_ALIGNMENT_LEFT, -1, 22).x + 14)


func _claws() -> void:
	var pl: PlayerCtl = world.player
	var x := 1920.0 - 20 - 5 * 150
	var y := 900.0
	d.draw_rect(Rect2(x - 10, y - 40, 5 * 150 + 10, 120), BG)
	_text(Vector2(x, y - 12), "КЛЕШНИ", F_HEAD, 20, DIM)
	for i in PlayerCtl.CLAWS.size():
		var c: Dictionary = PlayerCtl.CLAWS[i]
		var r := Rect2(x + i * 150, y, 140, 64)
		var sel := pl.claw == i
		d.draw_rect(r, Color(0.6, 0.78, 0.95, 0.25) if sel else Color(1, 1, 1, 0.05))
		d.draw_rect(r, Color(0.6, 0.78, 0.95) if sel else Color(1, 1, 1, 0.15), false, 2.0)
		_text(r.position + Vector2(8, 26), "%d  %s" % [i + 1, c["name"]], F_HEAD, 20, PAPER)
		_text(r.position + Vector2(8, 54), "−%.0f памяти" % pl._claw_cost(i), F_BODY, 18, DIM)
	if pl.claw >= 0:
		_text(Vector2(x, y + 100), PlayerCtl.CLAWS[pl.claw]["hint"], F_BODY, 19, Color(0.6, 0.78, 0.95))
	if not pl.spirit.held.is_empty():
		_text(Vector2(x, y - 52), "В клешне: " + String(pl.spirit.held.get("name", "")), F_BODY, 20, K.GOLD)


func _voices() -> void:
	var y: float = 330.0 + world.case.open_tails().size() * 30.0 + (40.0 if world.case.open_tails().size() > 0 else 0.0)
	for v in voices:
		var a := clampf(float(v["t"]), 0.0, 1.0)
		var col: Color = v["col"]
		_shadow_text(Vector2(40, y), v["who"], F_HEAD, 20, Color(col, a))
		var h := _wrap(Vector2(40, y + 30), v["text"], F_BODY, 24, Color(PAPER, a), 640, true)
		y += h + 46


func _toasts() -> void:
	var y := 300.0
	var cs: Case = world.case
	for tt in toasts:
		var c: Dictionary = tt["card"]
		var a := clampf(float(tt["t"]), 0.0, 1.0)
		var r := Rect2(1380, y, 500, 10)
		var body := cs.text(c)
		if tt["extra"] != "" and tt["extra"] != body:
			body = tt["extra"] + "\n— " + body
		var f := _font(F_HAND)
		var h := f.get_multiline_string_size(body, HORIZONTAL_ALIGNMENT_LEFT, 460, 30).y
		r.size.y = h + 70
		d.draw_rect(r, Color(0.86, 0.82, 0.72, 0.95 * a))
		d.draw_rect(Rect2(r.position, Vector2(r.size.x, 6)), Color(K.GOLD, a))
		_text(r.position + Vector2(20, 38), "%s · %s" % [c["title"], tt["src"]], F_HEAD, 22, Color(0.2, 0.18, 0.16, a))
		d.draw_multiline_string(f, r.position + Vector2(20, 72), body, HORIZONTAL_ALIGNMENT_LEFT, 460, 30, -1, Color(0.15, 0.14, 0.2, a))
		y += r.size.y + 16


# ======================= полоса района =======================

func _minimap() -> void:
	var city: City = world.city
	var pl: PlayerCtl = world.player
	var wpx := float(city.width * K.T)
	var r := Rect2(1300, 22, 600, 96)
	d.draw_rect(r.grow(8), BG)
	var sx := r.size.x / wpx
	var gy := r.position.y + 70
	d.draw_line(Vector2(r.position.x, gy), Vector2(r.end.x, gy), Color(PAPER, 0.4), 2.0)
	for b in city.buildings:
		var x0 := r.position.x + float(b["px0"]) * sx
		var bw := (float(b["px1"]) - float(b["px0"])) * sx
		var h := float(b["n"]) * 7.0
		var near: bool = int(b["id"]) == int(city.building_at(pl.focus_pos().x).get("id", -1))
		d.draw_rect(Rect2(x0, gy - h, bw, h), Color(0.3, 0.3, 0.32, 0.9) if not near else Color(0.42, 0.4, 0.36, 0.95))
	# таксофоны
	for o in city.objs:
		if o["kind"] == "payphone":
			var ox := r.position.x + float(o["x"]) * sx
			var ring: bool = o["ring"]
			d.draw_rect(Rect2(ox - 2, gy - 8, 4, 8), K.GOLD if ring and int(t * 4) % 2 == 0 else Color(0.5, 0.55, 0.5))
	# милиция
	if world.police_state == "here":
		var px: float = r.position.x + world.police_target.x * sx
		d.draw_rect(Rect2(px - 4, gy + 4, 8, 6), Color(0.4, 0.5, 1.0) if int(t * 4) % 2 == 0 else RED)
	# игрок
	var fp := pl.focus_pos()
	var yy := gy - clampf((K.floor_y(0) - fp.y) / 80.0 * 7.0, -18.0, 80.0)
	var mx := r.position.x + fp.x * sx
	d.draw_circle(Vector2(mx, yy - 3), 5.0, K.GOLD if pl.host else Color(0.6, 0.78, 0.95))
	_text(Vector2(r.position.x, r.end.y + 4), _place_name(fp, pl.focus_area()), F_BODY, 20, DIM)


func _place_name(fp: Vector2, area: String) -> String:
	var city: City = world.city
	if area == "C":
		return "коллектор"
	if area == "M":
		return "метро, платформа"
	if area.begins_with("R"):
		return "крыша"
	if city.areas.has(area) and city.areas[area]["inside"]:
		var b: Dictionary = city.buildings[int(city.areas[area]["bid"])]
		var f := int(city.areas[area]["f"])
		var nm: String = b["name"] if b["name"] != "" else "жилой дом"
		return "%s, %s" % [nm, "подвал" if f < 0 else "%d-й этаж" % (f + 1)]
	var best := ""
	var bd := 220.0
	for k in city.places:
		var pl: Dictionary = city.places[k]
		if pl["area"] == "S" and absf(float(pl["x"]) - fp.x) < bd:
			bd = absf(float(pl["x"]) - fp.x)
			best = k
	return "улица" + (" · " + best if best != "" else "")


# ======================= доска =======================

func _board() -> void:
	var cs: Case = world.case
	d.draw_rect(Rect2(0, 0, 1920, 1080), Color(0.05, 0.05, 0.06, 0.9))
	d.draw_rect(Rect2(60, 50, 1800, 980), Color(0.33, 0.25, 0.18))
	d.draw_rect(Rect2(60, 50, 1800, 980), Color(0.2, 0.15, 0.1), false, 8.0)
	_text(Vector2(100, 112), "ДЕЛО №%d · %s" % [world.case_seed, cs.curator["name"]], F_HEAD, 40, PAPER)
	_text(Vector2(1820, 112), "булавок: %d · звонков: %d · Tab — закрыть" % [cs.pins_left, cs.calls_left], F_BODY, 22, PAPER, HORIZONTAL_ALIGNMENT_RIGHT, 0)
	board_rects.clear()
	var x := 100.0
	var y := 150.0
	var col := 0
	var known := cs.cards.filter(func(c): return c["known"])
	for c in known:
		var r := Rect2(x + col * 440, y, 420, 250)
		var st := cs.stage(c)
		var paper := Color(0.88, 0.85, 0.77) if c["own"] else Color(0.75, 0.82, 0.86)
		var rot := 0.0
		d.draw_set_transform(r.position + r.size / 2, rot, Vector2.ONE)
		var rr := Rect2(-r.size / 2, r.size)
		d.draw_rect(rr, paper)
		d.draw_rect(rr, Color(0, 0, 0, 0.25), false, 2.0)
		_text(rr.position + Vector2(18, 40), c["title"].to_upper(), F_HEAD, 26, Color(0.18, 0.16, 0.14))
		var stw := {"clear": "ясно", "haze": "мутно", "dist": "искажено?", "empty": "пусто"}
		var stc := {"clear": Color(0.2, 0.45, 0.25), "haze": Color(0.55, 0.45, 0.15), "dist": Color(0.65, 0.25, 0.2), "empty": Color(0.4, 0.4, 0.4)}
		_text(rr.position + Vector2(rr.size.x - 18, 40), stw[st], F_BODY, 20, stc[st], HORIZONTAL_ALIGNMENT_RIGHT, 0)
		var ink := Color(0.12, 0.12, 0.25, 0.4 + 0.6 * clampf(float(c["clar"]) / 100.0, 0.0, 1.0))
		d.draw_multiline_string(_font(F_HAND), rr.position + Vector2(18, 84), cs.text(c), HORIZONTAL_ALIGNMENT_LEFT, 384, 30, 5, ink)
		var pl := cs.cur_place(c)
		if pl != "" and c["hours"].size() > 0:
			_text(rr.position + Vector2(18, 226), "→ %s, %s" % [pl, cs.hhmm(float(c["hours"][0]))], F_BODY, 18, Color(0.3, 0.25, 0.2))
		elif c["src"] != "":
			_text(rr.position + Vector2(18, 226), String(c["src"]), F_BODY, 18, Color(0.4, 0.35, 0.3))
		# ясность
		d.draw_rect(Rect2(rr.position + Vector2(0, rr.size.y - 6), Vector2(rr.size.x * float(c["clar"]) / 100.0, 6)), stc[st])
		if c["pinned"]:
			d.draw_circle(rr.position + Vector2(rr.size.x / 2, 8), 11, Color(0.75, 0.15, 0.12))
			d.draw_circle(rr.position + Vector2(rr.size.x / 2 - 3, 5), 3, Color(1, 0.6, 0.6))
		d.draw_set_transform(Vector2.ZERO, 0.0, Vector2.ONE)
		if c["own"]:
			board_rects.append([r, c])
		col += 1
		if col >= 4:
			col = 0
			y += 270
	if known.is_empty():
		_text(Vector2(100, 220), "Пусто. Куратор ничего не сказал — придётся узнать самому.", F_HAND, 34, PAPER)
	var unk := cs.cards.filter(func(c): return not c["known"] and c["own"]).size()
	_text(Vector2(100, 1000), "Неизвестно ещё: %d.  Клик по записи — булавка: тает втрое медленнее.  Узнавать: говорить с людьми (E), улики дома у цели, подслушивать." % unk, F_BODY, 22, Color(PAPER, 0.8))
	# хвосты справа внизу
	var tails := cs.open_tails()
	if tails.size() > 0:
		var ty := 1000.0 - tails.size() * 30 - 30
		_text(Vector2(1820, ty), "ХВОСТЫ", F_HEAD, 24, RED, HORIZONTAL_ALIGNMENT_RIGHT, 0)
		for tl in tails:
			ty += 30
			_text(Vector2(1820, ty), tl["text"], F_BODY, 20, PAPER, HORIZONTAL_ALIGNMENT_RIGHT, 0)


# ======================= карта =======================

func _map() -> void:
	var city: City = world.city
	var cs: Case = world.case
	var pl: PlayerCtl = world.player
	d.draw_rect(Rect2(0, 0, 1920, 1080), Color(0.05, 0.05, 0.06, 0.92))
	_text(Vector2(60, 90), "РАЙОН · разрез", F_HEAD, 40, PAPER)
	_text(Vector2(1860, 90), "M — закрыть", F_BODY, 22, DIM, HORIZONTAL_ALIGNMENT_RIGHT, 0)
	var wpx := float(city.width * K.T)
	var sx := 1800.0 / wpx
	var top := float((K.GY - 62) * K.T)
	var bot := float(K.ROWS * K.T)
	var sy := 860.0 / (bot - top)
	var o := Vector2(60, 140)
	var tr := func(p: Vector2) -> Vector2: return o + Vector2(p.x * sx, (p.y - top) * sy)
	# земля
	var g0: Vector2 = tr.call(Vector2(0, K.floor_y(0)))
	d.draw_rect(Rect2(g0, Vector2(1800, 860 - (g0.y - o.y))), Color(0.12, 0.11, 0.1))
	for id in city.areas:
		var a: Dictionary = city.areas[id]
		var p0: Vector2 = tr.call(Vector2(float(a["x0"]), float(a["y"]) - 64.0))
		var p1: Vector2 = tr.call(Vector2(float(a["x1"]), float(a["y"])))
		if id == "S":
			continue
		var c := Color(0.25, 0.25, 0.27) if a["inside"] else Color(0.18, 0.18, 0.2)
		if id == pl.focus_area():
			c = Color(0.42, 0.38, 0.3)
		d.draw_rect(Rect2(p0, p1 - p0), c)
		d.draw_rect(Rect2(p0, p1 - p0), Color(0, 0, 0, 0.5), false, 1.0)
	for b in city.buildings:
		var bp: Vector2 = tr.call(Vector2(float(b["px0"]), float(int(b["roof_r"]) * K.T)))
		var nm: String = b["name"] if b["name"] != "" else ("жилой" if b["kind"] == "res" else "")
		_text(bp + Vector2(4, -6), nm, F_BODY, 18, DIM)
	# места
	for k in city.places:
		var plc: Dictionary = city.places[k]
		if not city.areas.has(plc["area"]):
			continue
		var y := float(city.areas[plc["area"]]["y"])
		var mp: Vector2 = tr.call(Vector2(float(plc["x"]), y))
		d.draw_circle(mp + Vector2(0, -4), 4, Color(PAPER, 0.6))
		_text(mp + Vector2(6, 18), k, F_BODY, 16, Color(PAPER, 0.7))
	# куда ведут записи
	for c in cs.cards:
		if not c["known"]:
			continue
		var pk := cs.cur_place(c)
		var plc2 := cs.place(pk) if pk != "" else {}
		if plc2.is_empty() or not city.areas.has(plc2.get("area", "")):
			continue
		var mp2: Vector2 = tr.call(Vector2(float(plc2["x"]), float(city.areas[plc2["area"]]["y"])))
		var st := cs.stage(c)
		var col := K.GOLD if st == "clear" else (Color(0.8, 0.65, 0.3) if st == "haze" else Color(0.75, 0.4, 0.35))
		d.draw_circle(mp2 + Vector2(0, -14), 9, col)
		var hr: String = cs.hhmm(float(c["hours"][0])) if c["hours"].size() > 0 else ""
		_shadow_text(mp2 + Vector2(12, -24), "%s %s" % [c["title"], hr], F_HEAD, 20, col)
	# таксофоны
	for ob in city.objs:
		if ob["kind"] == "payphone":
			var pp: Vector2 = tr.call(Vector2(float(ob["x"]), float(ob["y"])))
			d.draw_rect(Rect2(pp - Vector2(4, 16), Vector2(8, 16)), K.GOLD if ob["ring"] else Color(0.45, 0.6, 0.45))
	# игрок
	var fp: Vector2 = tr.call(pl.focus_pos())
	d.draw_circle(fp + Vector2(0, -6), 8, K.GOLD if pl.host else Color(0.6, 0.78, 0.95))
	_shadow_text(fp + Vector2(0, -20), "ты", F_HEAD, 22, PAPER, HORIZONTAL_ALIGNMENT_CENTER, 0)
	_text(Vector2(60, 1050), "Золотые метки — куда ведут ясные записи. Блёклые — мутные или искажённые: могут врать.  Зелёные столбики — таксофоны.", F_BODY, 20, DIM)


# ======================= пауза и помощь =======================

func _pause() -> void:
	d.draw_rect(Rect2(0, 0, 1920, 1080), Color(0.04, 0.04, 0.05, 0.8))
	_text(Vector2(960, 330), "ПАУЗА", F_HEAD, 72, PAPER, HORIZONTAL_ALIGNMENT_CENTER, 0)
	pause_btns.clear()
	var items := [["resume", "Продолжить"], ["help", "Управление"], ["full", "Полный экран (F11)"], ["quit", "Бросить дело"]]
	var mp: Vector2 = d.get_local_mouse_position()
	for i in items.size():
		var r := Rect2(760, 420 + i * 84, 400, 64)
		var hov := r.has_point(mp)
		d.draw_rect(r, Color(K.GOLD, 0.9) if hov else Color(1, 1, 1, 0.08))
		_text(r.position + Vector2(0, 44), items[i][1], F_HEAD, 30, K.INK if hov else PAPER, HORIZONTAL_ALIGNMENT_CENTER, r.size.x)
		pause_btns.append([r, items[i][0]])


const HELP := [
	["В ТЕЛЕ", ""],
	["A / D", "идти;  Shift — бежать, Ctrl — красться, Space — прыжок"],
	["W / S", "лестница, люк, эскалатор, труба вверх/вниз; S — спрыгнуть с балкона"],
	["E", "дверь, вход, окно, разговор, улика, пульт, щиток, таксофон"],
	["Q (держать)", "задушить; на краю крыши или у дороги — столкнуть"],
	["G", "поднять / бросить тело;  E у шкафа или бака — спрятать"],
	["F", "покинуть тело;  T — ждать (×1, ×3, ×6), когда никто не смотрит"],
	["R (держать)", "у таксофона — экстренная линия: уйти, бросив дело"],
	["ВНЕ ТЕЛА", ""],
	["W A S D", "лететь;  Shift — быстрее;  W/S у лестницы — этаж;  E — вход, окно, форточка"],
	["F / ЛКМ", "войти в тело под мышью (−8 памяти, −28 если меньше 8 с назад)"],
	["1–5 и ЛКМ", "клешни: Дёрнуть, Утащить, Передвинуть, Оглушить, Задушить;  ПКМ — убрать"],
	["ОБЩЕЕ", ""],
	["Tab / M", "доска записей / карта района;  Esc — пауза;  F1 — эта справка;  F11 — экран"],
]


func _help() -> void:
	d.draw_rect(Rect2(0, 0, 1920, 1080), Color(0.04, 0.04, 0.05, 0.92))
	_text(Vector2(960, 140), "УПРАВЛЕНИЕ", F_HEAD, 56, PAPER, HORIZONTAL_ALIGNMENT_CENTER, 0)
	var y := 220.0
	for h in HELP:
		if h[1] == "":
			y += 14
			_text(Vector2(300, y), h[0], F_HEAD, 28, K.GOLD)
			y += 44
			continue
		_text(Vector2(300, y), h[0], F_HEAD, 24, PAPER)
		_text(Vector2(560, y), h[1], F_BODY, 24, Color(PAPER, 0.85))
		y += 40
	_text(Vector2(960, 1030), "F1 или Esc — закрыть", F_BODY, 22, DIM, HORIZONTAL_ALIGNMENT_CENTER, 0)


# ======================= конец =======================

func _draw_end() -> void:
	var a := clampf(end_t / 0.6, 0.0, 1.0)
	d.draw_rect(Rect2(0, 0, 1920, 1080), Color(0.04, 0.04, 0.05, 0.7 * a))
	var ok: bool = end.get("ok", false)
	var txt := "ДЕЛО ЗАКРЫТО" if ok else "ПРОВАЛ"
	var col := K.GOLD if ok else RED
	d.draw_set_transform(Vector2(960, 520), -0.08, Vector2.ONE * lerpf(1.6, 1.0, a))
	d.draw_rect(Rect2(-420, -90, 840, 150), Color(col, 0.0), false, 8.0)
	d.draw_rect(Rect2(-420, -90, 840, 150), Color(col, a), false, 8.0)
	_text(Vector2(-420, 20), txt, F_HEAD, 96, Color(col, a), HORIZONTAL_ALIGNMENT_CENTER, 840)
	d.draw_set_transform(Vector2.ZERO, 0.0, Vector2.ONE)
	var sub: String = end.get("grade", "") if ok else end.get("why", "")
	_text(Vector2(960, 680), sub, F_BODY, 32, Color(PAPER, a), HORIZONTAL_ALIGNMENT_CENTER, 0)


# ======================= папка куратора =======================

func _brief() -> void:
	var cs: Case = world.case
	d.draw_rect(Rect2(0, 0, 1920, 1080), Color(0.04, 0.04, 0.05, 0.86))
	var r := Rect2(180, 90, 1560, 900)
	d.draw_rect(r.grow(10), Color(0.42, 0.33, 0.2))
	d.draw_rect(Rect2(r.position, Vector2(r.size.x / 2 - 6, r.size.y)), Color(0.87, 0.83, 0.73))
	d.draw_rect(Rect2(r.position + Vector2(r.size.x / 2 + 6, 0), Vector2(r.size.x / 2 - 6, r.size.y)), Color(0.85, 0.81, 0.71))
	var ink := Color(0.16, 0.14, 0.12)
	var x := r.position.x + 50
	var y := r.position.y + 80
	_text(Vector2(x, y), "ДЕЛО №%d" % world.case_seed, F_HEAD, 48, ink)
	_text(Vector2(x + 660, y), "СЕКРЕТНО", F_HEAD, 30, Color(0.7, 0.2, 0.15), HORIZONTAL_ALIGNMENT_RIGHT, 0)
	y += 50
	_text(Vector2(x, y), "Куратор: %s.  Сложность: %s." % [cs.curator["name"], Game.difficulty], F_BODY, 24, ink)
	y += 50
	y += _wrap(Vector2(x, y), "«%s» %s" % [cs.curator["line"], cs.curator["tic"]], F_HAND, 34, Color(0.15, 0.15, 0.3), 660) + 20
	_text(Vector2(x, y), "ЧТО ИЗВЕСТНО О ЦЕЛИ", F_HEAD, 28, ink)
	y += 40
	var known := cs.cards.filter(func(c): return c["known"])
	for c in known:
		_text(Vector2(x, y), c["title"].to_upper(), F_HEAD, 22, Color(0.45, 0.35, 0.2))
		y += 6
		y += _wrap(Vector2(x, y + 24), cs.text(c), F_HAND, 32, Color(0.12, 0.12, 0.28), 660) + 26
	if known.is_empty():
		_wrap(Vector2(x, y + 20), "Ничего. Только место и час утром — да и то со слов.", F_HAND, 32, Color(0.12, 0.12, 0.28), 660)
	# правая страница
	x = r.position.x + r.size.x / 2 + 56
	y = r.position.y + 80
	_text(Vector2(x, y), "ЗАДАЧА", F_HEAD, 36, ink)
	y += 30
	var task := "1. Найти цель среди похожих. Записи тают с каждым прыжком и клешнёй — сверяй их с тем, что видишь.\n" + \
		"2. Снять. Чище всего — несчастный случай: крыша, дорога, горшок с подоконника.\n" + \
		"3. Подчистить хвосты: тело, камеры, свидетели.\n" + \
		"4. Уйти: позвоню на таксофон и назову время. Сними трубку телом.\n\n" + \
		"Время не останавливается. К рассвету (2:00) дело закроют без тебя."
	y += _wrap(Vector2(x, y + 20), task, F_BODY, 25, ink, 660) + 50
	_text(Vector2(x, y), "ГЛАВНОЕ", F_HEAD, 28, ink)
	y += 10
	var keys := "A/D, Space — тело; W/S — лестницы; E — действие; Q — руки; G — тело на плечо; F — выйти из тела.\n" + \
		"Вне тела: WASD — лететь, 1–5 и ЛКМ — клешни, F — войти в тело.\nTab — доска записей, M — карта, F1 — вся справка."
	_wrap(Vector2(x, y + 30), keys, F_BODY, 22, Color(0.3, 0.27, 0.22), 660)
	brief_btn = Rect2(r.end.x - 420, r.end.y - 100, 360, 64)
	var hov := brief_btn.has_point(d.get_local_mouse_position())
	d.draw_rect(brief_btn, Color(0.7, 0.2, 0.15) if hov else Color(0.55, 0.15, 0.12))
	_text(brief_btn.position + Vector2(0, 44), "ПРИНЯТЬ ДЕЛО", F_HEAD, 32, PAPER, HORIZONTAL_ALIGNMENT_CENTER, brief_btn.size.x)
