extends Node
## Звук, синтезированный кодом: шаги, двери, клешни, собака, звонок, сердце, фоны города, дождя и подземки.

const RATE := 22050
var streams := {}
var pool: Array = []
var loops := {}            # имя -> AudioStreamPlayer
var rng := RandomNumberGenerator.new()


func _ready() -> void:
	rng.seed = 3
	_make_all()
	for i in 14:
		var p := AudioStreamPlayer.new()
		add_child(p)
		pool.append(p)
	for nm in ["city", "rain", "under", "spirit", "heart", "wind"]:
		var p := AudioStreamPlayer.new()
		p.stream = streams[nm]
		p.volume_db = -80.0
		add_child(p)
		p.play()
		loops[nm] = p


func play(nm: String, vol_db: float = 0.0, pitch: float = 1.0) -> void:
	if not streams.has(nm):
		return
	for p in pool:
		var ap := p as AudioStreamPlayer
		if not ap.playing:
			ap.stream = streams[nm]
			ap.volume_db = vol_db
			ap.pitch_scale = pitch * rng.randf_range(0.95, 1.05)
			ap.play()
			return


func play_at(nm: String, world_pos: Vector2, listener: Vector2, vol_db: float = 0.0, pitch: float = 1.0) -> void:
	var d := world_pos.distance_to(listener)
	if d > 520.0:
		return
	play(nm, vol_db - d / 520.0 * 22.0, pitch)


func loop_level(nm: String, lin: float, dt: float) -> void:
	if not loops.has(nm):
		return
	var p: AudioStreamPlayer = loops[nm]
	var target := linear_to_db(maxf(0.0005, lin))
	p.volume_db = move_toward(p.volume_db, target, dt * 30.0)


# ---------------- синтез ----------------

func _wav(data: PackedFloat32Array, loop: bool = false) -> AudioStreamWAV:
	var b := PackedByteArray()
	b.resize(data.size() * 2)
	for i in data.size():
		var v := int(clampf(data[i], -1.0, 1.0) * 32000.0)
		b.encode_s16(i * 2, v)
	var w := AudioStreamWAV.new()
	w.format = AudioStreamWAV.FORMAT_16_BITS
	w.mix_rate = RATE
	w.stereo = false
	w.data = b
	if loop:
		w.loop_mode = AudioStreamWAV.LOOP_FORWARD
		w.loop_begin = 0
		w.loop_end = data.size()
	return w


func _buf(sec: float) -> PackedFloat32Array:
	var a := PackedFloat32Array()
	a.resize(int(sec * RATE))
	return a


func _noise_burst(sec: float, decay: float, lp: float, gain: float) -> PackedFloat32Array:
	var a := _buf(sec)
	var y := 0.0
	for i in a.size():
		var t := float(i) / RATE
		var n := rng.randf_range(-1, 1)
		y += (n - y) * lp
		a[i] = y * exp(-t * decay) * gain
	return a


func _tone(sec: float, f0: float, f1: float, decay: float, gain: float, shape: int = 0) -> PackedFloat32Array:
	var a := _buf(sec)
	var ph := 0.0
	for i in a.size():
		var t := float(i) / RATE
		var f := lerpf(f0, f1, t / sec)
		ph += f / RATE
		var s := sin(ph * TAU)
		if shape == 1:
			s = 1.0 if fmod(ph, 1.0) < 0.5 else -1.0
		elif shape == 2:
			s = fmod(ph, 1.0) * 2.0 - 1.0
		a[i] = s * exp(-t * decay) * gain
	return a


func _mix(a: PackedFloat32Array, b: PackedFloat32Array, k: float = 1.0) -> PackedFloat32Array:
	var n := maxi(a.size(), b.size())
	var o := PackedFloat32Array()
	o.resize(n)
	for i in n:
		o[i] = (a[i] if i < a.size() else 0.0) + (b[i] if i < b.size() else 0.0) * k
	return o


func _make_all() -> void:
	streams["step"] = _wav(_noise_burst(0.08, 60.0, 0.25, 0.5))
	streams["step_hard"] = _wav(_mix(_noise_burst(0.07, 70.0, 0.5, 0.45), _tone(0.06, 140, 90, 50, 0.3)))
	streams["land"] = _wav(_mix(_noise_burst(0.15, 30.0, 0.2, 0.8), _tone(0.12, 90, 50, 30, 0.5)))
	streams["door"] = _wav(_mix(_tone(0.25, 180, 120, 14, 0.4, 2), _noise_burst(0.2, 25, 0.15, 0.4)))
	streams["door_lock"] = _wav(_mix(_tone(0.12, 900, 600, 40, 0.3, 1), _noise_burst(0.1, 50, 0.6, 0.3)))
	streams["claw"] = _wav(_mix(_noise_burst(0.3, 9.0, 0.7, 0.35), _tone(0.3, 2200, 1500, 10, 0.08, 2)))
	streams["grab"] = _wav(_mix(_noise_burst(0.12, 30.0, 0.5, 0.5), _tone(0.1, 300, 200, 30, 0.3)))
	streams["crash"] = _wav(_mix(_noise_burst(0.6, 6.0, 0.6, 0.9), _tone(0.4, 220, 80, 9, 0.4, 2)))
	streams["thud"] = _wav(_mix(_tone(0.3, 110, 45, 12, 0.9), _noise_burst(0.2, 20, 0.12, 0.6)))
	streams["click"] = _wav(_tone(0.05, 1800, 1200, 80, 0.4, 1))
	streams["switch"] = _wav(_mix(_tone(0.08, 600, 400, 60, 0.5, 1), _tone(0.4, 60, 60, 4, 0.3)))
	streams["bark"] = _wav(_mix(_tone(0.18, 520, 300, 14, 0.6, 2), _noise_burst(0.18, 16, 0.4, 0.45)))
	streams["growl"] = _wav(_mix(_tone(0.6, 85, 70, 3, 0.4, 2), _noise_burst(0.6, 3, 0.08, 0.4)))
	streams["glitch"] = _wav(_glitch())
	streams["enter"] = _wav(_mix(_tone(0.7, 90, 380, 3.5, 0.45), _noise_burst(0.7, 4, 0.3, 0.3)))
	streams["leave"] = _wav(_mix(_tone(0.7, 380, 70, 3.5, 0.45), _noise_burst(0.7, 4, 0.3, 0.3)))
	streams["ring"] = _wav(_ring())
	streams["pickup"] = _wav(_mix(_tone(0.15, 300, 300, 20, 0.4, 1), _noise_burst(0.1, 40, 0.5, 0.3)))
	streams["choke"] = _wav(_mix(_noise_burst(1.2, 1.5, 0.08, 0.5), _tone(1.2, 140, 90, 1.8, 0.2, 2)))
	streams["car"] = _wav(_car())
	streams["paper"] = _wav(_noise_burst(0.25, 12.0, 0.9, 0.3))
	streams["memory"] = _wav(_mix(_tone(1.2, 660, 640, 2.5, 0.25), _tone(1.2, 990, 960, 2.8, 0.15)))
	streams["alarm"] = _wav(_alarm())
	streams["siren"] = _wav(_siren(), true)
	streams["stamp"] = _wav(_mix(_tone(0.2, 90, 50, 18, 0.9), _noise_burst(0.15, 30, 0.3, 0.6)))
	streams["hurt"] = _wav(_mix(_tone(0.4, 300, 120, 7, 0.3, 2), _noise_burst(0.4, 8, 0.5, 0.4)))
	streams["fall"] = _wav(_tone(0.8, 500, 120, 2.0, 0.3))
	streams["train"] = _wav(_mix(_noise_burst(3.0, 0.6, 0.05, 0.8), _tone(3.0, 70, 55, 0.7, 0.3, 2)))
	streams["ui"] = _wav(_tone(0.06, 900, 900, 50, 0.25))
	streams["ui_ok"] = _wav(_mix(_tone(0.12, 660, 660, 25, 0.25), _tone(0.12, 990, 990, 25, 0.15)))
	streams["city"] = _wav(_amb_city(), true)
	streams["rain"] = _wav(_amb_rain(), true)
	streams["under"] = _wav(_amb_under(), true)
	streams["spirit"] = _wav(_amb_spirit(), true)
	streams["heart"] = _wav(_heart(), true)
	streams["wind"] = _wav(_amb_wind(), true)


func _glitch() -> PackedFloat32Array:
	var a := _buf(0.45)
	var v := 0.0
	for i in a.size():
		if i % 300 == 0:
			v = rng.randf_range(-0.6, 0.6)
		a[i] = v * (1.0 - float(i) / a.size()) + rng.randf_range(-0.1, 0.1)
	return a


func _ring() -> PackedFloat32Array:
	var a := _buf(1.6)
	for i in a.size():
		var t := float(i) / RATE
		var on := 1.0 if fmod(t, 0.1) < 0.05 and t < 1.2 else 0.0
		a[i] = (sin(t * TAU * 1100.0) + sin(t * TAU * 1400.0)) * 0.18 * on
	return a


func _car() -> PackedFloat32Array:
	var a := _buf(1.4)
	var y := 0.0
	for i in a.size():
		var t := float(i) / RATE
		y += (rng.randf_range(-1, 1) - y) * 0.06
		var env := sin(t / 1.4 * PI)
		a[i] = (y * 0.8 + sin(t * TAU * (60.0 + 20.0 * t)) * 0.2) * env * 0.7
	return a


func _alarm() -> PackedFloat32Array:
	var a := _buf(1.0)
	for i in a.size():
		var t := float(i) / RATE
		a[i] = sin(t * TAU * (700.0 if fmod(t, 0.25) < 0.125 else 520.0)) * 0.25 * (1.0 - t)
	return a


func _siren() -> PackedFloat32Array:
	var a := _buf(2.0)
	var ph := 0.0
	for i in a.size():
		var t := float(i) / RATE
		ph += (600.0 + 250.0 * sin(t * PI)) / RATE
		a[i] = sin(ph * TAU) * 0.18
	return a


func _amb_city() -> PackedFloat32Array:
	var a := _buf(6.0)
	var y := 0.0
	var y2 := 0.0
	for i in a.size():
		var t := float(i) / RATE
		y += (rng.randf_range(-1, 1) - y) * 0.015
		y2 += (rng.randf_range(-1, 1) - y2) * 0.2
		a[i] = y * 0.9 + y2 * 0.02 + sin(t * TAU * 50.0) * 0.02
	_fade_loop(a)
	return a


func _amb_rain() -> PackedFloat32Array:
	var a := _buf(4.0)
	var y := 0.0
	for i in a.size():
		y += (rng.randf_range(-1, 1) - y) * 0.45
		var drop := 0.0
		if rng.randf() < 0.002:
			drop = rng.randf_range(0.2, 0.5)
		a[i] = y * 0.25 + drop
	_fade_loop(a)
	return a


func _amb_under() -> PackedFloat32Array:
	var a := _buf(6.0)
	var y := 0.0
	for i in a.size():
		var t := float(i) / RATE
		y += (rng.randf_range(-1, 1) - y) * 0.008
		var drip := 0.0
		if i % 30000 < 300:
			drip = sin(float(i % 30000) / 300.0 * PI) * sin(t * TAU * 1300.0) * 0.15
		a[i] = y * 1.2 + sin(t * TAU * 41.0) * 0.05 + drip
	_fade_loop(a)
	return a


func _amb_spirit() -> PackedFloat32Array:
	var a := _buf(8.0)
	for i in a.size():
		var t := float(i) / RATE
		var ch := sin(t * TAU * 110.0) * 0.08 + sin(t * TAU * 164.8) * 0.06 + sin(t * TAU * 220.5 + sin(t * 0.7) * 2.0) * 0.05
		a[i] = ch * (0.6 + 0.4 * sin(t * TAU / 8.0))
	return a


func _heart() -> PackedFloat32Array:
	var a := _buf(1.0)
	for i in a.size():
		var t := float(i) / RATE
		var b1 := exp(-pow((t - 0.05) * 40.0, 2.0))
		var b2 := exp(-pow((t - 0.28) * 40.0, 2.0)) * 0.7
		a[i] = sin(t * TAU * 55.0) * (b1 + b2) * 0.9
	return a


func _amb_wind() -> PackedFloat32Array:
	var a := _buf(6.0)
	var y := 0.0
	for i in a.size():
		var t := float(i) / RATE
		y += (rng.randf_range(-1, 1) - y) * (0.03 + 0.02 * sin(t * 0.9))
		a[i] = y * (0.8 + 0.4 * sin(t * TAU / 6.0))
	_fade_loop(a)
	return a


func _fade_loop(a: PackedFloat32Array) -> void:
	var n := 2000
	for i in n:
		var k := float(i) / n
		var j := a.size() - n + i
		a[j] = a[j] * (1.0 - k) + a[i] * k
