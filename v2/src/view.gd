class_name View
extends Control
## Конвейер картинки: мир рисуется в низком разрешении в пять буферов (дальний план, интерьеры,
## улица и два буфера света), потом шейдер собирает кадр и растягивает его на экран.

const MARGIN := 2

var vp_out: SubViewport
var vps: Array = []
var rect: ColorRect
var mat: ShaderMaterial
var city: City
var env: Env
var cam := Vector2(400, 1200)       # центр камеры (мир)
var cam_target := Vector2(400, 1200)
var shake := 0.0
var far: FarLayer
var lbase_in: LightBase
var lbase_out: LightBase
var rain: RainLayer
var viewer_bid := -1                 # дом, внутри которого смотрит игрок
var viewer_inside := false
var viewer_under := false
var spirit_k := 0.0
var hurt_k := 0.0
var fade_k := 0.0
var t := 0.0


func setup(c: City, e: Env) -> void:
	city = c
	env = e
	set_anchors_preset(Control.PRESET_FULL_RECT)
	mouse_filter = Control.MOUSE_FILTER_IGNORE
	var sz := Vector2i(K.VIEW_W + MARGIN * 2, K.VIEW_H + MARGIN * 2)
	var masks := [K.V_FAR, K.V_INNER, K.V_OUTER, K.V_LIN, K.V_LOUT]
	for i in masks.size():
		var v := SubViewport.new()
		v.size = sz
		v.transparent_bg = i in [1, 2]
		v.render_target_update_mode = SubViewport.UPDATE_ALWAYS
		v.canvas_cull_mask = masks[i]
		v.disable_3d = true
		v.snap_2d_transforms_to_pixel = true
		v.canvas_item_default_texture_filter = Viewport.DEFAULT_CANVAS_ITEM_TEXTURE_FILTER_NEAREST
		add_child(v)
		vps.append(v)
	vp_out = vps[2]
	vp_out.add_child(city)
	vp_out.physics_object_picking = false
	for v in vps:
		if v != vp_out:
			(v as SubViewport).world_2d = vp_out.world_2d
	far = FarLayer.new()
	far.env = env
	far.visibility_layer = K.V_FAR
	far.z_index = -100
	city.add_child(far)
	lbase_in = LightBase.new()
	lbase_in.visibility_layer = K.V_LIN
	lbase_in.z_index = -100
	lbase_in.mode = 0
	lbase_in.env = env
	lbase_in.city = city
	city.add_child(lbase_in)
	lbase_out = LightBase.new()
	lbase_out.visibility_layer = K.V_LOUT
	lbase_out.z_index = -100
	lbase_out.mode = 1
	lbase_out.env = env
	lbase_out.city = city
	city.add_child(lbase_out)
	rain = RainLayer.new()
	rain.visibility_layer = K.V_OUTER
	rain.z_index = K.Z_FX
	rain.env = env
	rain.view = self
	city.add_child(rain)
	rect = ColorRect.new()
	rect.set_anchors_preset(Control.PRESET_FULL_RECT)
	rect.mouse_filter = Control.MOUSE_FILTER_IGNORE
	mat = ShaderMaterial.new()
	mat.shader = load("res://shaders/compose.gdshader")
	rect.material = mat
	add_child(rect)
	mat.set_shader_parameter("far_tex", vps[0].get_texture())
	mat.set_shader_parameter("in_tex", vps[1].get_texture())
	mat.set_shader_parameter("out_tex", vps[2].get_texture())
	mat.set_shader_parameter("lin_tex", vps[3].get_texture())
	mat.set_shader_parameter("lout_tex", vps[4].get_texture())
	mat.set_shader_parameter("tex_size", Vector2(sz))


func snap_to(p: Vector2) -> void:
	cam = p
	cam_target = p
	_apply()


func _process(dt: float) -> void:
	t += dt
	cam = cam.lerp(cam_target, 1.0 - exp(-dt * 6.0))
	shake = maxf(0.0, shake - dt * 2.0)
	_apply()
	_facades(dt)
	mat.set_shader_parameter("time_s", t)
	mat.set_shader_parameter("spirit", spirit_k)
	mat.set_shader_parameter("hurt", hurt_k)
	mat.set_shader_parameter("fade", fade_k)


func _apply() -> void:
	var half := Vector2(K.VIEW_W, K.VIEW_H) / 2.0
	var c := cam
	if shake > 0.0:
		c += Vector2(randf_range(-1, 1), randf_range(-1, 1)) * shake * 3.0
	var lo := half
	var hi := Vector2(city.width * K.T, K.ROWS * K.T) - half
	c.x = clampf(c.x, lo.x, hi.x)
	c.y = clampf(c.y, float((K.GY - 62) * K.T), hi.y)
	var tl := c - half
	var ti := tl.floor()
	var frac := tl - ti
	var xf := Transform2D(0.0, -ti + Vector2(MARGIN, MARGIN))
	for v in vps:
		(v as SubViewport).canvas_transform = xf
	mat.set_shader_parameter("sub_off", frac)
	far.position = ti - Vector2(MARGIN, MARGIN)
	far.cam = c
	lbase_in.position = far.position
	lbase_out.position = far.position
	rain.position = far.position
	lbase_out.queue_redraw()
	lbase_in.queue_redraw()
	far.queue_redraw()
	rain.queue_redraw()


func top_left() -> Vector2:
	return far.position + Vector2(MARGIN, MARGIN)


func world_to_screen(p: Vector2) -> Vector2:
	## Мировые пиксели -> координаты интерфейса (1920x1080).
	var s := size / Vector2(K.VIEW_W, K.VIEW_H)
	var tl := cam - Vector2(K.VIEW_W, K.VIEW_H) / 2.0
	var hi := Vector2(city.width * K.T, K.ROWS * K.T) - Vector2(K.VIEW_W, K.VIEW_H) / 2.0
	var c := Vector2(clampf(cam.x, K.VIEW_W / 2.0, hi.x), clampf(cam.y, float((K.GY - 62) * K.T), hi.y))
	tl = c - Vector2(K.VIEW_W, K.VIEW_H) / 2.0
	return (p - tl) * s


func screen_to_world(p: Vector2) -> Vector2:
	var s := size / Vector2(K.VIEW_W, K.VIEW_H)
	var hi := Vector2(city.width * K.T, K.ROWS * K.T) - Vector2(K.VIEW_W, K.VIEW_H) / 2.0
	var c := Vector2(clampf(cam.x, K.VIEW_W / 2.0, hi.x), clampf(cam.y, float((K.GY - 62) * K.T), hi.y))
	var tl := c - Vector2(K.VIEW_W, K.VIEW_H) / 2.0
	return tl + p / s


func _facades(dt: float) -> void:
	for b in city.buildings:
		var target := 1.0
		if viewer_inside and int(b["id"]) == viewer_bid:
			target = 0.0
		elif spirit_k > 0.5:
			target = 0.55
		var a := move_toward(float(b["facade_alpha"]), target, dt * 3.0)
		b["facade_alpha"] = a
		var tm: TileMapLayer = b["facade"]
		tm.modulate.a = a
		tm.visible = a > 0.01
		var fp: Node2D = b["fp"]
		fp.modulate.a = a
		fp.visible = a > 0.01


# ================= дальний план =================

class FarLayer extends Node2D:
	var env: Env
	var cam := Vector2.ZERO
	var sil: Array = []
	var sil2: Array = []
	var clouds: Array = []

	func _ready() -> void:
		var r := RandomNumberGenerator.new()
		r.seed = 99
		var x := -200.0
		while x < 3000.0:
			var w := r.randf_range(30, 90)
			sil.append([x, w, r.randf_range(60, 170), r.randi()])
			x += w + r.randf_range(-10, 12)
		x = -200.0
		while x < 3000.0:
			var w := r.randf_range(40, 110)
			sil2.append([x, w, r.randf_range(90, 230), r.randi()])
			x += w + r.randf_range(0, 30)
		for i in 9:
			clouds.append([r.randf_range(0, 2000), r.randf_range(10, 120), r.randf_range(60, 160), r.randf_range(0.5, 1.5)])

	func _draw() -> void:
		var W := float(K.VIEW_W + 8)
		var H := float(K.VIEW_H + 8)
		# небо: горизонт привязан к земле
		var horizon := K.floor_y(0) - 40.0 - (cam.y - K.VIEW_H / 2.0)
		var steps := 24
		for i in steps:
			var y0 := float(i) / steps * H
			var k := clampf((y0 - (horizon - 300.0)) / 300.0, 0.0, 1.0)
			draw_rect(Rect2(0, y0, W, H / steps + 1), env.sky_top.lerp(env.sky_bot, k))
		# солнце или луна
		var h := fmod(env.hour, 24.0)
		if env.night < 0.6:
			var t := clampf((h - 6.5) / 13.0, 0.0, 1.0)
			var sx := lerpf(40.0, W - 40.0, t)
			var sy := horizon - sin(t * PI) * 200.0
			var sc := Color(1.0, 0.92, 0.75, (1.0 - env.night) * (0.25 if env.weather != "clear" else 0.9))
			draw_circle(Vector2(sx, sy), 9.0, sc)
		else:
			draw_circle(Vector2(W * 0.7, horizon - 170.0), 6.0, Color(0.85, 0.87, 0.9, env.night * 0.8))
			var r := RandomNumberGenerator.new()
			r.seed = 5
			for i in 40:
				var p := Vector2(r.randf() * W, r.randf() * (horizon - 120.0))
				draw_rect(Rect2(p, Vector2(1, 1)), Color(1, 1, 1, env.night * 0.5 * (1.0 - env.fog) * (0.3 if env.weather in ["cloudy", "rain"] else 1.0)))
		# облака
		var cc := env.sky_bot.lerp(Color(0.8, 0.8, 0.82), 0.4)
		cc.a = 0.35 + (0.4 if env.weather in ["cloudy", "rain"] else 0.0)
		if env.night > 0.5:
			cc = Color(0.15, 0.16, 0.2, 0.5)
		for c in clouds:
			var x := fposmod(float(c[0]) - cam.x * 0.05 + env.hour * 30.0 * float(c[3]), W + 300.0) - 150.0
			var y := horizon - 260.0 + float(c[1])
			draw_rect(Rect2(x, y, float(c[2]), 6), cc)
			draw_rect(Rect2(x + 14, y - 5, float(c[2]) * 0.6, 6), cc)
		# дальние дома: два слоя параллакса, ТЭЦ
		var c2 := env.sky_bot.lerp(Color(0.25, 0.27, 0.3), 0.55)
		c2 = c2.darkened(0.15 + env.night * 0.5)
		_sil(sil2, 0.12, horizon + 50.0, c2, 0.4)
		var tx := fposmod(900.0 - cam.x * 0.12, 1800.0) - 300.0
		for k in 2:
			var px := tx + k * 46.0
			draw_rect(Rect2(px, horizon + 50.0 - 230.0, 12, 230), c2)
			draw_rect(Rect2(px, horizon + 50.0 - 220.0, 12, 4), Color(0.6, 0.25, 0.22, 0.8))
			for s in 6:
				var a := 0.18 - s * 0.025
				draw_circle(Vector2(px + 6 + s * 10 + sin(env.hour * 3.0 + s) * 3, horizon + 50.0 - 236.0 - s * 9), 6.0 + s * 2, Color(0.7, 0.7, 0.72, a))
		var c1 := env.sky_bot.lerp(Color(0.2, 0.21, 0.24), 0.75).darkened(0.1 + env.night * 0.55)
		_sil(sil, 0.25, horizon + 40.0, c1, 0.7)
		# туман
		if env.fog > 0.0:
			draw_rect(Rect2(0, 0, W, H), Color(0.6, 0.62, 0.64, env.fog * 0.45 * (1.0 - env.night * 0.6)))

	func _sil(arr: Array, par: float, base: float, c: Color, win: float) -> void:
		var W := float(K.VIEW_W + 8)
		var span := 3200.0
		var off := fposmod(-cam.x * par, span)
		for s in arr:
			var x := fposmod(float(s[0]) + off, span) - 200.0
			if x > W or x + float(s[1]) < 0:
				continue
			var hgt := float(s[2])
			draw_rect(Rect2(x, base - hgt, float(s[1]), hgt + 200), c)
			if env.night > 0.4:
				var r := RandomNumberGenerator.new()
				r.seed = int(s[3])
				var wy := base - hgt + 6
				while wy < base - 4:
					var wx := x + 4
					while wx < x + float(s[1]) - 4:
						if r.randf() < 0.18 * win:
							draw_rect(Rect2(wx, wy, 2, 2), Color(0.95, 0.8, 0.5, env.night * 0.7))
						wx += 6
					wy += 8


# ================= основа света =================

class LightBase extends Node2D:
	var mode := 0
	var env: Env
	var city: City

	func _draw() -> void:
		var W := float(K.VIEW_W + 8)
		var H := float(K.VIEW_H + 8)
		var gy := K.floor_y(0) + 2.0 - position.y
		if mode == 0:
			# окружающий свет в домах (половинная шкала), под землёй темно
			draw_rect(Rect2(-4, -4, W, H), _h(env.amb_in, 0.5))
			if gy < H:
				draw_rect(Rect2(-4, gy, W, H - gy + 4), Color(0.05, 0.05, 0.065))
			return
		draw_rect(Rect2(-4, -4, W, H), _h(env.amb_out + env.sun_col, 0.5))
		if env.sun_k > 0.01:
			for poly in shadow_polys(city, env):
				var pts := PackedVector2Array()
				for p in poly:
					pts.append(p - position)
				draw_colored_polygon(pts, _h(env.amb_out, 0.5))
		if gy < H:
			draw_rect(Rect2(-4, gy, W, H - gy + 4), _h(env.amb_out, 0.3))
		return

	static func _h(c: Color, k: float) -> Color:
		return Color(c.r * k, c.g * k, c.b * k, 1.0)

	static func shadow_polys(c: City, e: Env) -> Array:
		var out := []
		var s := e.sun_dir
		if s.y < 0.05:
			return out
		var gy := K.floor_y(0)
		for b in c.buildings:
			var top := float(int(b["roof_r"]) * K.T) - 6.0
			var len := (gy - top) * s.x / s.y
			if s.x >= 0:
				var x1 := float(b["px1"])
				out.append([Vector2(x1, top), Vector2(x1 + len, gy), Vector2(x1, gy)])
			else:
				var x0 := float(b["px0"])
				out.append([Vector2(x0, top), Vector2(x0, gy), Vector2(x0 + len, gy)])
		return out


# ================= дождь =================

class RainLayer extends Node2D:
	var env: Env
	var view: View
	var drops: Array = []

	func _ready() -> void:
		for i in 260:
			drops.append(Vector2(randf() * (K.VIEW_W + 40), randf() * (K.VIEW_H + 40)))

	func _draw() -> void:
		if env.rain < 0.02:
			return
		var n := int(drops.size() * env.rain)
		var gy := K.floor_y(0) - position.y
		var t := Time.get_ticks_msec() / 1000.0
		var skip0 := -1.0
		var skip1 := -1.0
		if view.viewer_inside and view.viewer_bid >= 0:
			var b: Dictionary = view.city.buildings[view.viewer_bid]
			skip0 = float(b["px0"]) - position.x
			skip1 = float(b["px1"]) - position.x
		for i in n:
			var d: Vector2 = drops[i]
			var y := fposmod(d.y + t * 420.0 + i * 13.0, K.VIEW_H + 40) - 20
			var x := fposmod(d.x - t * 60.0 + position.x * 0.0, K.VIEW_W + 40) - 20
			if y > gy:
				continue
			if x > skip0 and x < skip1:
				continue
			draw_line(Vector2(x, y), Vector2(x - 2, y + 7), Color(0.7, 0.75, 0.82, 0.35), 1.0)
		# брызги у земли
		if gy < K.VIEW_H + 4:
			for i in n / 6:
				var x2 := fposmod(drops[i].x * 1.7 + t * 37.0 * (i % 5), K.VIEW_W + 10)
				if x2 > skip0 and x2 < skip1:
					continue
				draw_rect(Rect2(x2, gy - 1, 2, 1), Color(0.75, 0.8, 0.85, 0.4))
