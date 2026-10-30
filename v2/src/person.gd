class_name Person
extends CharacterBody2D
## Человек: фигура из слоёв, ходьба, прыжки, лестницы и переходы между зонами.
## Им управляет либо мозг (Brain), либо игрок, который в него вселился.

const GRAV := 900.0
const JUMP_V := 268.0
const W_WALK := 50.0
const W_RUN := 118.0
const W_SNEAK := 28.0
const NFR := 57
const STAIR_K := 0.8          # по ступеням медленнее, чем по полу
const STEPS := 5              # ступеней в пролёте (для покачивания по шагам)

var world: Node
var city: City
var pid := 0
var first := ""
var last := ""
var female := false
var age := 1
var prof := "resident"
var cls := 1                   # 0 низ башни, 1 середина, 2 верх: одежда, речь, «чужой здесь»
var look := {}
var gait := ""                # limp, hunch, glance
var base_speed := W_WALK
var inside := false
var area := "S"
var facing := 1
var state := "ok"             # ok, ko, dead, carried, hidden, transit, gone
var pose := ""                # постоянная поза: sit, smoke, phone, talk, read, work, cower
var host := false
var brain: Brain
var fig: Node2D
var mat: ShaderMaterial
var sprites: Array = []
var anim := "idle"
var fade := 1.0                 # в кабине лифта фигуру не видно
var anim_t := 0.0
var frame := 0
var move_x := 0.0             # команда движения -1..1
var mode := "walk"            # walk, run, sneak
var want_jump := false
var drop_t := 0.0
var climbing := false
var climb_x := 0.0
var climb_y0 := 0.0
var climb_y1 := 0.0
var climb_v := 0.0
var transit := {}
var stair_in := 0.0             # игрок на марше: -1..1 вдоль пути (вперёд — туда, куда шёл)
var carrying: Person = null
var carried_by: Person = null
var ko_t := 0.0
var bubble := ""
var bubble_t := 0.0
var bubble_col := Color(0.92, 0.9, 0.84)
var keys: Array = []
var home := {}                # {area, x, apt, bid}
var work := {}
var flash := 0.0
var glance_t := 0.0
var look_t := 0.0
var fall_y0 := 0.0
var air := false
var step_t := 0.0
var raining := false
var dead_by := ""             # способ смерти
var hidden_in: Dictionary = {}
var last_floor_y := 0.0
var alpha := 1.0
var dormant := false            # далеко от камеры: без физики и картинки, ходит «по бумаге»


func _init() -> void:
	collision_layer = 0
	motion_mode = CharacterBody2D.MOTION_MODE_GROUNDED
	floor_snap_length = 6.0
	floor_max_angle = deg_to_rad(50)


func setup(w: Node, c: City, id: int, lk: Dictionary) -> void:
	world = w
	city = c
	pid = id
	look = lk
	female = lk.get("female", false)
	age = lk.get("age", 1)
	var sh := CollisionShape2D.new()
	var rs := RectangleShape2D.new()
	rs.size = Vector2(10, 38)
	sh.shape = rs
	sh.position = Vector2(0, -19)
	add_child(sh)
	fig = Node2D.new()
	fig.visibility_layer = K.V_ALL
	add_child(fig)
	mat = ShaderMaterial.new()
	mat.shader = Res.fig_shader
	fig.material = mat
	rebuild_fig()
	set_inside(inside)


func rebuild_fig() -> void:
	for s in sprites:
		s.queue_free()
	sprites.clear()
	var b: String = look.get("build", "m")
	for ln in Looks.layers(look, raining):
		var tex := Res.fig_tex(b, ln)
		if tex == null:
			continue
		var s := Sprite2D.new()
		s.texture = tex
		s.hframes = NFR
		s.centered = false
		# лист в двойной плотности: кадр 84×108, подошва на 104-м ряду
		s.offset = Vector2(-40, -104)
		s.scale = Vector2(0.5, 0.5)
		s.use_parent_material = true
		s.visibility_layer = K.V_ALL
		fig.add_child(s)
		sprites.append(s)
	mat.set_shader_parameter("pal", look["pal"])
	mat.set_shader_parameter("pattern", int(look.get("pattern", 0)))
	_set_frame(frame)


func full_name() -> String:
	return "%s %s" % [first, last]


func set_dormant(v: bool) -> void:
	if v == dormant:
		return
	dormant = v
	set_physics_process(not v)
	if v:
		visible = false
		move_x = 0.0
		velocity = Vector2.ZERO
	else:
		visible = not state in ["hidden", "gone"]


func set_inside(v: bool) -> void:
	inside = v
	# решётки и перегородки — только внутри: на улице они не должны мешать (стояли невидимыми ступеньками)
	var m := K.L_COMMON
	if drop_t <= 0.0:
		m |= K.L_PLATFORM
	if v:
		m |= K.L_INTERIOR | K.L_DOOR | K.L_GRATE
	collision_mask = m
	visibility_layer = K.V_INNER if v else K.V_OUTER
	z_index = K.Z_PEOPLE if v else K.Z_OUT_PEOPLE


func bid() -> int:
	if not city.areas.has(area):
		return -1
	return int(city.areas[area]["bid"])


func floor_i() -> int:
	if not city.areas.has(area):
		return 0
	return int(city.areas[area]["f"])


func head_pos() -> Vector2:
	return global_position + Vector2(0, -40.0 * float(Looks.BUILD_H.get(look.get("build", "m"), 1.0)))


func center() -> Vector2:
	return global_position + Vector2(0, -22)


func is_active() -> bool:
	return state == "ok" or state == "transit"


func is_down() -> bool:
	return state in ["ko", "dead", "carried", "hidden"]


func say(t: String, dur: float = 3.0, col: Color = Color(0.92, 0.9, 0.84)) -> void:
	bubble = t
	bubble_t = dur
	bubble_col = col


# ======================= кадры =======================

func _set_frame(f: int) -> void:
	frame = f
	for s in sprites:
		(s as Sprite2D).frame = f
	# лежачий кадр нарисован стоя: фигуру кладём поворотом, головой назад по взгляду
	if anim == "lie":
		fig.rotation = -PI / 2.0 * facing
		fig.position = Vector2(20.0 * facing, -6.0)
	elif fig.rotation != 0.0:
		fig.rotation = 0.0
		fig.position = Vector2.ZERO


func _anim(nm: String, dt: float, fps: float) -> void:
	if nm != anim:
		anim = nm
		anim_t = 0.0
	anim_t += dt * fps
	var fr: PackedInt32Array = Res.fig_frames.get(nm, Res.fig_frames["idle"])
	var i := int(anim_t) % fr.size()
	if fr[i] != frame:
		_set_frame(fr[i])


func _pick_anim(dt: float) -> void:
	if state == "dead":
		_anim("lie", dt, 1.0)
		return
	if state == "ko":
		_anim("slump" if ko_t > 1.0 else "kneel", dt, 1.0)
		return
	if state == "carried":
		_anim("lie", dt, 1.0)
		return
	if state == "transit":
		if transit.get("kind", "") == "stairs":
			var v := absf(float(transit.get("v", 0.0)))
			if v < 2.0:
				_anim("idle", dt, 0.8)
			elif mode == "run" and v > 60.0:
				_anim("run", dt, v / 46.0 * 6.0)
			elif mode == "sneak":
				_anim("sneak", dt, v / 18.0 * 4.0)
			else:
				_anim("walk", dt, v / 26.0 * 8.0)
			return
		var k: String = transit.get("anim", "walk")
		_anim(k, dt, 8.0 if k != "climb" else 5.0)
		return
	if climbing:
		_anim("climb", dt, absf(climb_v) / 12.0)
		return
	if carrying:
		_anim("carry" if absf(velocity.x) < 2 else "walk", dt, absf(velocity.x) / 28.0 * 8.0)
		return
	if not is_on_floor() and air:
		_anim("jump" if velocity.y < 0 else "fall", dt, 1.0)
		return
	var vx := absf(velocity.x)
	if vx > 2.0:
		if mode == "run" and vx > 70.0:
			_anim("run", dt, vx / 46.0 * 6.0)
		elif mode == "sneak":
			_anim("sneak", dt, vx / 18.0 * 4.0)
		elif gait == "limp":
			_anim("walk_limp", dt, vx / 24.0 * 8.0)
		elif gait == "hunch":
			_anim("walk_hunch", dt, vx / 24.0 * 8.0)
		elif look_t > 0.0:
			_anim("look", dt, 1.0)
		else:
			_anim("walk", dt, vx / 28.0 * 8.0)
		return
	if mode == "sneak" and host:
		_anim("crouch", dt, 1.0)
		return
	if pose != "":
		var p := pose
		if p == "read":
			p = "idle"
		if p == "work":
			p = "reach" if int(world.t_total * 0.7 + pid) % 4 == 0 else "idle"
		if p == "sit_floor":
			p = "slump"
		_anim(p, dt, 4.0 if p in ["strangle", "talk"] else 1.0)
		return
	if look_t > 0.0:
		_anim("look", dt, 1.0)
		return
	_anim("idle", dt, 0.8)


# ======================= движение =======================

func _physics_process(dt: float) -> void:
	if state == "gone":
		return
	flash = maxf(0.0, flash - dt * 3.0)
	if bubble_t > 0.0:
		bubble_t -= dt
		if bubble_t <= 0.0:
			bubble = ""
	look_t = maxf(0.0, look_t - dt)
	if drop_t > 0.0:
		drop_t -= dt
		if drop_t <= 0.0:
			set_inside(inside)
	if state == "transit":
		_transit(dt)
		_pick_anim(dt)
		_after(dt)
		return
	if state == "carried":
		if carried_by and is_instance_valid(carried_by):
			global_position = carried_by.global_position + Vector2(0, -30)
			facing = carried_by.facing
			if inside != carried_by.inside:
				set_inside(carried_by.inside)
			area = carried_by.area
			z_index = carried_by.z_index + 1
		_pick_anim(dt)
		_after(dt)
		return
	if state == "hidden":
		visible = false
		return
	if state == "ko":
		ko_t += dt
		velocity.x = 0.0
	if state == "dead" or state == "ko":
		velocity.x = move_toward(velocity.x, 0.0, dt * 400.0)
		velocity.y += GRAV * dt
		move_and_slide()
		_pick_anim(dt)
		_after(dt)
		return
	if climbing:
		_climb(dt)
		_pick_anim(dt)
		_after(dt)
		return
	var sp := base_speed
	if host:
		sp = W_WALK
	if mode == "run":
		sp = W_RUN if host else base_speed * 2.1
	elif mode == "sneak":
		sp = W_SNEAK
	if carrying:
		sp = minf(sp, 34.0)
	if gait == "limp" and not host:
		sp *= 0.72 if fmod(world.t_total + pid, 1.2) < 0.6 else 1.0
	var target_vx := move_x * sp
	velocity.x = move_toward(velocity.x, target_vx, dt * (900.0 if is_on_floor() else 300.0))
	if move_x > 0.05:
		facing = 1
	elif move_x < -0.05:
		facing = -1
	if not is_on_floor():
		velocity.y = minf(velocity.y + GRAV * dt, 520.0)
		if not air:
			air = true
			fall_y0 = global_position.y
	else:
		if air:
			_landed()
		air = false
		if want_jump and not carrying:
			velocity.y = -JUMP_V
			air = true
			fall_y0 = global_position.y
	want_jump = false
	var was_floor := is_on_floor()
	move_and_slide()
	if is_on_floor():
		last_floor_y = global_position.y
	# шаги
	if is_on_floor() and absf(velocity.x) > 10.0:
		step_t -= dt * absf(velocity.x) / 30.0
		if step_t <= 0.0:
			step_t = 1.0
			world.footstep(self)
	_pick_anim(dt)
	_after(dt)


func _after(_dt: float) -> void:
	fig.scale.x = float(facing)
	if mat:
		mat.set_shader_parameter("flash", flash)
	var a := alpha * fade
	if fig.modulate.a != a:
		fig.modulate.a = a


func _landed() -> void:
	var h := global_position.y - fall_y0
	if h > 30.0:
		world.noise_at(global_position, 60.0 + h * 0.4, self, "land")
	if h > 230.0:
		world.fall_hurt(self, h)


func climb_start(c: Dictionary) -> void:
	climbing = true
	climb_x = float(c["x"])
	climb_y0 = float(c["y0"])
	climb_y1 = float(c["y1"])
	velocity = Vector2.ZERO
	global_position.x = climb_x


func climb_stop() -> void:
	climbing = false
	air = true
	fall_y0 = global_position.y


func _climb(dt: float) -> void:
	velocity = Vector2.ZERO
	global_position.x = move_toward(global_position.x, climb_x, dt * 80.0)
	var y := global_position.y + climb_v * dt
	if y < climb_y0:
		# наверху: шаг на крышу
		y = climb_y0
		climbing = false
		global_position.y = y - 2
		velocity.y = -40
		return
	if y > climb_y1:
		y = climb_y1
		climbing = false
	global_position.y = y


# ======================= переходы =======================

func use_portal(p: Dictionary, dir: int) -> void:
	## Переход между зонами: лестница, лифт, вход, люк, окно, мостик. Пока идёт переход, физика выключена.
	var x0 := global_position.x
	var px := City.px_from(p, dir)
	var ya := float(p["ya"])
	var yb := float(p["yb"])
	var from_y := ya if dir > 0 else yb
	var to_y := yb if dir > 0 else ya
	var to_area: String = p["b"] if dir > 0 else p["a"]
	var pts: Array = []
	var anim_k := "walk"
	var dur := float(p.get("dur", 1.0))
	var kind: String = p["kind"]
	match kind:
		"stairs":
			# пролёт: от точки, где стоишь, к маршу и обратно на площадку
			var mid := (from_y + to_y) / 2.0
			var xl := px - 22.0
			var xr := px + 22.0
			pts = [Vector2(xl, from_y), Vector2(xr, mid), Vector2(xl, to_y)]
		"lift", "freight":
			pts = [Vector2(px, from_y), Vector2(px, to_y)]
			anim_k = "idle"
		"express":
			# у дверей ждут кабину (вместе со всеми), потом едут без остановок
			var slot := px + randf_range(-14.0, 14.0) if not host else px
			pts = [Vector2(slot, from_y), Vector2(px, from_y), Vector2(px, to_y)]
			anim_k = "idle"
		"entrance", "backdoor":
			pts = [Vector2(px, from_y), Vector2(px, to_y)]
		"hatch", "manhole", "shaft", "ladder", "ventshaft", "drain":
			pts = [Vector2(px, from_y), Vector2(px, to_y)]
			anim_k = "climb"
		"escalator":
			var dx := -60.0 if dir > 0 else 60.0
			pts = [Vector2(px, from_y), Vector2(px + dx, (from_y + to_y) / 2.0), Vector2(px, to_y)]
		"srvstairs":
			pts = [Vector2(px, from_y), Vector2(px + 20.0, (from_y + to_y) / 2.0), Vector2(px, to_y)]
		"bridge", "passage", "roofladder", "gate":
			var path: Array = (p["path"] as Array).duplicate()
			if dir < 0:
				path.reverse()
			pts = path
			var ln := 0.0
			for i in range(1, path.size()):
				ln += (path[i] as Vector2).distance_to(path[i - 1])
			dur = maxf(dur, ln / 55.0)
			if kind == "roofladder":
				anim_k = "climb"
		"window", "vent":
			pts = [Vector2(px, from_y), Vector2(px, to_y)]
	var to_inside: bool = city.areas[to_area]["inside"] if city.areas.has(to_area) else not inside
	if kind in ["window", "vent"]:
		to_inside = dir > 0
	transit = {"pts": [Vector2(x0, from_y)] + pts, "i": 0, "t": 0.0, "dur": dur, "to_area": to_area,
		"to_inside": to_inside, "anim": anim_k, "kind": kind, "p": p, "dir": dir}
	if kind == "express":
		transit["wait"] = world.express_wait(self, from_y)
		transit["waiting"] = true
	if kind == "stairs":
		# марш проходится шагами: игрок ведёт сам (W/S, A/D, Shift — бегом), жители — своим шагом
		var lens := []
		var tl := 0.0
		var all: Array = transit["pts"]
		for i in range(1, all.size()):
			var l := (all[i] as Vector2).distance_to(all[i - 1])
			lens.append(l)
			tl += l
		transit["lens"] = lens
		transit["L"] = tl
		transit["s"] = 0.0
		transit["v"] = 0.0
		transit["manual"] = host
		transit["from_area"] = area
		transit["switched"] = false
		stair_in = 0.0
	state = "transit"
	velocity = Vector2.ZERO
	climbing = false
	if kind in ["entrance", "backdoor", "window", "vent", "hatch", "manhole", "shaft", "escalator", "lift", "ladder", "srvstairs", "gate", "freight"]:
		world.portal_used(self, p, dir)


func stair_speed() -> float:
	var sp := W_WALK if host else base_speed
	if mode == "run":
		sp = W_RUN if host else base_speed * 2.1
	elif mode == "sneak":
		sp = W_SNEAK
	if carrying:
		sp = minf(sp, 30.0)
	return sp * STAIR_K


func stair_seg() -> int:
	## Номер отрезка пути, на котором стоит (0 — подход по площадке, дальше пролёты).
	var s: float = transit["s"]
	var lens: Array = transit["lens"]
	var acc := 0.0
	for i in lens.size():
		acc += float(lens[i])
		if s < acc:
			return i
	return lens.size() - 1


func stair_hdir() -> int:
	## Куда по горизонтали ведёт текущий отрезок, если идти вперёд.
	var pts: Array = transit["pts"]
	var i := stair_seg()
	var dx := (pts[i + 1] as Vector2).x - (pts[i] as Vector2).x
	return 1 if dx > 0.5 else (-1 if dx < -0.5 else 0)


func stair_up() -> bool:
	var pts: Array = transit["pts"]
	return (pts[pts.size() - 1] as Vector2).y < (pts[0] as Vector2).y


func stair_held() -> bool:
	## Разговор или руки на горле останавливают человека прямо на ступенях.
	if brain and not brain.react.is_empty() and brain.react.get("kind", "") == "talk":
		return true
	if world.player and world.player.strangle.get("victim") == self:
		return true
	return world.hud != null and world.hud.talk != null and world.hud.talk.q == self


func _stairs(dt: float) -> void:
	var pts: Array = transit["pts"]
	var lens: Array = transit["lens"]
	var tl: float = transit["L"]
	var v := stair_speed()
	if bool(transit["manual"]):
		v *= stair_in
	if not host and stair_held():
		v = 0.0
	transit["v"] = v
	var s: float = float(transit["s"]) + v * dt
	if s <= 0.0 and v < 0.0:
		_stairs_back()
		return
	s = clampf(s, 0.0, tl)
	transit["s"] = s
	# где на пути
	var acc := 0.0
	var pos: Vector2 = pts[pts.size() - 1]
	for i in lens.size():
		var l := float(lens[i])
		if s <= acc + l or i == lens.size() - 1:
			var k := 0.0 if l < 0.01 else clampf((s - acc) / l, 0.0, 1.0)
			var a: Vector2 = pts[i]
			var b: Vector2 = pts[i + 1]
			pos = a.lerp(b, k)
			if i >= 1 and absf(b.y - a.y) > 4.0:
				# по ступенькам: нога поднимается в конце каждого шага
				var n := k * STEPS
				var st := floorf(n) + smoothstep(0.55, 1.0, n - floorf(n))
				pos.y = a.y + (b.y - a.y) * minf(st / STEPS, 1.0)
			if absf(b.x - a.x) > 0.5 and absf(v) > 0.5:
				facing = (1 if b.x > a.x else -1) * (1 if v > 0 else -1)
			break
		acc += l
	global_position = pos
	# зона меняется на середине пути: на площадке между этажами видно уже другой этаж
	var half := tl * 0.5
	if s >= half and not transit["switched"]:
		transit["switched"] = true
		if city.areas.has(transit["to_area"]):
			area = transit["to_area"]
	elif s < half and transit["switched"]:
		transit["switched"] = false
		area = transit["from_area"]
	# шаги слышно; бег по лестнице — громко
	if absf(v) > 4.0:
		step_t -= dt * absf(v) / 26.0
		if step_t <= 0.0:
			step_t = 1.0
			world.footstep(self)
	if s >= tl:
		_end_transit()


func _stairs_back() -> void:
	## Передумал и спустился (поднялся) обратно на свою площадку.
	area = transit["from_area"]
	global_position = transit["pts"][0]
	state = "ok"
	velocity = Vector2.ZERO
	air = false
	fade = 1.0
	transit = {}
	world.transit_done(self)


func drop_transit() -> void:
	## Человека остановили посреди перехода (упал без сознания, умер): дальше падает сам.
	if state != "transit":
		return
	if transit.get("switched", false) == false and transit.has("from_area"):
		area = transit["from_area"]
	transit = {}
	state = "ok"
	fade = 1.0
	air = true
	fall_y0 = global_position.y


func _transit(dt: float) -> void:
	if transit.get("kind", "") == "stairs":
		_stairs(dt)
		return
	if transit.get("waiting", false) and int(transit["i"]) >= 1:
		# стоит у дверей экспресса, пока не придёт кабина
		transit["wait"] = float(transit["wait"]) - dt
		if float(transit["wait"]) > 0.0:
			return
		transit["waiting"] = false
		world.express_board(self)
	var pts: Array = transit["pts"]
	var i: int = transit["i"]
	if i >= pts.size() - 1:
		_end_transit()
		return
	var a: Vector2 = pts[i]
	var b: Vector2 = pts[i + 1]
	var segs := pts.size() - 1
	var seg_dur := float(transit["dur"]) / segs
	if transit["kind"] == "express" and i >= 1:
		seg_dur = 0.5 if i == 1 else float(transit["dur"])
	elif i == 0 and a.distance_to(b) > 1.0:
		seg_dur = maxf(0.15, a.distance_to(b) / 60.0)
	transit["t"] = float(transit["t"]) + dt / seg_dur
	var k := clampf(float(transit["t"]), 0.0, 1.0)
	global_position = a.lerp(b, k)
	if absf(b.x - a.x) > 1.0:
		facing = 1 if b.x > a.x else -1
	if transit["kind"] in ["lift", "freight"]:
		fade = 0.0 if i > 0 else 1.0 - k
	elif transit["kind"] == "express":
		fade = 1.0 if i == 0 else (1.0 - k if i == 1 else 0.0)
	# внутренний/внешний меняются на середине перехода
	if transit["kind"] in ["entrance", "backdoor", "window", "vent", "hatch", "manhole", "escalator", "gate"] and i == segs - 1 and k > 0.5:
		if inside != bool(transit["to_inside"]):
			set_inside(bool(transit["to_inside"]))
			world.inside_changed(self)
	if k >= 1.0:
		transit["i"] = i + 1
		transit["t"] = 0.0
		if i + 1 >= pts.size() - 1:
			_end_transit()


func _end_transit() -> void:
	var to: String = transit["to_area"]
	if city.areas.has(to):
		area = to
	elif to == "OUT":
		area = city.area_at(global_position, false)
	if inside != bool(transit["to_inside"]):
		set_inside(bool(transit["to_inside"]))
		world.inside_changed(self)
	state = "ok"
	velocity = Vector2.ZERO
	air = false
	fade = 1.0
	transit = {}
	world.transit_done(self)


func update_area() -> void:
	## Уточняет зону по положению (после прыжков, падений, выхода духа).
	var a := city.area_at(global_position, inside)
	if a != "":
		area = a


# ======================= состояния =======================

func knock_out(dur: float) -> void:
	if state == "dead":
		return
	if state == "transit":
		drop_transit()
	state = "ko"
	ko_t = 0.0
	pose = ""
	move_x = 0.0
	velocity.x = 0.0
	if brain:
		brain.ko_left = dur


func wake_up() -> void:
	if state != "ko":
		return
	state = "ok"
	anim = ""


func die(how: String) -> void:
	if state == "transit":
		drop_transit()
	state = "dead"
	dead_by = how
	pose = ""
	move_x = 0.0
	bubble = ""
	climbing = false
	if carrying:
		carrying.drop_from(self)
		carrying = null


func pick_up(other: Person) -> void:
	carrying = other
	other.carried_by = self
	other.state = "carried"
	other.collision_layer = 0


func drop_from(by: Person) -> void:
	carried_by = null
	state = "dead" if dead_by != "" else "ko"
	global_position = by.global_position + Vector2(by.facing * 10, 0)
	area = by.area
	set_inside(by.inside)
	visible = true
	velocity = Vector2.ZERO
