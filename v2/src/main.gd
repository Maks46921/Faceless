extends Node
## Корень: меню, брифинг, игра, итог. Тесты запускаются ключами после «--».

var current: Node


func _ready() -> void:
	var args := OS.get_cmdline_user_args()
	if "--autostart" in args:
		start_game(1234)
		return
	if args.size() > 0 and args[0].begins_with("--"):
		var path := "res://test/%s.gd" % args[0].substr(2)
		if ResourceLoader.exists(path):
			var t: Node = load(path).new()
			t.set_meta("args", args)
			add_child(t)
			return
	show_menu()


func _swap(n: Node) -> void:
	if current and is_instance_valid(current):
		current.queue_free()
	current = n
	add_child(n)


func show_menu() -> void:
	get_tree().paused = false
	var m: Control = load("res://src/ui/menu.gd").new()
	m.main = self
	_swap(m)


func show_brief(case_seed: int) -> void:
	## Папка куратора открывается поверх уже собранного района (игра на паузе).
	start_game(case_seed, true)


func start_game(case_seed: int, brief: bool = false) -> Node:
	get_tree().paused = false
	var w: Node = load("res://src/world.gd").new()
	w.main = self
	w.case_seed = case_seed
	w.brief = brief
	_swap(w)
	return w


func show_result(res: Dictionary) -> void:
	get_tree().paused = false
	var r: Control = load("res://src/ui/result.gd").new()
	r.main = self
	r.res = res
	_swap(r)
