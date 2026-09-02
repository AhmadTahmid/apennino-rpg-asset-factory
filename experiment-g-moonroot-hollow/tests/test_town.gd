extends Node

const MAIN_SCENE := preload("res://scenes/main.tscn")
const TOWN_PATH := "res://assets/moonroot_hollow.png"
const TRAVELER_PATH := "res://assets/traveler_walk_sheet.png"
const GEOMETRY_PATH := "res://data/town_geometry.json"
const TOWN_HASH := "7B4DF1C2EB62D1E1C12893E5F9D4B3E3DF28249C5323F8C6D9C9294194D09674"
const TRAVELER_HASH := "4433340653530325DA27FE497E17226741B926404283383F1006FE7FE0FB6876"
const GEOMETRY_HASH := "E0A63D3F32BA02AD0E7FA8B1910913BD343260828DA0D5A634E69F74E9C11A98"
const SPAWN := Vector2(836, 860)
const WELL_CENTER := Vector2(842, 545)

var world: Node2D
var player: CharacterBody2D
var mutation := "none"
var results: Array[Dictionary] = []
var failure_count := 0


func _ready() -> void:
	mutation = _read_mutation()
	call_deferred("_run_suite")


func _run_suite() -> void:
	world = MAIN_SCENE.instantiate()
	add_child(world)
	player = world.get_node("Player")
	player.accept_manual_input = false
	await get_tree().physics_frame
	world.apply_test_mutation(mutation)
	await get_tree().physics_frame
	_test_asset_integrity()
	_test_visible_art_policy()
	_test_runtime_contract()
	_test_quest_order_contract()
	await _test_complete_quest_loop()
	await _test_well_collision()
	await _test_outer_boundary()
	_finish_suite()


func _test_asset_integrity() -> void:
	var actual := {
		"town": FileAccess.get_sha256(TOWN_PATH).to_upper(),
		"traveler": FileAccess.get_sha256(TRAVELER_PATH).to_upper(),
		"geometry": FileAccess.get_sha256(GEOMETRY_PATH).to_upper()
	}
	var expected := {"town": TOWN_HASH, "traveler": TRAVELER_HASH, "geometry": GEOMETRY_HASH}
	var town := Image.load_from_file(TOWN_PATH)
	var traveler := Image.load_from_file(TRAVELER_PATH)
	var passed := actual == expected and town.get_size() == Vector2i(1672, 941) and traveler.get_size() == Vector2i(144, 256)
	_record("asset_integrity", passed, {"actual_hashes": actual, "expected_hashes": expected, "town_size": town.get_size(), "traveler_size": traveler.get_size()})


func _test_visible_art_policy() -> void:
	var banned_types := ["ColorRect", "Polygon2D", "Line2D", "NinePatchRect"]
	var violations: Array[String] = []
	for node in _descendants(world):
		if banned_types.has(node.get_class()):
			violations.append("%s:%s" % [node.get_path(), node.get_class()])
	var sprite_paths := [
		String(world.get_node("Background").texture.resource_path),
		String(world.get_node("Player/Sprite").texture.resource_path)
	]
	var raster_only := true
	for path in sprite_paths:
		raster_only = raster_only and path.ends_with(".png")
	_record("visible_art_policy", violations.is_empty() and raster_only, {"banned_visible_node_violations": violations, "runtime_sprite_texture_paths": sprite_paths, "declared_policy": "all visible illustration is raster PNG; collision geometry is invisible"})


func _test_runtime_contract() -> void:
	var sprite := world.get_node("Player/Sprite") as Sprite2D
	var passed: bool = player.global_position.distance_to(SPAWN) <= 0.01
	passed = passed and sprite.scale.distance_to(Vector2(2, 2)) <= 0.001
	passed = passed and sprite.position.distance_to(Vector2(0, -64)) <= 0.01
	passed = passed and sprite.hframes == 3 and sprite.vframes == 4
	passed = passed and world.get_node_or_null("CollisionGeometry/TownBoundary") != null
	passed = passed and world.get_node_or_null("CollisionGeometry/MoonwellBasin") != null
	passed = passed and world.quest_state == "find_apothecary"
	_record("runtime_contract", passed, {"spawn": [player.global_position.x, player.global_position.y], "sprite_scale": [sprite.scale.x, sprite.scale.y], "sprite_position": [sprite.position.x, sprite.position.y], "quest_state": world.quest_state})


func _test_quest_order_contract() -> void:
	world.reset_quest_for_test()
	player.teleport_to(world.interaction_anchor("moonwell"), 3)
	var accepted: bool = world.try_interact()
	var passed: bool = not accepted and world.quest_state == "find_apothecary"
	_record("quest_order_contract", passed, {"accepted_before_apothecary": accepted, "quest_state_after_attempt": world.quest_state, "expected_state": "find_apothecary"})


func _test_complete_quest_loop() -> void:
	world.reset_quest_for_test()
	player.teleport_to(SPAWN, 3)
	await get_tree().physics_frame
	var geometry: Dictionary = world.geometry
	var route_evidence: Array = []
	var stage_evidence: Array = []
	var passed := true
	var stages := [
		{"route": "spawn_to_apothecary", "landmark": "apothecary", "expected_state": "seek_moonwater"},
		{"route": "apothecary_to_moonwell", "landmark": "moonwell", "expected_state": "deliver_moonwater"},
		{"route": "moonwell_to_gatekeeper", "landmark": "gatekeeper", "expected_state": "complete"}
	]
	for stage in stages:
		var legs: Array = []
		for value in geometry["tested_quest_route"][stage["route"]]:
			var waypoint := Vector2(float(value[0]), float(value[1]))
			var movement := await _run_command(waypoint, 3.0)
			legs.append(movement)
			if movement["outcome"] != "REACHED" or float(movement["target_error_px"]) > 5.0:
				passed = false
				break
		route_evidence.append({"route": stage["route"], "legs": legs})
		var accepted: bool = world.try_interact() if passed else false
		var state_matches: bool = world.quest_state == stage["expected_state"]
		stage_evidence.append({"landmark": stage["landmark"], "accepted": accepted, "actual_state": world.quest_state, "expected_state": stage["expected_state"], "last_interaction": world.last_interaction})
		passed = passed and accepted and state_matches and world.last_interaction == stage["landmark"]
		if not passed:
			break
	var quest_text: String = world.get_node("Interface/Quest").text
	passed = passed and world.quest_state == "complete" and quest_text.begins_with("Quest complete:")
	_record("complete_quest_loop", passed, {"routes": route_evidence, "stages": stage_evidence, "final_state": world.quest_state, "quest_text": quest_text})


func _test_well_collision() -> void:
	player.teleport_to(Vector2(842, 700), 3)
	await get_tree().physics_frame
	var movement := await _run_command(WELL_CENTER, 2.0)
	var passed: bool = movement["outcome"] == "BLOCKED" and movement["collider_name"] == "MoonwellBasin"
	_record("well_collision", passed, {"movement": movement, "expected_collider": "MoonwellBasin"})


func _test_outer_boundary() -> void:
	player.teleport_to(SPAWN, 0)
	await get_tree().physics_frame
	var movement := await _run_command(Vector2(836, 980), 2.0)
	var passed: bool = movement["outcome"] == "BLOCKED" and movement["collider_name"] == "TownBoundary"
	_record("outer_boundary", passed, {"movement": movement, "expected_collider": "TownBoundary"})


func _run_command(target: Vector2, timeout_seconds: float) -> Dictionary:
	player.command_move(target, timeout_seconds)
	while player.command_active:
		await get_tree().physics_frame
	return player.last_command_result


func _descendants(root: Node) -> Array[Node]:
	var nodes: Array[Node] = []
	for child in root.get_children():
		nodes.append(child)
		nodes.append_array(_descendants(child))
	return nodes


func _record(test_name: String, passed: bool, evidence: Dictionary) -> void:
	results.append({"test": test_name, "status": "PASS" if passed else "FAIL", "evidence": evidence})
	if passed:
		print("[PASS] %s" % test_name)
	else:
		failure_count += 1
		printerr("[FAIL] %s | %s" % [test_name, JSON.stringify(evidence)])


func _finish_suite() -> void:
	var payload := {
		"experiment": "experiment_g_moonroot_hollow",
		"mutation": mutation,
		"godot_version": Engine.get_version_info().get("string", "unknown"),
		"timestamp_utc": Time.get_datetime_string_from_system(true, true),
		"passed": failure_count == 0,
		"failure_count": failure_count,
		"source_hashes": {
			"town": FileAccess.get_sha256(TOWN_PATH).to_upper(),
			"traveler": FileAccess.get_sha256(TRAVELER_PATH).to_upper(),
			"geometry": FileAccess.get_sha256(GEOMETRY_PATH).to_upper(),
			"world_script": FileAccess.get_sha256("res://scripts/town_world.gd").to_upper(),
			"player_script": FileAccess.get_sha256("res://scripts/player_controller.gd").to_upper(),
			"test_script": FileAccess.get_sha256("res://tests/test_town.gd").to_upper(),
			"main_scene": FileAccess.get_sha256("res://scenes/main.tscn").to_upper()
		},
		"results": results
	}
	var suffix := "" if mutation == "none" else "_" + mutation
	var file := FileAccess.open("res://diagnostics/test_results%s.json" % suffix, FileAccess.WRITE)
	if file:
		file.store_string(JSON.stringify(payload, "  "))
		file.close()
	print("TEST_SUMMARY passed=%s failures=%s mutation=%s" % [payload.passed, failure_count, mutation])
	get_tree().quit(0 if failure_count == 0 else 1)


func _read_mutation() -> String:
	for argument in OS.get_cmdline_user_args():
		if argument.begins_with("--mutation="):
			return argument.trim_prefix("--mutation=")
	return "none"
