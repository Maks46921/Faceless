class_name Spirit
extends CharacterBody2D
## Дух вне тела: летает, проходит в лазы и под дверями, держит предметы клешнями.

const SPEED := 92.0
const FAST := 150.0

var city: City
var inside := false
var area := "S"
var spr: Sprite2D
var claw_l: Sprite2D
var claw_r: Sprite2D
var anim_t := 0.0
var move := Vector2.ZERO
var fast := false
var held := {}                 # предмет в клешне
var claw_t := 0.0              # анимация удара клешнёй
var claw_target := Vector2.ZERO
var still_t := 0.0
var transit := {}
var flicker := 0.0


func setup(c: City) -> void:
	city = c
	collision_layer = 0
	motion_mode = CharacterBody2D.MOTION_MODE_FLOATING
	var sh := CollisionShape2D.new()
	var rs := RectangleShape2D.new()
	rs.size = Vector2(6, 8)
	sh.shape = rs
	sh.position = Vector2(0, -6)
	add_child(sh)
	spr = Res.prop_sprite("spirit")
	spr.visibility_layer = K.V_ALL
	spr.position = Vector2(0, 4)
	spr.self_modulate = Color(1.9, 2.1, 2.5)
	add_child(spr)
	claw_l = Res.prop_sprite("claw")
	claw_r = Res.prop_sprite("claw")
	for c2 in [claw_l, claw_r]:
		c2.visibility_layer = K.V_ALL
		c2.centered = true
		c2.offset = Vector2(6, 0)
		add_child(c2)
	# собственное слабое свечение: дух виден и в темноте
	var gl := Sprite2D.new()
	gl.texture = Res.light_tex
	gl.scale = Vector2(90, 90) / 128.0
	gl.position = Vector2(0, -8)
	gl.modulate = Color(0.42, 0.5, 0.62)
	var m := CanvasItemMaterial.new()
	m.blend_mode = CanvasItemMaterial.BLEND_MODE_ADD
	gl.material = m
	gl.visibility_layer = K.V_LIN | K.V_LOUT
	add_child(gl)
	set_inside(false)


func set_inside(v: bool) -> void:
	inside = v
	collision_mask = K.L_COMMON | (K.L_INTERIOR if v else 0)
	visibility_layer = K.V_INNER if v else K.V_OUTER
	z_index = K.Z_PEOPLE + 3 if v else K.Z_OUT_PEOPLE + 3


func center() -> Vector2:
	return global_position + Vector2(0, -8)


func _physics_process(dt: float) -> void:
	if not visible:
		return
	anim_t += dt * 7.0
	spr.frame = int(anim_t) % 6
	spr.modulate.a = 0.92 - flicker * 0.5 * (0.5 + 0.5 * sin(anim_t * 5.0))
	if not transit.is_empty():
		_transit(dt)
		_claws(dt)
		return
	var sp := FAST if fast else SPEED
	var target := move.normalized() * sp if move.length() > 0.1 else Vector2.ZERO
	velocity = velocity.lerp(target, 1.0 - exp(-dt * 8.0))
	# лёгкое парение
	velocity.y += sin(anim_t * 0.6) * 4.0 * dt * 60.0 * 0.05
	move_and_slide()
	if velocity.length() < 8.0:
		still_t += dt
	else:
		still_t = 0.0
	if absf(velocity.x) > 4:
		spr.flip_h = velocity.x < 0
	_claws(dt)


func _claws(dt: float) -> void:
	claw_t = maxf(0.0, claw_t - dt * 2.5)
	var base_l := Vector2(-9, -10 + sin(anim_t * 0.9) * 2)
	var base_r := Vector2(9, -10 + cos(anim_t * 0.8) * 2)
	claw_l.position = base_l
	claw_r.position = base_r
	claw_l.rotation = PI + sin(anim_t * 0.5) * 0.4
	claw_r.rotation = sin(anim_t * 0.45) * 0.4
	claw_l.frame = 0
	claw_r.frame = 2 if not held.is_empty() else 0
	if claw_t > 0.0:
		var to := claw_target - global_position
		var k := sin(claw_t * PI)
		claw_r.position = base_r.lerp(to, k * 0.9)
		claw_r.rotation = to.angle()
		claw_r.frame = 1 if claw_t > 0.5 else 2


func strike(at: Vector2) -> void:
	claw_t = 1.0
	claw_target = at


func go_portal(p: Dictionary, dir: int) -> void:
	var from_y := float(p["ya"]) if dir > 0 else float(p["yb"])
	var to_y := float(p["yb"]) if dir > 0 else float(p["ya"])
	var to_area: String = p["b"] if dir > 0 else p["a"]
	var to_inside: bool = dir > 0 if p["kind"] in ["window", "vent"] else bool(city.areas[to_area]["inside"]) if city.areas.has(to_area) else not inside
	var px := float(p["x"])
	transit = {"pts": [global_position, Vector2(px, from_y - 10), Vector2(px, to_y - 10)], "i": 0, "t": 0.0, "to_area": to_area, "to_inside": to_inside}


func _transit(dt: float) -> void:
	var pts: Array = transit["pts"]
	var i: int = transit["i"]
	var a: Vector2 = pts[i]
	var b: Vector2 = pts[i + 1]
	var dur := maxf(0.12, a.distance_to(b) / 160.0)
	transit["t"] = float(transit["t"]) + dt / dur
	var k := clampf(float(transit["t"]), 0.0, 1.0)
	global_position = a.lerp(b, k)
	if i == pts.size() - 2 and k > 0.4 and inside != bool(transit["to_inside"]):
		set_inside(bool(transit["to_inside"]))
	if k >= 1.0:
		transit["i"] = i + 1
		transit["t"] = 0.0
		if i + 1 >= pts.size() - 1:
			var to: String = transit["to_area"]
			area = to if city.areas.has(to) else city.area_at(global_position + Vector2(0, 10), inside)
			set_inside(bool(transit["to_inside"]))
			transit = {}
			velocity = Vector2.ZERO
