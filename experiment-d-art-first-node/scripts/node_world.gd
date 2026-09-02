extends Node2D

const GEOMETRY_PATH := "res://data/node_001_geometry.json"

var geometry: Dictionary = {}
var debug_visible := false
var boundary_points := PackedVector2Array()
var fountain_points := PackedVector2Array()


func _ready() -> void:
	geometry = _load_geometry()
	boundary_points = _vectors(geometry["walkable_boundary"])
	_configure_player()
	_build_boundary()
	_build_fountain()
	queue_redraw()


func _unhandled_input(event: InputEvent) -> void:
	if event is InputEventKey and event.pressed and not event.echo:
		if event.keycode == KEY_F2:
			debug_visible = not debug_visible
			queue_redraw()
		elif event.keycode == KEY_ESCAPE:
			get_tree().quit(0)


func _draw() -> void:
	if not debug_visible:
		return
	draw_colored_polygon(boundary_points, Color(0.1, 0.8, 0.95, 0.16))
	draw_polyline(boundary_points + PackedVector2Array([boundary_points[0]]), Color(0.1, 0.9, 1.0, 0.95), 3.0)
	draw_colored_polygon(fountain_points, Color(1.0, 0.2, 0.25, 0.24))
	draw_polyline(fountain_points + PackedVector2Array([fountain_points[0]]), Color(1.0, 0.25, 0.25, 0.95), 3.0)
	var route: PackedVector2Array = _vectors(geometry["tested_route"]["waypoints"])
	draw_polyline(route, Color(1.0, 0.86, 0.15, 0.95), 3.0)
	for point in route:
		draw_circle(point, 6.0, Color(1.0, 0.86, 0.15, 1.0))


func apply_test_mutation(mutation: String) -> void:
	match mutation:
		"shift_fountain":
			get_node("CollisionGeometry/FountainBasin").position.x += 180.0
		"corridor_blocker":
			_build_box_obstacle("MutationCorridorBlocker", Rect2(875, 690, 34, 55))
		"", "none":
			pass
		_:
			push_error("Unknown test mutation: %s" % mutation)


func _load_geometry() -> Dictionary:
	var raw := FileAccess.get_file_as_string(GEOMETRY_PATH)
	var parsed = JSON.parse_string(raw)
	if not parsed is Dictionary:
		push_error("Invalid geometry JSON: %s" % GEOMETRY_PATH)
		return {}
	return parsed


func _configure_player() -> void:
	var spec: Dictionary = geometry["player"]
	$Player.position = Vector2(float(spec["spawn"][0]), float(spec["spawn"][1]))
	$Player.speed = float(spec["speed_px_per_second"])
	var feet_shape := $Player/Feet.shape as CircleShape2D
	feet_shape.radius = float(spec["foot_collider_radius_px"])


func _build_boundary() -> void:
	var body := StaticBody2D.new()
	body.name = "PlazaBoundary"
	body.collision_layer = 1
	body.collision_mask = 1
	$CollisionGeometry.add_child(body)
	var collision := CollisionPolygon2D.new()
	collision.name = "BoundarySegments"
	collision.build_mode = CollisionPolygon2D.BUILD_SEGMENTS
	collision.polygon = boundary_points
	body.add_child(collision)


func _build_fountain() -> void:
	var spec: Dictionary = geometry["obstacles"][0]
	var center := Vector2(float(spec["center"][0]), float(spec["center"][1]))
	var radii := Vector2(float(spec["radii"][0]), float(spec["radii"][1]))
	var segments := int(spec["segments"])
	fountain_points = PackedVector2Array()
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


func _vectors(values: Array) -> PackedVector2Array:
	var result := PackedVector2Array()
	for value in values:
		result.append(Vector2(float(value[0]), float(value[1])))
	return result
