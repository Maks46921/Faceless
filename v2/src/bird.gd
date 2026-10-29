class_name Bird
extends Node2D
## Голуби и вороны: клюют, разлетаются от людей и духа, потом возвращаются.

var kind := "pigeon"
var spr: Sprite2D
var home := Vector2.ZERO
var state := "peck"            # peck, fly, away
var t := 0.0
var vel := Vector2.ZERO
var anim_t := 0.0


func setup(k: String, pos: Vector2) -> void:
	kind = k
	home = pos
	position = pos
	spr = Res.prop_sprite(k)
	spr.visibility_layer = K.V_OUTER
	add_child(spr)
	visibility_layer = K.V_OUTER
	z_index = K.Z_OUT_PEOPLE - 2
	anim_t = randf() * 3.0


func _process(dt: float) -> void:
	anim_t += dt
	var w := get_parent()
	while w and not w.has_method("can_see"):
		w = w.get_parent()
	match state:
		"peck":
			var n := spr.hframes
			spr.frame = (int(anim_t * 2.0) % 2) if n >= 2 else 0
			t -= dt
			if t <= 0.0:
				t = randf_range(1.0, 4.0)
				spr.flip_h = randf() < 0.5
				position.x = clampf(position.x + randf_range(-8, 8), home.x - 40, home.x + 40)
			if w and _threat(w):
				scatter()
		"fly":
			position += vel * dt
			vel.y -= 30.0 * dt
			if spr.hframes >= 4:
				spr.frame = 2 + int(anim_t * 10.0) % 2
			t -= dt
			if t <= 0.0:
				state = "away"
				visible = false
				t = randf_range(15.0, 30.0)
		"away":
			t -= dt
			if t <= 0.0:
				state = "peck"
				visible = true
				position = home + Vector2(randf_range(-30, 30), 0)


func _threat(w: Node) -> bool:
	var pl = w.get("player")
	if pl and pl.host == null and pl.spirit.visible and not pl.spirit.inside and pl.spirit.global_position.distance_to(position) < 60.0:
		return true
	for p in w.people:
		if not p.inside and p.state == "ok" and absf(p.global_position.x - position.x) < 22.0 and absf(p.global_position.y - position.y) < 10.0 and absf(p.velocity.x) > 60.0:
			return true
	return false


func scatter() -> void:
	if state != "peck":
		return
	state = "fly"
	t = 2.5
	vel = Vector2(randf_range(-60, 60), randf_range(-110, -70))
	spr.flip_h = vel.x < 0
	Sfx.play("paper", -24.0, 1.6)
