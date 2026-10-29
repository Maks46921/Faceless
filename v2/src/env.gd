class_name Env
extends Node
## Время суток и погода: цвета неба, окружающий свет, солнце, фонари.

var hour := 8.0
var day_len_s := 70.0            # реальных секунд на игровой час
var speed := 1.0                 # ожидание [T]
var weather := "clear"           # clear, cloudy, rain, fog
var weather_plan: Array = []     # [[час, погода]]
var rain := 0.0                  # 0..1 сглаженная сила дождя
var fog := 0.0
var lightning := 0.0
var rng := RandomNumberGenerator.new()

var sky_top := Color()
var sky_bot := Color()
var amb_out := Color()
var amb_in := Color()
var sun_col := Color()
var sun_dir := Vector2(0.4, 1.0)   # куда светит солнце (вниз-вправо утром)
var sun_k := 0.0                    # сила прямого солнца 0..1
var night := 0.0                    # 0 день, 1 ночь


func setup(seed_v: int, start_h: float, hour_s: float) -> void:
	rng.seed = seed_v
	hour = start_h
	day_len_s = hour_s
	var opts := ["clear", "clear", "cloudy", "cloudy", "rain", "fog"]
	var h := 7.0
	while h < 30.0:
		weather_plan.append([h, opts[rng.randi() % opts.size()]])
		h += rng.randf_range(2.0, 4.5)
	weather_plan[0][1] = ["clear", "cloudy", "fog"][rng.randi() % 3]
	_apply_weather(true)


func tick(dt: float) -> void:
	hour += dt * speed / day_len_s
	_apply_weather(false)
	var tr := 1.0 if weather == "rain" else 0.0
	rain = move_toward(rain, tr, dt * 0.15)
	fog = move_toward(fog, 1.0 if weather == "fog" else 0.0, dt * 0.1)
	if weather == "rain" and rng.randf() < dt * 0.02 * rain:
		lightning = 1.0
	lightning = maxf(0.0, lightning - dt * 3.0)
	_colors()


func _apply_weather(_init: bool) -> void:
	for w in weather_plan:
		if hour >= float(w[0]):
			weather = w[1]


func weather_at(h: float) -> String:
	var out := "clear"
	for w in weather_plan:
		if h >= float(w[0]):
			out = w[1]
	return out


func _colors() -> void:
	var h := fmod(hour, 24.0)
	# 0 ночь, 1 день: рассвет 6–8, закат 18.5–20.5
	var d := 0.0
	if h >= 6.0 and h < 8.0:
		d = (h - 6.0) / 2.0
	elif h >= 8.0 and h < 18.5:
		d = 1.0
	elif h >= 18.5 and h < 20.5:
		d = 1.0 - (h - 18.5) / 2.0
	night = 1.0 - d
	var dusk := 0.0
	if h >= 17.5 and h < 21.0:
		dusk = 1.0 - absf(h - 19.3) / 1.7
	elif h >= 5.5 and h < 8.5:
		dusk = 1.0 - absf(h - 7.0) / 1.5
	dusk = clampf(dusk, 0.0, 1.0)
	var over := 0.0
	match weather:
		"cloudy": over = 0.6
		"rain": over = 0.85
		"fog": over = 0.7
	var day_top := Color(0.42, 0.55, 0.68).lerp(Color(0.55, 0.57, 0.6), over)
	var day_bot := Color(0.72, 0.76, 0.78).lerp(Color(0.66, 0.67, 0.68), over)
	var dusk_top := Color(0.32, 0.3, 0.45)
	var dusk_bot := Color(0.86, 0.55, 0.36).lerp(Color(0.55, 0.45, 0.42), over)
	var night_top := Color(0.03, 0.04, 0.08)
	var night_bot := Color(0.1, 0.11, 0.17)
	sky_top = night_top.lerp(day_top, d).lerp(dusk_top, dusk * 0.7)
	sky_bot = night_bot.lerp(day_bot, d).lerp(dusk_bot, dusk * 0.8)
	var a_day := Color(0.95, 0.95, 0.93).lerp(Color(0.78, 0.8, 0.84), over)
	var a_night := Color(0.13, 0.15, 0.24)
	amb_out = a_night.lerp(a_day, d).lerp(Color(0.85, 0.65, 0.55), dusk * 0.35)
	if lightning > 0.0:
		amb_out = amb_out.lerp(Color(1.2, 1.2, 1.3), lightning * 0.6)
	amb_in = Color(0.1, 0.1, 0.14).lerp(Color(0.78, 0.76, 0.72), d * (1.0 - over * 0.25))
	# солнце: с востока (слева) утром, с запада (справа) вечером
	var t := clampf((h - 6.5) / 13.0, 0.0, 1.0)
	var ang := lerpf(0.25, PI - 0.25, t)
	sun_dir = Vector2(cos(ang), sin(ang)).normalized()   # направление лучей: вниз
	sun_k = d * (1.0 - over) * (1.0 if h > 6.8 and h < 19.6 else 0.0)
	sun_col = Color(1.0, 0.95, 0.85).lerp(Color(1.0, 0.7, 0.45), dusk) * 0.35 * sun_k


func lamps_on() -> bool:
	var h := fmod(hour, 24.0)
	return h >= 18.6 or h < 7.2 or (weather in ["rain", "fog"] and (h >= 17.0 or h < 8.0))


func windows_on_k() -> float:
	return clampf(night * 1.2, 0.0, 1.0)
