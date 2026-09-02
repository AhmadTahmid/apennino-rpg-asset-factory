extends Node2D

const MANIFEST_PATH := "res://data/world_manifest.json"
const SAVE_SCHEMA_VERSION := 1
const DEFAULT_SAVE_PATH := "user://moonroot_hollow_save.json"

const STATE_FIND_MORA := "find_mora"
const STATE_SEEK_MOONWATER := "seek_moonwater"
const STATE_DELIVER_MOONWATER := "deliver_moonwater"
const STATE_ENTER_LUMENWOOD := "enter_lumenwood"
const STATE_GATHER_STAR_SEED := "gather_star_seed"
const STATE_ENTER_SANCTUARY := "enter_sanctuary"
const STATE_RESTORE_HEARTROOT := "restore_heartroot"
const STATE_COMPLETE := "complete"

const VALID_STATES := [STATE_FIND_MORA, STATE_SEEK_MOONWATER, STATE_DELIVER_MOONWATER, STATE_ENTER_LUMENWOOD, STATE_GATHER_STAR_SEED, STATE_ENTER_SANCTUARY, STATE_RESTORE_HEARTROOT, STATE_COMPLETE]
const VALID_ITEMS := ["moonwater", "star_seed"]

var manifest: Dictionary = {}
var current_location := ""
var quest_state := STATE_FIND_MORA
var inventory: Array[String] = []
var last_interaction := ""
var mutation := "none"
var save_path := DEFAULT_SAVE_PATH
var boundary_points := PackedVector2Array()

@onready var background: Sprite2D = $Background
@onready var player: CharacterBody2D = $Player


func _ready() -> void:
	manifest = JSON.parse_string(FileAccess.get_file_as_string(MANIFEST_PATH))
	_configure_player()
	start_new_game(false)


func _process(_delta: float) -> void:
	$Interface/InteractionPrompt.visible = not nearby_interaction().is_empty() and quest_state != STATE_COMPLETE


func _unhandled_input(event: InputEvent) -> void:
	if event is InputEventKey and event.pressed and not event.echo:
		match event.keycode:
			KEY_E:
				try_interact()
			KEY_F5:
				save_game()
			KEY_F9:
				load_game()
			KEY_N:
				start_new_game(true)
			KEY_ESCAPE:
				get_tree().quit(0)


func start_new_game(show_message := true) -> void:
	quest_state = STATE_FIND_MORA
	inventory.clear()
	last_interaction = ""
	set_location(String(manifest["start_location"]))
	$Interface/Ending.visible = false
	_update_interface("A silver bell rings beneath the ancient tree." if show_message else "")


func set_location(location_id: String, position_override := Vector2.INF) -> bool:
	if not manifest["locations"].has(location_id):
		return false
	current_location = location_id
	var spec: Dictionary = manifest["locations"][location_id]
	background.texture = load(String(spec["art"]))
	_clear_collision()
	_build_collision(spec)
	var spawn := _vector(spec["spawn"])
	if position_override != Vector2.INF:
		spawn = position_override
	player.teleport_to(spawn, 0)
	if mutation == "wrong_forest_spawn" and location_id == "forest":
		player.teleport_to(Vector2(90, 90), 0)
	$Interface/Title.text = String(spec["name"])
	_update_interface("")
	return true


func apply_test_mutation(test_mutation: String) -> void:
	mutation = test_mutation
	if mutation == "forest_corridor_blocker" and current_location == "forest":
		_build_box_obstacle("MutationForestBlocker", Rect2(300, 570, 1070, 54))


func reset_for_test() -> void:
	mutation = "none"
	start_new_game(false)


func interaction_anchor(interaction_id: String, location_id := "") -> Vector2:
	var target_location := current_location if location_id.is_empty() else location_id
	var spec: Dictionary = manifest["locations"][target_location]["interactions"][interaction_id]
	return _vector(spec["anchor"])


func route(route_id: String, location_id := "") -> Array:
	var target_location := current_location if location_id.is_empty() else location_id
	return manifest["locations"][target_location]["tested_routes"][route_id]


func nearby_interaction() -> String:
	var interactions: Dictionary = manifest["locations"][current_location]["interactions"]
	for interaction_id in interactions:
		var spec: Dictionary = interactions[interaction_id]
		if player.global_position.distance_to(_vector(spec["anchor"])) <= float(spec["radius_px"]):
			return String(interaction_id)
	return ""


func try_interact() -> bool:
	var interaction_id := nearby_interaction()
	last_interaction = interaction_id
	match interaction_id:
		"apothecary":
			if quest_state == STATE_FIND_MORA:
				quest_state = STATE_SEEK_MOONWATER
				_update_interface("Mora: Bring moonwater to the antlered keeper. The forest has begun to forget.")
				return true
			_update_interface("Mora: The Heartroot waits beyond Lumenwood.")
			return true
		"moonwell":
			if quest_state == STATE_SEEK_MOONWATER:
				_add_item("moonwater")
				quest_state = STATE_DELIVER_MOONWATER
				_update_interface("You fill a small vial with singing moonwater.")
				return true
			_update_interface("The moonwell reflects a sky with one star missing.")
			return false
		"gatekeeper":
			if quest_state == STATE_DELIVER_MOONWATER and inventory.has("moonwater"):
				_remove_item("moonwater")
				quest_state = STATE_ENTER_LUMENWOOD
				_update_interface("Gatekeeper: The root arch remembers you. Press E again to cross.")
				return true
			if quest_state == STATE_ENTER_LUMENWOOD:
				quest_state = STATE_GATHER_STAR_SEED
				set_location("forest")
				_update_interface("Lumenwood opens. Find the star-seed that fell from the Heartroot.")
				return true
			_update_interface("Gatekeeper: Moonwater wakes the path. Bring it from the village well.")
			return false
		"star_seed":
			if quest_state == STATE_GATHER_STAR_SEED:
				if mutation != "missing_star_seed":
					_add_item("star_seed")
					quest_state = STATE_ENTER_SANCTUARY
				_update_interface("The star-seed is warm in your hands. Carry it through the upper root arch.")
				return mutation != "missing_star_seed"
			_update_interface("Only a shimmer remains among the violet leaves.")
			return false
		"moon_basin":
			_update_interface("The basin shows Moonroot Hollow safe beneath the silver tree.")
			return true
		"root_arch":
			if quest_state == STATE_ENTER_SANCTUARY or mutation == "portal_bypass":
				quest_state = STATE_RESTORE_HEARTROOT
				set_location("sanctuary")
				_update_interface("The Heartroot is silent. Return the fallen star to its empty cradle.")
				return true
			_update_interface("The arch is sealed by a star-shaped hollow.")
			return false
		"heartroot_altar":
			if quest_state == STATE_RESTORE_HEARTROOT and inventory.has("star_seed"):
				_remove_item("star_seed")
				if mutation != "missing_completion":
					quest_state = STATE_COMPLETE
					$Interface/Ending.visible = true
				_update_interface("Silver light races through every root. The valley breathes again.")
				return mutation != "missing_completion"
			_update_interface("The altar waits for the star-seed.")
			return false
		_:
			_update_interface("")
			return false


func save_game() -> bool:
	var payload := {
		"schema_version": SAVE_SCHEMA_VERSION,
		"location": current_location,
		"quest_state": quest_state,
		"inventory": inventory.duplicate(),
		"player_position": [player.global_position.x, player.global_position.y]
	}
	var file := FileAccess.open(save_path, FileAccess.WRITE)
	if file == null:
		_update_interface("The memory could not be written.")
		return false
	file.store_string(JSON.stringify(payload, "  "))
	file.close()
	_update_interface("Journey saved.")
	return true


func load_game() -> bool:
	if not FileAccess.file_exists(save_path):
		_update_interface("No saved journey was found.")
		return false
	var payload = JSON.parse_string(FileAccess.get_file_as_string(save_path))
	if not _valid_save(payload):
		_update_interface("The saved journey is invalid and was not loaded.")
		return false
	quest_state = String(payload["quest_state"])
	inventory.clear()
	for item in payload["inventory"]:
		inventory.append(String(item))
	var saved_position := _vector(payload["player_position"])
	if mutation == "save_state_drift":
		saved_position += Vector2(120, 0)
	set_location(String(payload["location"]), saved_position)
	$Interface/Ending.visible = quest_state == STATE_COMPLETE
	_update_interface("Journey restored.")
	return true


func _valid_save(payload) -> bool:
	if not payload is Dictionary:
		return false
	for key in ["schema_version", "location", "quest_state", "inventory", "player_position"]:
		if not payload.has(key):
			return false
	if int(payload["schema_version"]) != SAVE_SCHEMA_VERSION:
		return false
	if not manifest["locations"].has(String(payload["location"])) or not VALID_STATES.has(String(payload["quest_state"])):
		return false
	if not payload["inventory"] is Array or not payload["player_position"] is Array or payload["player_position"].size() != 2:
		return false
	for item in payload["inventory"]:
		if not VALID_ITEMS.has(String(item)):
			return false
	for coordinate in payload["player_position"]:
		if typeof(coordinate) not in [TYPE_INT, TYPE_FLOAT] or not is_finite(float(coordinate)):
			return false
	var location_id := String(payload["location"])
	var state := String(payload["quest_state"])
	var allowed_states_by_location := {
		"town": [STATE_FIND_MORA, STATE_SEEK_MOONWATER, STATE_DELIVER_MOONWATER, STATE_ENTER_LUMENWOOD],
		"forest": [STATE_GATHER_STAR_SEED, STATE_ENTER_SANCTUARY],
		"sanctuary": [STATE_RESTORE_HEARTROOT, STATE_COMPLETE]
	}
	if not allowed_states_by_location[location_id].has(state):
		return false
	var expected_items := []
	if state == STATE_DELIVER_MOONWATER:
		expected_items = ["moonwater"]
	elif state in [STATE_ENTER_SANCTUARY, STATE_RESTORE_HEARTROOT]:
		expected_items = ["star_seed"]
	if payload["inventory"] != expected_items:
		return false
	var location_spec: Dictionary = manifest["locations"][location_id]
	if not Geometry2D.is_point_in_polygon(_vector(payload["player_position"]), _vectors(location_spec["walkable_boundary"])):
		return false
	return true


func _update_interface(message: String) -> void:
	var objectives := {
		STATE_FIND_MORA: "Speak with Mora at the left herb stall.",
		STATE_SEEK_MOONWATER: "Gather moonwater from the village well.",
		STATE_DELIVER_MOONWATER: "Bring the moonwater to the antlered gatekeeper.",
		STATE_ENTER_LUMENWOOD: "Cross through the gatekeeper's awakened root arch.",
		STATE_GATHER_STAR_SEED: "Find the fallen star-seed in Lumenwood Crossing.",
		STATE_ENTER_SANCTUARY: "Carry the star-seed through the upper root arch.",
		STATE_RESTORE_HEARTROOT: "Place the star-seed in the Heartroot altar.",
		STATE_COMPLETE: "Complete — the Heartroot awakens. Press N to begin again."
	}
	$Interface/Quest.text = "Quest: " + String(objectives[quest_state])
	$Interface/Inventory.text = "Inventory: " + (", ".join(inventory) if not inventory.is_empty() else "empty")
	$Interface/Message.text = message


func _configure_player() -> void:
	var spec: Dictionary = manifest["player"]
	player.speed = float(spec["speed_px_per_second"])
	var feet := $Player/Feet.shape as CircleShape2D
	feet.radius = float(spec["foot_collider_radius_px"])
	$Player/Sprite.scale = _vector(spec["sprite_scale"])


func _clear_collision() -> void:
	for child in $CollisionGeometry.get_children():
		$CollisionGeometry.remove_child(child)
		child.free()


func _build_collision(spec: Dictionary) -> void:
	boundary_points = _vectors(spec["walkable_boundary"])
	var boundary := StaticBody2D.new()
	boundary.name = String(spec["name"]).replace(" ", "") + "Boundary"
	boundary.collision_layer = 1
	boundary.collision_mask = 1
	$CollisionGeometry.add_child(boundary)
	var boundary_collision := CollisionPolygon2D.new()
	boundary_collision.build_mode = CollisionPolygon2D.BUILD_SEGMENTS
	boundary_collision.polygon = boundary_points
	boundary.add_child(boundary_collision)
	for obstacle in spec["obstacles"]:
		_build_obstacle(obstacle)
	if mutation == "forest_corridor_blocker" and current_location == "forest":
		_build_box_obstacle("MutationForestBlocker", Rect2(300, 570, 1070, 54))


func _build_obstacle(spec: Dictionary) -> void:
	var points := PackedVector2Array()
	if String(spec["shape"]) == "ellipse":
		var center := _vector(spec["center"])
		var radii := _vector(spec["radii"])
		for index in range(int(spec["segments"])):
			var angle := TAU * float(index) / float(spec["segments"])
			points.append(center + Vector2(cos(angle) * radii.x, sin(angle) * radii.y))
	elif String(spec["shape"]) == "polygon":
		points = _vectors(spec["points"])
	var body := StaticBody2D.new()
	body.name = String(spec["node_name"])
	body.collision_layer = 1
	body.collision_mask = 1
	$CollisionGeometry.add_child(body)
	var collision := CollisionPolygon2D.new()
	collision.polygon = points
	body.add_child(collision)


func _build_box_obstacle(node_name: String, rect: Rect2) -> void:
	_build_obstacle({"node_name": node_name, "shape": "polygon", "points": [[rect.position.x, rect.position.y], [rect.end.x, rect.position.y], [rect.end.x, rect.end.y], [rect.position.x, rect.end.y]]})


func _add_item(item: String) -> void:
	if not inventory.has(item):
		inventory.append(item)


func _remove_item(item: String) -> void:
	inventory.erase(item)


func _vector(value: Array) -> Vector2:
	return Vector2(float(value[0]), float(value[1]))


func _vectors(values: Array) -> PackedVector2Array:
	var result := PackedVector2Array()
	for value in values:
		result.append(_vector(value))
	return result
