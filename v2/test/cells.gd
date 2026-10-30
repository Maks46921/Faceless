extends Node

func _ready() -> void:
	var city := City.new()
	city.build(4242)
	add_child(city)
	await get_tree().physics_frame
	await get_tree().physics_frame
	for x in [1904, 2784, 4288, 4816, 816]:
		var c := int(x / 16)
		var line := ""
		for r in range(K.GY - 4, K.GY + 1):
			var s := ""
			for cc in range(c - 3, c + 4):
				var tc: TileMapLayer = city.tm_common
				var ti: TileMapLayer = city.tm_inner
				var a := tc.get_cell_source_id(Vector2i(cc, r)) >= 0
				var b := ti.get_cell_source_id(Vector2i(cc, r)) >= 0
				s += ("C" if a else ".") + ("I" if b else ".") + " "
			line += "r%d: %s\n" % [r, s]
		print("x=", x, " col ", c, " building ", city.building_at(float(x)).get("name", "?"), " kind ", city.building_at(float(x)).get("kind", "gap"))
		print(line)
		var sp := city.get_world_2d().direct_space_state
		var q := PhysicsRayQueryParameters2D.create(Vector2(x - 40, K.floor_y(0) - 10), Vector2(x + 40, K.floor_y(0) - 10), K.L_COMMON | K.L_GRATE | K.L_DOOR | K.L_PLATFORM)
		print(" hit: ", sp.intersect_ray(q))
	get_tree().quit()
