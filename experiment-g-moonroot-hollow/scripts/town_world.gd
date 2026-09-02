extends Node2D

const GEOMETRY_PATH := "res://data/town_geometry.json"
const STATE_FIND_APOTHECARY := "find_apothecary"
const STATE_SEEK_MOONWATER := "seek_moonwater"
const STATE_DELIVER_MOONWATER := "deliver_moonwater"
const STATE_COMPLETE := "complete"

var geometry: Dictionary = {}
var quest_state := STATE_FIND_APOTHECARY
var last_interaction := ""
var mutation := "none"
var boundary_points := PackedVector2Array()
var well_points := PackedVector2Array()


func _ready() -> void:
	geometry = JSON.parse_string(FileAccess.get_file_as_string(GEOMETRY_PATH))
	_configure_player()
	_build_collision()
	_update_interface("")


func _process(_delta: float) -> void:
	$Interface/InteractionPrompt.visible = not _nearby_landmark().is_empty()


func _unhandled_input(event: InputEvent) -> void:
	if event is InputEventKey and event.pressed and not event.echo:
		if event.keycode == KEY_E:
			try_interact()
		elif event.keycode == KEY_ESCAPE:
			get_tree().quit(0)


func apply_test_mutation(test_mutation: String) -> void:
	mutation = test_mutation
	match mutation:
		"corridor_blocker":
			_build_box_obstacle("MutationCorridorBlocker", Rect2(620, 720, 44, 135))
		"allow_early_well", "shift_apothecary_x180", "missing_completion", "", "none":
			pass
		_:
			push_error("Unknown test mutation: %s" % mutation)


func reset_quest_for_test() -> void:
	quest_state = STATE_FIND_APOTHECARY
	last_interaction = ""
	_update_interface("")


func try_interact() -> bool:
	var landmark := _nearby_landmark()
	last_interaction = landmark
	match landmark:
		"apothecary":
			if quest_state == STATE_FIND_APOTHECARY:
				quest_state = STATE_SEEK_MOONWATER
				_update_interface("Mora: The root arch sleeps. Bring me moonwater from the glowing well.")
				return true
			_update_interface("Mora watches the blue lanterns flicker.")
			return true
		"moonwell":
			if quest_state == STATE_SEEK_MOONWATER or mutation == "allow_early_well":
				quest_state = STATE_DELIVER_MOONWATER
				_update_interface("You gather a bright vial of moonwater.")
				return true
			_update_interface("The moonwell hums, but you do not yet know what to take.")
			return false
		"gatekeeper":
			if quest_state == STATE_DELIVER_MOONWATER:
				if mutation != "missing_completion":
					quest_state = STATE_COMPLETE
				_update_interface("Gatekeeper: The root remembers. Moonroot Hollow shines again.")
				return true
			_update_interface("Gatekeeper: The luminous arch is still sleeping.")
			return false
		_:
			_update_interface("")
			return false


func interaction_anchor(landmark: String) -> Vector2:
	var spec: Dictionary = geometry["quest_landmarks"][landmark]
	var anchor := Vector2(float(spec["interaction_anchor"][0]), float(spec["interaction_anchor"][1]))
	if landmark == "apothecary" and mutation == "shift_apothecary_x180":
		anchor.x += 180.0
	return anchor


func _nearby_landmark() -> String:
	for landmark in ["apothecary", "moonwell", "gatekeeper"]:
		var spec: Dictionary = geometry["quest_landmarks"][landmark]
		if $Player.global_position.distance_to(interaction_anchor(landmark)) <= float(spec["interaction_radius_px"]):
			return landmark
	return ""


func _update_interface(message: String) -> void:
	match quest_state:
		STATE_FIND_APOTHECARY:
			$Interface/Quest.text = "Quest: Speak with Mora at the left herb stall."
		STATE_SEEK_MOONWATER:
			$Interface/Quest.text = "Quest: Gather moonwater from the central glowing well."
		STATE_DELIVER_MOONWATER:
			$Interface/Quest.text = "Quest: Bring the moonwater to the antlered gatekeeper."
		STATE_COMPLETE:
			$Interface/Quest.text = "Quest complete: Moonroot Hollow shines again."
	$Interface/Message.text = message


func _configure_player() -> void:
	var spec: Dictionary = geometry["player"]
	$Player.position = Vector2(float(spec["spawn"][0]), float(spec["spawn"][1]))
	$Player.speed = float(spec["speed_px_per_second"])
	var feet := $Player/Feet.shape as CircleShape2D
	feet.radius = float(spec["foot_collider_radius_px"])


func _build_collision() -> void:
	boundary_points = _vectors(geometry["walkable_boundary"])
	var boundary := StaticBody2D.new()
	boundary.name = "TownBoundary"
	boundary.collision_layer = 1
	boundary.collision_mask = 1
	$CollisionGeometry.add_child(boundary)
	var boundary_collision := CollisionPolygon2D.new()
	boundary_collision.build_mode = CollisionPolygon2D.BUILD_SEGMENTS
	boundary_collision.polygon = boundary_points
	boundary.add_child(boundary_collision)
	_build_well(geometry["obstacles"][0])


func _build_well(spec: Dictionary) -> void:
	var center := Vector2(float(spec["center"][0]), float(spec["center"][1]))
	var radii := Vector2(float(spec["radii"][0]), float(spec["radii"][1]))
	well_points = PackedVector2Array()
	for index in range(int(spec["segments"])):
		var angle := TAU * float(index) / float(spec["segments"])
		well_points.append(center + Vector2(cos(angle) * radii.x, sin(angle) * radii.y))
	var body := StaticBody2D.new()
	body.name = String(spec["node_name"])
	body.collision_layer = 1
	body.collision_mask = 1
	$CollisionGeometry.add_child(body)
	var collision := CollisionPolygon2D.new()
	collision.polygon = well_points
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
