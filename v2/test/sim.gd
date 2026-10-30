extends Node
## Прогон расписаний на ускорении: -- --sim [seed] [игровых часов]

var w: Node


func _ready() -> void:
	var args: Array = get_meta("args")
	var seed_v := 4242 if args.size() < 2 else int(args[1])
	var hours := 4.0 if args.size() < 3 else float(args[2])
	var main := get_parent()
	w = load("res://src/world.gd").new()
	w.main = main
	w.case_seed = seed_v
	main.add_child(w)
	await get_tree().process_frame
	w.player.leave(true)
	w.player.density = 100000.0
	Engine.time_scale = 4.0
	var h0: float = w.env.hour
	var last := {}
	var stuck := {}
	var next_h := h0
	while w.env.hour < h0 + hours and not w.over:
		await get_tree().process_frame
		w.player.density = 100000.0
		for p in w.people:
			var k: Vector2 = p.global_position
			if last.has(p.pid) and (last[p.pid] as Vector2).distance_to(k) < 0.5 and p.brain and not p.brain.arrived and p.state == "ok" and not p.brain.away and p.brain.react.is_empty():
				stuck[p.pid] = stuck.get(p.pid, 0.0) + get_process_delta_time()
			else:
				stuck[p.pid] = 0.0
			last[p.pid] = k
		if w.env.hour >= next_h:
			next_h += 0.5
			var cnt := {}
			for p in w.people:
				var key: String = p.state
				if p.state == "ok":
					key = "away" if p.brain.away else (p.area.substr(0, 1) + ("✓" if p.brain.arrived else "…"))
				cnt[key] = cnt.get(key, 0) + 1
			var st := []
			for pid in stuck:
				if stuck[pid] > 6.0:
					var p = w.people[pid] if pid < w.people.size() else null
					if p:
						st.append("%s/%s@%s(%d,%d)->%s" % [p.prof, p.first, p.area, int(p.global_position.x), int(p.global_position.y), p.brain.goal.get("area", "?")])
			var shown := 0
			for p in w.people:
				if p.state == "ok" and p.area == "S" and not p.brain.arrived and not p.brain.away and shown < 4:
					shown += 1
					var r: Array = p.brain.route
					var nx := ""
					if p.brain.step < r.size():
						var e: Dictionary = r[p.brain.step]
						nx = "%s x=%d dir=%d" % [e["p"]["kind"], int(e["p"]["x"]), e["dir"]]
					print("   ", p.prof, " pos=", p.global_position.round(), " goal=", p.brain.goal.get("area", ""), " gx=", int(p.brain.goal.get("x", 0)), " route=", r.size(), " step=", p.brain.step, " next=", nx, " mx=", p.move_x, " v=", p.velocity.round(), " floor=", p.is_on_floor(), " react=", p.brain.react.get("kind", ""))
			var t = w.case.target
			print("%.2f %s | target %s %s goal=%s arrived=%s | stuck %d %s" % [w.env.hour, str(cnt), t.area, t.state, t.brain.goal.get("name", t.brain.goal.get("area", "")), t.brain.arrived, st.size(), str(st.slice(0, 6))])
	Engine.time_scale = 1.0
	get_tree().quit()
