extends Node

const MAIN_SCENE := preload("res://scenes/main.tscn")

const PIAZZA_ART_PATH := "res://assets/piazza.png"
const BELVEDERE_ART_PATH := "res://assets/belvedere.png"
const ATLAS_PATH := "res://assets/traveler_walk_sheet.png"
const FOREGROUND_PATH := "res://assets/southwest_planter_foreground.png"
const PIAZZA_GEOMETRY_PATH := "res://data/node_001_geometry.json"
const BELVEDERE_GEOMETRY_PATH := "res://data/node_002_geometry.json"

const PIAZZA_ART_HASH := "FD11B82DEAD94E5BF5CB30F9DD9F718C84C5D9D5AAFD8170483FA222B5CBB54F"
const BELVEDERE_ART_HASH := "812AF962D4D567F99B474D9CAC328FCF2E176A973226C3FC3694D08177A992BA"
const ATLAS_HASH := "4433340653530325DA27FE497E17226741B926404283383F1006FE7FE0FB6876"
const FOREGROUND_HASH := "7A59A290EA28117E6DF18EBDC26AF6B5D801BE120A50B7F7098BBECBE48C7895"
const PIAZZA_GEOMETRY_HASH := "DF0924A62B4216268C7152070644BBDC9635CF19A4693A2290003C5D6C38CAF4"
const BELVEDERE_GEOMETRY_HASH := "02E836B1068E9B398189EA79097B02F3D8EC82AD1022E7E882230C0B0D50BCC4"

const PIAZZA_SPAWN := Vector2(733, 675)
const PIAZZA_PORTAL := Vector2(1095, 655)
const PIAZZA_RETURN_SPAWN := Vector2(1070, 670)
const BELVEDERE_ARRIVAL := Vector2(836, 850)
const BELVEDERE_PORTAL := Vector2(836, 902)

var piazza_route := PackedVector2Array([
	Vector2(669, 640),
	Vector2(760, 705),
	Vector2(888, 720),
	Vector2(1020, 700),
	PIAZZA_PORTAL
])
var belvedere_route := PackedVector2Array([
	Vector2(650, 820),
	Vector2(560, 780),
	Vector2(680, 735),
	Vector2(836, 720),
	Vector2(1000, 750),
	Vector2(1120, 800),
	Vector2(1020, 845),
	BELVEDERE_ARRIVAL,
	BELVEDERE_PORTAL
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
	await _test_node_001_regression()
	_test_portal_gating()
	await _test_piazza_route_to_portal()
	await _test_transition_to_belvedere()
	await _test_belvedere_route()
	await _test_belvedere_boundary()
	await _test_round_trip_return()
	_finish_suite()


func _test_asset_integrity() -> void:
	var actual_hashes := {
		"piazza_art": FileAccess.get_sha256(PIAZZA_ART_PATH).to_upper(),
		"belvedere_art": FileAccess.get_sha256(BELVEDERE_ART_PATH).to_upper(),
		"atlas": FileAccess.get_sha256(ATLAS_PATH).to_upper(),
		"foreground": FileAccess.get_sha256(FOREGROUND_PATH).to_upper(),
		"piazza_geometry": FileAccess.get_sha256(PIAZZA_GEOMETRY_PATH).to_upper(),
		"belvedere_geometry": FileAccess.get_sha256(BELVEDERE_GEOMETRY_PATH).to_upper()
	}
	var expected_hashes := {
		"piazza_art": PIAZZA_ART_HASH,
		"belvedere_art": BELVEDERE_ART_HASH,
		"atlas": ATLAS_HASH,
		"foreground": FOREGROUND_HASH,
		"piazza_geometry": PIAZZA_GEOMETRY_HASH,
		"belvedere_geometry": BELVEDERE_GEOMETRY_HASH
	}
	var dimensions := {
		"piazza": Image.load_from_file(PIAZZA_ART_PATH).get_size(),
		"belvedere": Image.load_from_file(BELVEDERE_ART_PATH).get_size(),
		"atlas": Image.load_from_file(ATLAS_PATH).get_size(),
		"foreground": Image.load_from_file(FOREGROUND_PATH).get_size()
	}
	var passed := actual_hashes == expected_hashes
	passed = passed and dimensions["piazza"] == Vector2i(1672, 941)
	passed = passed and dimensions["belvedere"] == Vector2i(1672, 941)
	passed = passed and dimensions["atlas"] == Vector2i(144, 256)
	passed = passed and dimensions["foreground"] == Vector2i(1672, 941)
	_record("asset_integrity", passed, {"actual_hashes": actual_hashes, "expected_hashes": expected_hashes, "dimensions": dimensions})


func _test_node_001_regression() -> void:
	world.enter_node_for_test("piazza", PIAZZA_SPAWN, 0)
	await get_tree().physics_frame
	var state_passed: bool = world.current_node_id == "piazza"
	state_passed = state_passed and world.get_node("PiazzaBackground").visible
	state_passed = state_passed and not world.get_node("BelvedereBackground").visible
	state_passed = state_passed and world.get_node("ForegroundOccluder").visible
	state_passed = state_passed and player.global_position.distance_to(PIAZZA_SPAWN) <= 0.01
	state_passed = state_passed and world.get_node("CollisionGeometry/PiazzaBoundary") != null
	state_passed = state_passed and world.get_node("CollisionGeometry/FountainBasin") != null
	player.reset_for_test(Vector2(735, 640))
	await get_tree().physics_frame
	var movement := await _run_command(Vector2(894, 612), 2.0)
	var collision_passed: bool = movement["outcome"] == "BLOCKED" and movement["collider_name"] == "FountainBasin"
	_record("node_001_regression", state_passed and collision_passed, {"state_passed": state_passed, "fountain_movement": movement, "geometry_sha256": FileAccess.get_sha256(PIAZZA_GEOMETRY_PATH).to_upper()})


func _test_portal_gating() -> void:
	world.enter_node_for_test("piazza", PIAZZA_SPAWN, 0)
	player.global_position = PIAZZA_SPAWN
	var far_rejected: bool = not world.is_player_near_current_portal() and not world.request_portal_transition()
	player.global_position = PIAZZA_PORTAL
	var expected_anchor_active: bool = world.is_player_near_current_portal()
	_record("portal_gating", far_rejected and expected_anchor_active, {"far_rejected": far_rejected, "expected_anchor_active": expected_anchor_active, "declared_anchor": [PIAZZA_PORTAL.x, PIAZZA_PORTAL.y], "mutation": mutation})


func _test_piazza_route_to_portal() -> void:
	world.enter_node_for_test("piazza", PIAZZA_SPAWN, 0)
	await get_tree().physics_frame
	var legs: Array = []
	var passed := true
	for waypoint in piazza_route:
		var movement := await _run_command(waypoint, 3.0)
		legs.append(movement)
		if movement["outcome"] != "REACHED" or float(movement["target_error_px"]) > 4.0:
			passed = false
			break
	passed = passed and player.global_position.distance_to(PIAZZA_PORTAL) <= 6.0
	_record("piazza_route_to_portal", passed, {"legs": legs, "destination_error_px": player.global_position.distance_to(PIAZZA_PORTAL)})


func _test_transition_to_belvedere() -> void:
	world.enter_node_for_test("piazza", PIAZZA_SPAWN, 0)
	await get_tree().physics_frame
	player.global_position = world._current_portal_anchor()
	var accepted: bool = world.request_portal_transition()
	await get_tree().physics_frame
	var passed: bool = accepted and world.current_node_id == "belvedere"
	passed = passed and world.get_node("BelvedereBackground").visible
	passed = passed and not world.get_node("PiazzaBackground").visible
	passed = passed and not world.get_node("ForegroundOccluder").visible
	passed = passed and world.get_node_or_null("CollisionGeometry/BelvedereBoundary") != null
	passed = passed and world.get_node_or_null("CollisionGeometry/FountainBasin") == null
	passed = passed and player.global_position.distance_to(BELVEDERE_ARRIVAL) <= 0.01
	_record("transition_to_belvedere", passed, {"accepted": accepted, "current_node": world.current_node_id, "actual_spawn": [player.global_position.x, player.global_position.y], "expected_spawn": [BELVEDERE_ARRIVAL.x, BELVEDERE_ARRIVAL.y], "piazza_visible": world.get_node("PiazzaBackground").visible, "belvedere_visible": world.get_node("BelvedereBackground").visible, "foreground_visible": world.get_node("ForegroundOccluder").visible})


func _test_belvedere_route() -> void:
	world.enter_node_for_test("belvedere", BELVEDERE_ARRIVAL, 3)
	await get_tree().physics_frame
	var legs: Array = []
	var passed := true
	for waypoint in belvedere_route:
		var movement := await _run_command(waypoint, 3.0)
		legs.append(movement)
		if movement["outcome"] != "REACHED" or float(movement["target_error_px"]) > 4.0:
			passed = false
			break
	passed = passed and player.global_position.distance_to(BELVEDERE_PORTAL) <= 6.0
	_record("belvedere_route", passed, {"legs": legs, "destination_error_px": player.global_position.distance_to(BELVEDERE_PORTAL)})


func _test_belvedere_boundary() -> void:
	world.enter_node_for_test("belvedere", Vector2(836, 720), 3)
	await get_tree().physics_frame
	var movement := await _run_command(Vector2(836, 620), 2.0)
	var passed: bool = movement["outcome"] == "BLOCKED" and movement["collider_name"] == "BelvedereBoundary"
	_record("belvedere_boundary", passed, {"movement": movement, "expected_collider": "BelvedereBoundary"})


func _test_round_trip_return() -> void:
	world.enter_node_for_test("belvedere", BELVEDERE_PORTAL, 0)
	await get_tree().physics_frame
	var log_before: int = world.transition_log.size()
	var accepted: bool = world.request_portal_transition()
	await get_tree().physics_frame
	var log_after: int = world.transition_log.size()
	var passed: bool = accepted and world.current_node_id == "piazza"
	passed = passed and world.get_node("PiazzaBackground").visible
	passed = passed and not world.get_node("BelvedereBackground").visible
	passed = passed and world.get_node("ForegroundOccluder").visible
	passed = passed and player.global_position.distance_to(PIAZZA_RETURN_SPAWN) <= 0.01
	passed = passed and log_after == log_before + 1
	var last_transition: Dictionary = world.transition_log[-1] if not world.transition_log.is_empty() else {}
	passed = passed and last_transition.get("from", "") == "belvedere" and last_transition.get("to", "") == "piazza"
	_record("round_trip_return", passed, {"accepted": accepted, "current_node": world.current_node_id, "actual_spawn": [player.global_position.x, player.global_position.y], "expected_spawn": [PIAZZA_RETURN_SPAWN.x, PIAZZA_RETURN_SPAWN.y], "log_before": log_before, "log_after": log_after, "last_transition": last_transition})


func _run_command(target: Vector2, timeout_seconds: float) -> Dictionary:
	player.command_move(target, timeout_seconds)
	while player.command_active:
		await get_tree().physics_frame
	return player.last_command_result


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
		"experiment": "experiment_f_connected_belvedere",
		"mutation": mutation,
		"godot_version": Engine.get_version_info().get("string", "unknown"),
		"timestamp_utc": Time.get_datetime_string_from_system(true, true),
		"passed": failure_count == 0,
		"failure_count": failure_count,
		"source_hashes": {
			"piazza_art": FileAccess.get_sha256(PIAZZA_ART_PATH).to_upper(),
			"belvedere_art": FileAccess.get_sha256(BELVEDERE_ART_PATH).to_upper(),
			"atlas": FileAccess.get_sha256(ATLAS_PATH).to_upper(),
			"foreground": FileAccess.get_sha256(FOREGROUND_PATH).to_upper(),
			"piazza_geometry": FileAccess.get_sha256(PIAZZA_GEOMETRY_PATH).to_upper(),
			"belvedere_geometry": FileAccess.get_sha256(BELVEDERE_GEOMETRY_PATH).to_upper(),
			"world_script": FileAccess.get_sha256("res://scripts/node_world.gd").to_upper(),
			"player_script": FileAccess.get_sha256("res://scripts/player_controller.gd").to_upper(),
			"test_script": FileAccess.get_sha256("res://tests/test_node.gd").to_upper(),
			"main_scene": FileAccess.get_sha256("res://scenes/main.tscn").to_upper()
		},
		"results": results
	}
	var suffix := "" if mutation == "none" else "_" + mutation
	var file := FileAccess.open("res://diagnostics/test_results%s.json" % suffix, FileAccess.WRITE)
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
