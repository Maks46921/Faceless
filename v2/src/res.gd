extends Node
## Ресурсы: атлас тайлов и TileSet, предметы, слои фигур, шрифты, текстуры света.

var tiles := {}            # имя -> Vector2i в атласе
var tileset: TileSet
var props := {}            # имя -> {tex, w, h, n}
var fig := {}              # слой -> Texture2D
var fig_frames := {}       # анимация -> PackedInt32Array
var fonts := {}
var light_tex: Texture2D
var light_soft: Texture2D
var fig_shader: Shader

const ALT_NONE := 0
const ALT_COMMON := 1
const ALT_INTERIOR := 2
const ALT_GRATE := 3
const ALT_PLATFORM := 4


func _ready() -> void:
	_load_fonts()
	_load_tiles()
	_load_props()
	_load_fig()
	_make_lights()
	fig_shader = load("res://shaders/figure.gdshader")


func _lines(path: String) -> PackedStringArray:
	var f := FileAccess.open(path, FileAccess.READ)
	if f == null:
		push_error("нет файла " + path)
		return PackedStringArray()
	var out := PackedStringArray()
	while not f.eof_reached():
		var l := f.get_line().strip_edges()
		if l != "":
			out.append(l)
	return out


func _load_fonts() -> void:
	for k in ["Oswald", "PT_Sans-Web-Bold", "Caveat", "PTM55FT", "PT_Serif-Web-Bold"]:
		fonts[k] = load("res://fonts/%s.ttf" % k)


func font(n: String) -> Font:
	return fonts.get(n, fonts["PT_Sans-Web-Bold"])


func _load_tiles() -> void:
	var tex: Texture2D = load("res://assets/tiles.png")
	for l in _lines("res://assets/tiles.txt"):
		var p := l.split(" ")
		tiles[p[0]] = Vector2i(int(p[1]), int(p[2]))
	tileset = TileSet.new()
	tileset.tile_size = Vector2i(K.T, K.T)
	var bits := [K.L_COMMON, K.L_INTERIOR, K.L_GRATE, K.L_PLATFORM]
	for i in bits.size():
		tileset.add_physics_layer()
		tileset.set_physics_layer_collision_layer(i, bits[i])
		tileset.set_physics_layer_collision_mask(i, 0)
	var src := TileSetAtlasSource.new()
	src.texture = tex
	src.texture_region_size = Vector2i(K.T, K.T)
	tileset.add_source(src, 0)
	var h := K.T / 2.0
	var sq := PackedVector2Array([Vector2(-h, -h), Vector2(h, -h), Vector2(h, h), Vector2(-h, h)])
	var top := PackedVector2Array([Vector2(-h, -h), Vector2(h, -h), Vector2(h, -h + 4), Vector2(-h, -h + 4)])
	for nm in tiles:
		var c: Vector2i = tiles[nm]
		src.create_tile(c)
		for layer in 4:
			var alt := src.create_alternative_tile(c)
			var td := src.get_tile_data(c, alt)
			td.add_collision_polygon(layer)
			td.set_collision_polygon_points(layer, 0, top if layer == 3 else sq)
			if layer == 3:
				td.set_collision_polygon_one_way(layer, 0, true)


func _load_props() -> void:
	for l in _lines("res://assets/props.txt"):
		var p := l.split(" ")
		props[p[0]] = {"tex": load("res://assets/props/%s.png" % p[0]), "w": int(p[1]), "h": int(p[2]), "n": int(p[3])}


func prop_sprite(nm: String, frame: int = 0) -> Sprite2D:
	## Спрайт предмета с опорой в середине нижнего края.
	var s := Sprite2D.new()
	if not props.has(nm):
		push_error("нет предмета " + nm)
		return s
	var d: Dictionary = props[nm]
	s.texture = d["tex"]
	s.hframes = int(d["n"])
	s.frame = frame
	s.centered = false
	s.offset = Vector2(-int(d["w"]) / 2, -int(d["h"]))
	return s


func prop_size(nm: String) -> Vector2:
	var d: Dictionary = props[nm]
	return Vector2(int(d["w"]), int(d["h"]))


func _load_fig() -> void:
	var dir := DirAccess.open("res://assets/fig")
	for f in dir.get_files():
		var nm := f.replace(".import", "")
		if nm.ends_with(".png"):
			var key := nm.trim_suffix(".png")
			if not fig.has(key):
				fig[key] = load("res://assets/fig/" + nm)
	for l in _lines("res://assets/fig/frames.txt"):
		var p := l.split(" ")
		var arr := PackedInt32Array()
		for s in p[1].split(","):
			arr.append(int(s))
		fig_frames[p[0]] = arr


func _make_lights() -> void:
	var g := Gradient.new()
	g.set_color(0, Color(1, 1, 1, 1))
	g.set_color(1, Color(1, 1, 1, 0))
	g.add_point(0.5, Color(1, 1, 1, 0.45))
	var t := GradientTexture2D.new()
	t.gradient = g
	t.fill = GradientTexture2D.FILL_RADIAL
	t.fill_from = Vector2(0.5, 0.5)
	t.fill_to = Vector2(1.0, 0.5)
	t.width = 128
	t.height = 128
	light_tex = t
	var g2 := Gradient.new()
	g2.set_color(0, Color(1, 1, 1, 1))
	g2.set_color(1, Color(1, 1, 1, 0))
	g2.add_point(0.7, Color(1, 1, 1, 0.8))
	var t2 := GradientTexture2D.new()
	t2.gradient = g2
	t2.fill = GradientTexture2D.FILL_SQUARE
	t2.fill_from = Vector2(0.5, 0.5)
	t2.fill_to = Vector2(1.0, 0.5)
	t2.width = 64
	t2.height = 64
	light_soft = t2
