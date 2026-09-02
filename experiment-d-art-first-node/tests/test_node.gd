extends Node

const MAIN_SCENE := preload("res://scenes/main.tscn")
const ART_HASH := "FD11B82DEAD94E5BF5CB30F9DD9F718C84C5D9D5AAFD8170483FA222B5CBB54F"
const PLAYER_HASH := "21B0086C676A466196D97E72889D13940BE62922A5439624C2605ECE68157102"
const SPAWN := Vector2(733, 675)
const FOUNTAIN_CENTER := Vector2(894, 612)
const FOUNTAIN_RADII := Vector2(122, 82)
var outbound_route := PackedVector2Array([
	Vector2(669, 640),
	Vector2(760, 705),
	Vector2(888, 720),
	Vector2(1020, 700),
	Vector2(1095, 655)
])
var return_route := PackedVector2Array([
	Vector2(1020, 700),
	Vector2(888, 720),
	Vector2(760, 705),
	SPAWN
])

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
	await _test_collision_probes()
	await _test_fountain_blocking()
	await _test_lower_court_outbound()
	await _test_lower_court_return()
	await _test_outer_boundary()
	_finish_suite()


func _test_asset_integrity() -> void:
	var art_hash := FileAccess.get_sha256("res://assets/control_01.png").to_upper()
	var player_hash := FileAccess.get_sha256("res://assets/player.png").to_upper()
	var art_texture: Texture2D = load("res://assets/control_01.png")
	var art_size := Vector2i(art_texture.get_size())
	var checks_pass := art_hash == ART_HASH and player_hash == PLAYER_HASH and art_size == Vector2i(1672, 941)
	_record(
		"asset_integrity",
		checks_pass,
		{
			"art_hash": art_hash,
			"expected_art_hash": ART_HASH,
			"player_hash": player_hash,
			"expected_player_hash": PLAYER_HASH,
			"art_dimensions": [art_size.x, art_size.y],
			"expected_dimensions": [1672, 941]
		}
	)


func _test_collision_probes() -> void:
	var open_points := [SPAWN, Vector2(669, 640), Vector2(1095, 655), Vector2(888, 720)]
	var unexpected: Array = []
	for point in open_points:
		var names := _colliders_at(point)
		if not names.is_empty():
			unexpected.append({"point": [point.x, point.y], "colliders": names})
	var fountain_hits := _colliders_at(FOUNTAIN_CENTER)
	var passed: bool = unexpected.is_empty() and fountain_hits.has("FountainBasin")
	_record(
		"collision_probe_contract",
		passed,
		{
			"unexpected_open_point_colliders": unexpected,
			"fountain_center_colliders": fountain_hits,
			"expected_fountain_collider": "FountainBasin"
		}
	)


func _test_fountain_blocking() -> void:
	player.reset_for_test(Vector2(735, 640))
	await get_tree().physics_frame
	var result := await _run_command(FOUNTAIN_CENTER, 2.0)
	var final_pos := Vector2(float(result["final_position"][0]), float(result["final_position"][1]))
	var normalized := Vector2(
		(final_pos.x - FOUNTAIN_CENTER.x) / FOUNTAIN_RADII.x,
		(final_pos.y - FOUNTAIN_CENTER.y) / FOUNTAIN_RADII.y
	).length()
	var passed: bool = result["outcome"] == "BLOCKED" and result["collider_name"] == "FountainBasin" and int(result["slide_collision_count"]) > 0 and normalized >= 0.98
	_record(
		"fountain_blocking",
		passed,
		{"movement": result, "normalized_final_distance": normalized, "minimum_expected": 0.98}
	)


func _test_lower_court_outbound() -> void:
	player.reset_for_test(SPAWN)
	await get_tree().physics_frame
	var legs: Array = []
	var passed := true
	for waypoint in outbound_route:
		var result := await _run_command(waypoint, 3.0)
		legs.append(result)
		if result["outcome"] != "REACHED" or float(result["target_error_px"]) > 4.0 or int(result["slide_collision_count"]) != 0:
			passed = false
			break
	var destination_error := player.global_position.distance_to(outbound_route[-1])
	passed = passed and destination_error <= 6.0
	_record(
		"lower_court_outbound",
		passed,
		{
			"legs": legs,
			"destination_error_px": destination_error,
			"maximum_destination_error_px": 6.0
		}
	)


func _test_lower_court_return() -> void:
	player.reset_for_test(outbound_route[-1])
	await get_tree().physics_frame
	var legs: Array = []
	var passed := true
	for waypoint in return_route:
		var result := await _run_command(waypoint, 3.0)
		legs.append(result)
		if result["outcome"] != "REACHED" or float(result["target_error_px"]) > 4.0 or int(result["slide_collision_count"]) != 0:
			passed = false
			break
	var return_error := player.global_position.distance_to(SPAWN)
	passed = passed and return_error <= 6.0
	_record(
		"lower_court_return",
		passed,
		{"legs": legs, "return_error_px": return_error, "maximum_return_error_px": 6.0}
	)


func _test_outer_boundary() -> void:
	player.reset_for_test(SPAWN)
	await get_tree().physics_frame
	var result := await _run_command(Vector2(560, 720), 2.0)
	var passed: bool = result["outcome"] == "BLOCKED" and result["collider_name"] == "PlazaBoundary" and int(result["slide_collision_count"]) > 0
	_record(
		"outer_boundary",
		passed,
		{"movement": result, "expected_collider": "PlazaBoundary"}
	)


func _run_command(target: Vector2, timeout_seconds: float) -> Dictionary:
	player.command_move(target, timeout_seconds)
	while player.command_active:
		await get_tree().physics_frame
	return player.last_command_result


func _colliders_at(point: Vector2) -> Array[String]:
	var query := PhysicsPointQueryParameters2D.new()
	query.position = point
	query.collision_mask = 1
	query.collide_with_bodies = true
	query.exclude = [player.get_rid()]
	var hits := get_viewport().world_2d.direct_space_state.intersect_point(query, 16)
	var names: Array[String] = []
	for hit in hits:
		if hit["collider"] is Node:
			names.append(String(hit["collider"].name))
	return names


func _record(test_name: String, passed: bool, evidence: Dictionary) -> void:
	var status := "PASS" if passed else "FAIL"
	results.append({"test": test_name, "status": status, "evidence": evidence})
	if passed:
		print("[PASS] %s | %s" % [test_name, JSON.stringify(evidence)])
	else:
		failure_count += 1
		printerr("[FAIL] %s | %s" % [test_name, JSON.stringify(evidence)])


func _finish_suite() -> void:
	var payload := {
		"experiment": "experiment_d_art_first_node",
		"mutation": mutation,
		"godot_version": Engine.get_version_info().get("string", "unknown"),
		"timestamp_utc": Time.get_datetime_string_from_system(true, true),
		"passed": failure_count == 0,
		"failure_count": failure_count,
		"source_hashes": {
			"geometry": FileAccess.get_sha256("res://data/node_001_geometry.json").to_upper(),
			"world_script": FileAccess.get_sha256("res://scripts/node_world.gd").to_upper(),
			"player_script": FileAccess.get_sha256("res://scripts/player_controller.gd").to_upper(),
			"test_script": FileAccess.get_sha256("res://tests/test_node.gd").to_upper(),
			"main_scene": FileAccess.get_sha256("res://scenes/main.tscn").to_upper()
		},
		"results": results
	}
	var suffix := "" if mutation == "none" else "_" + mutation
	var path := "res://diagnostics/test_results%s.json" % suffix
	var file := FileAccess.open(path, FileAccess.WRITE)
	if file:
		file.store_string(JSON.stringify(payload, "  "))
		file.close()
	print("TEST_SUMMARY %s" % JSON.stringify(payload))
	get_tree().quit(0 if failure_count == 0 else 1)


func _read_mutation() -> String:
	for argument in OS.get_cmdline_user_args():
		if argument.begins_with("--mutation="):
			return argument.trim_prefix("--mutation=")
	return "none"
