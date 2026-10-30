class_name Dog
extends Node2D
## Дворовая собака: чует духа, лает на него и рвёт его плотность. Людей поднимает на лай.

const WALK := 30.0
const RUN := 120.0

var world: Node
var city: City
var spr: Sprite2D
var home_x := 0.0
var x0 := 0.0
var x1 := 0.0
var state := "idle"            # idle, walk, chase, bark, look
var t := 0.0
var goal_x := 0.0
var anim_t := 0.0
var bark_t := 0.0
var facing := 1


func setup(w: Node, c: City) -> void:
	world = w
	city = c
	home_x = float(c.places["Двор"]["x"])
	x0 = home_x - 260.0
	x1 = home_x + 260.0
	position = Vector2(home_x, K.floor_y(0))
	spr = Res.prop_sprite("dog")
	spr.visibility_layer = K.V_OUTER
	add_child(spr)
	visibility_layer = K.V_OUTER
	z_index = K.Z_OUT_PEOPLE - 1
	goal_x = home_x


func _process(dt: float) -> void:
	if world.over or world.paused:
		return
	anim_t += dt
	t -= dt
	bark_t = maxf(0.0, bark_t - dt)
	var pl: PlayerCtl = world.player
	var sp := pl.spirit if pl and pl.host == null and pl.spirit.visible and not pl.spirit.inside else null
	if sp and absf(sp.global_position.x - position.x) < 190.0 and sp.global_position.y > position.y - 150.0:
		state = "chase"
		goal_x = clampf(sp.global_position.x, x0 - 200.0, x1 + 200.0)
	elif state == "chase":
		state = "idle"
		t = 2.0
		goal_x = home_x
	var dx := goal_x - position.x
	match state:
		"chase":
			if absf(dx) > 26.0:
				position.x += signf(dx) * RUN * dt
				facing = int(signf(dx))
				_frame("run")
			else:
				_frame("bark")
				facing = 1 if sp.global_position.x > position.x else -1
				if bark_t <= 0.0:
					bark_t = 0.55
					Sfx.play_at("bark", position, pl.focus_pos(), -4.0, randf_range(0.9, 1.1))
					world.noise_at(position, 140.0, null, "bark")
		"look":
			_frame("idle")
			if t <= 0.0:
				state = "idle"
		_:
			if absf(dx) > 4.0:
				position.x += signf(dx) * WALK * dt
				facing = int(signf(dx))
				_frame("walk")
			else:
				_frame("idle")
				if t <= 0.0:
					t = randf_range(3.0, 8.0)
					goal_x = randf_range(x0, x1)
	spr.flip_h = facing < 0


func _frame(nm: String) -> void:
	var f := 0
	match nm:
		"idle":
			f = int(anim_t * 1.5) % 2
		"walk":
			f = 2 + int(anim_t * 8.0) % 4
		"run":
			f = 6 + int(anim_t * 12.0) % 4
		"bark":
			f = 10 + int(anim_t * 6.0) % 2
	spr.frame = f


func drain_at(pos: Vector2, inside: bool) -> float:
	## Собака рядом с духом — плотность рвётся.
	if inside or state != "chase":
		return 0.0
	return 1.0 if pos.distance_to(position + Vector2(0, -10)) < 70.0 else 0.0


func hear(pos: Vector2, loud: float) -> void:
	if state == "chase":
		return
	if absf(pos.x - position.x) < loud and absf(pos.y - position.y) < 60.0:
		state = "look"
		t = 2.0
		facing = 1 if pos.x > position.x else -1
		if loud > 120.0 and bark_t <= 0.0:
			bark_t = 1.0
			Sfx.play_at("bark", position, world.player.focus_pos(), -10.0)
