extends Node2D

const PIAZZA_GEOMETRY_PATH := "res://data/node_001_geometry.json"
const BELVEDERE_GEOMETRY_PATH := "res://data/node_002_geometry.json"
const PIAZZA_PORTAL := Vector2(1095, 655)
const PIAZZA_PORTAL_RADIUS := 28.0
const PIAZZA_RETURN_SPAWN := Vector2(1070, 670)
const BELVEDERE_PORTAL := Vector2(836, 902)
const BELVEDERE_PORTAL_RADIUS := 28.0
const BELVEDERE_ARRIVAL := Vector2(836, 850)

var current_node_id := "piazza"
var geometries: Dictionary = {}
var boundary_points := PackedVector2Array()
var fountain_points := PackedVector2Array()
var debug_visible := false
var transition_log: Array[Dictionary] = []
var mutation := "none"


func _ready() -> void:
	geometries = {
		"piazza": _load_geometry(PIAZZA_GEOMETRY_PATH),
		"belvedere": _load_geometry(BELVEDERE_GEOMETRY_PATH)
	}
	_enter_node("piazza", Vector2(733, 675), 0, false)


func _process(_delta: float) -> void:
	var near_portal := is_player_near_current_portal()
	$Interface/PortalHint.visible = near_portal
	if near_portal:
		$Interface/PortalHint.text = "Press E: %s" % ("Belvedere" if current_node_id == "piazza" else "Return to piazza")


func _unhandled_input(event: InputEvent) -> void:
	if event is InputEventKey and event.pressed and not event.echo:
		if event.keycode == KEY_F2:
			debug_visible = not debug_visible
			queue_redraw()
		elif event.keycode == KEY_E:
			request_portal_transition()
		elif event.keycode == KEY_ESCAPE:
			get_tree().quit(0)


func _draw() -> void:
	if not debug_visible or boundary_points.is_empty():
		return
	draw_colored_polygon(boundary_points, Color(0.1, 0.8, 0.95, 0.16))
	draw_polyline(boundary_points + PackedVector2Array([boundary_points[0]]), Color(0.1, 0.9, 1.0, 0.95), 3.0)
	if not fountain_points.is_empty():
		draw_colored_polygon(fountain_points, Color(1.0, 0.2, 0.25, 0.24))
		draw_polyline(fountain_points + PackedVector2Array([fountain_points[0]]), Color(1.0, 0.25, 0.25, 0.95), 3.0)
	var geometry: Dictionary = geometries[current_node_id]
	var route: PackedVector2Array = _vectors(geometry["tested_route"]["waypoints"])
	draw_polyline(route, Color(1.0, 0.86, 0.15, 0.95), 3.0)
	for point in route:
		draw_circle(point, 6.0, Color(1.0, 0.86, 0.15, 1.0))
	var portal := _current_portal_anchor()
	draw_circle(portal, _current_portal_radius(), Color(1.0, 0.72, 0.12, 0.22))
	draw_arc(portal, _current_portal_radius(), 0.0, TAU, 48, Color(1.0, 0.72, 0.12, 1.0), 3.0)


func apply_test_mutation(test_mutation: String) -> void:
	mutation = test_mutation
	match mutation:
		"belvedere_corridor_blocker":
			pass
		"wrong_belvedere_spawn", "broken_return", "shift_piazza_portal_x100", "", "none":
			pass
		_:
			push_error("Unknown test mutation: %s" % mutation)


func is_player_near_current_portal() -> bool:
	return $Player.global_position.distance_to(_current_portal_anchor()) <= _current_portal_radius()


func request_portal_transition() -> bool:
	if not is_player_near_current_portal():
		return false
	if current_node_id == "piazza":
		var spawn := BELVEDERE_ARRIVAL
		if mutation == "wrong_belvedere_spawn":
			spawn += Vector2(140, 0)
		_enter_node("belvedere", spawn, 3, true)
		return true
	if mutation == "broken_return":
		return false
	_enter_node("piazza", PIAZZA_RETURN_SPAWN, 1, true)
	return true


func enter_node_for_test(node_id: String, spawn: Vector2, facing_row: int) -> void:
	_enter_node(node_id, spawn, facing_row, false)


func current_boundary_name() -> String:
	return "PiazzaBoundary" if current_node_id == "piazza" else "BelvedereBoundary"


func _enter_node(node_id: String, spawn: Vector2, facing_row: int, record_transition: bool) -> void:
	var previous := current_node_id
	current_node_id = node_id
	$PiazzaBackground.visible = node_id == "piazza"
	$BelvedereBackground.visible = node_id == "belvedere"
	$ForegroundOccluder.visible = node_id == "piazza"
	_rebuild_collision()
	$Player.teleport_to(spawn, facing_row)
	if record_transition:
		transition_log.append({
			"from": previous,
			"to": node_id,
			"spawn": [spawn.x, spawn.y],
			"physics_frame": Engine.get_physics_frames()
		})
	queue_redraw()


func _rebuild_collision() -> void:
	for child in $CollisionGeometry.get_children():
		child.free()
	var geometry: Dictionary = geometries[current_node_id]
	boundary_points = _vectors(geometry["walkable_boundary"])
	fountain_points = PackedVector2Array()
	var boundary := StaticBody2D.new()
	boundary.name = current_boundary_name()
	boundary.collision_layer = 1
	boundary.collision_mask = 1
	$CollisionGeometry.add_child(boundary)
	var boundary_collision := CollisionPolygon2D.new()
	boundary_collision.name = "BoundarySegments"
	boundary_collision.build_mode = CollisionPolygon2D.BUILD_SEGMENTS
	boundary_collision.polygon = boundary_points
	boundary.add_child(boundary_collision)
	if current_node_id == "piazza":
		_build_fountain(geometry["obstacles"][0])
	elif mutation == "belvedere_corridor_blocker":
		_build_box_obstacle("MutationBelvedereBlocker", Rect2(815, 760, 42, 110))


func _build_fountain(spec: Dictionary) -> void:
	var center := Vector2(float(spec["center"][0]), float(spec["center"][1]))
	var radii := Vector2(float(spec["radii"][0]), float(spec["radii"][1]))
	var segments := int(spec["segments"])
	for index in range(segments):
		var angle := TAU * float(index) / float(segments)
		fountain_points.append(center + Vector2(cos(angle) * radii.x, sin(angle) * radii.y))
	var body := StaticBody2D.new()
	body.name = String(spec["node_name"])
	body.collision_layer = 1
	body.collision_mask = 1
	$CollisionGeometry.add_child(body)
	var collision := CollisionPolygon2D.new()
	collision.name = "BasinPolygon"
	collision.polygon = fountain_points
	body.add_child(collision)


func _build_box_obstacle(node_name: String, rect: Rect2) -> void:
	var body := StaticBody2D.new()
	body.name = node_name
	body.collision_layer = 1
	body.collision_mask = 1
	$CollisionGeometry.add_child(body)
	var collision := CollisionPolygon2D.new()
	collision.polygon = PackedVector2Array([
		rect.position,
		Vector2(rect.end.x, rect.position.y),
		rect.end,
		Vector2(rect.position.x, rect.end.y)
	])
	body.add_child(collision)


func _current_portal_anchor() -> Vector2:
	if current_node_id == "piazza":
		return PIAZZA_PORTAL + (Vector2(100, 0) if mutation == "shift_piazza_portal_x100" else Vector2.ZERO)
	return BELVEDERE_PORTAL


func _current_portal_radius() -> float:
	return PIAZZA_PORTAL_RADIUS if current_node_id == "piazza" else BELVEDERE_PORTAL_RADIUS


func _load_geometry(path: String) -> Dictionary:
	var parsed = JSON.parse_string(FileAccess.get_file_as_string(path))
	if not parsed is Dictionary:
		push_error("Invalid geometry JSON: %s" % path)
		return {}
	return parsed


func _vectors(values: Array) -> PackedVector2Array:
	var result := PackedVector2Array()
	for value in values:
		result.append(Vector2(float(value[0]), float(value[1])))
	return result
