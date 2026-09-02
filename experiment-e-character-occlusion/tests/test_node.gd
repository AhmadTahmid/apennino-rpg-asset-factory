extends Node

const MAIN_SCENE := preload("res://scenes/main.tscn")

const ART_HASH := "FD11B82DEAD94E5BF5CB30F9DD9F718C84C5D9D5AAFD8170483FA222B5CBB54F"
const ATLAS_HASH := "4433340653530325DA27FE497E17226741B926404283383F1006FE7FE0FB6876"
const MASK_HASH := "E57567DF8FD4B9C30AEB8D8452E5F28FD62053AB906330B9D2E04486B9AD5C91"
const FOREGROUND_HASH := "7A59A290EA28117E6DF18EBDC26AF6B5D801BE120A50B7F7098BBECBE48C7895"
const GEOMETRY_HASH := "DF0924A62B4216268C7152070644BBDC9635CF19A4693A2290003C5D6C38CAF4"

const ART_PATH := "res://assets/control_01.png"
const ATLAS_PATH := "res://assets/traveler_walk_sheet.png"
const MASK_PATH := "res://assets/southwest_planter_mask.png"
const FOREGROUND_PATH := "res://assets/southwest_planter_foreground.png"
const GEOMETRY_PATH := "res://data/node_001_geometry.json"

const ART_SIZE := Vector2i(1672, 941)
const ATLAS_SIZE := Vector2i(144, 256)
const FRAME_SIZE := Vector2i(48, 64)
const EXPECTED_FOREGROUND_ALPHA_PIXELS := 2072
const OCCLUSION_POSE := Vector2(704, 675)

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
var player_sprite: Sprite2D
var foreground: Sprite2D
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
	player_sprite = world.get_node("Player/Sprite")
	foreground = world.get_node_or_null("ForegroundOccluder") as Sprite2D
	player.accept_manual_input = false
	await get_tree().physics_frame
	world.apply_test_mutation(mutation)
	await get_tree().physics_frame

	_test_asset_integrity()
	_test_atlas_integrity()
	await _test_direction_mapping()
	await _test_temporal_animation()
	_test_foreground_asset_contract()
	_test_foreground_transform_contract()
	_test_occlusion_state_contract()
	await _test_collision_probes()
	await _test_fountain_blocking()
	await _test_lower_court_outbound()
	await _test_lower_court_return()
	await _test_outer_boundary()
	_finish_suite()


func _test_asset_integrity() -> void:
	var actual_hashes := {
		"scene_art": FileAccess.get_sha256(ART_PATH).to_upper(),
		"atlas": FileAccess.get_sha256(ATLAS_PATH).to_upper(),
		"mask": FileAccess.get_sha256(MASK_PATH).to_upper(),
		"foreground": FileAccess.get_sha256(FOREGROUND_PATH).to_upper(),
		"geometry": FileAccess.get_sha256(GEOMETRY_PATH).to_upper()
	}
	var expected_hashes := {
		"scene_art": ART_HASH,
		"atlas": ATLAS_HASH,
		"mask": MASK_HASH,
		"foreground": FOREGROUND_HASH,
		"geometry": GEOMETRY_HASH
	}
	var art := Image.load_from_file(ART_PATH)
	var atlas := Image.load_from_file(ATLAS_PATH)
	var mask := Image.load_from_file(MASK_PATH)
	var foreground_image := Image.load_from_file(FOREGROUND_PATH)
	var actual_dimensions := {
		"scene_art": [art.get_width(), art.get_height()],
		"atlas": [atlas.get_width(), atlas.get_height()],
		"mask": [mask.get_width(), mask.get_height()],
		"foreground": [foreground_image.get_width(), foreground_image.get_height()]
	}
	var passed := actual_hashes == expected_hashes
	passed = passed and art.get_size() == ART_SIZE
	passed = passed and atlas.get_size() == ATLAS_SIZE
	passed = passed and mask.get_size() == ART_SIZE
	passed = passed and foreground_image.get_size() == ART_SIZE
	_record(
		"asset_integrity",
		passed,
		{
			"actual_hashes": actual_hashes,
			"expected_hashes": expected_hashes,
			"actual_dimensions": actual_dimensions,
			"expected_dimensions": {
				"scene_art": [ART_SIZE.x, ART_SIZE.y],
				"atlas": [ATLAS_SIZE.x, ATLAS_SIZE.y],
				"mask": [ART_SIZE.x, ART_SIZE.y],
				"foreground": [ART_SIZE.x, ART_SIZE.y]
			}
		}
	)


func _test_atlas_integrity() -> void:
	var atlas := Image.load_from_file(ATLAS_PATH)
	atlas.convert(Image.FORMAT_RGBA8)
	var border_alpha_pixels := 0
	for x in range(atlas.get_width()):
		border_alpha_pixels += int(atlas.get_pixel(x, 0).a > 0.0)
		border_alpha_pixels += int(atlas.get_pixel(x, atlas.get_height() - 1).a > 0.0)
	for y in range(atlas.get_height()):
		border_alpha_pixels += int(atlas.get_pixel(0, y).a > 0.0)
		border_alpha_pixels += int(atlas.get_pixel(atlas.get_width() - 1, y).a > 0.0)

	var frame_reports: Array[Dictionary] = []
	var row_hashes: Array[Array] = [[], [], [], []]
	var frame_contract_pass := true
	for row in range(4):
		for column in range(3):
			var frame := atlas.get_region(Rect2i(column * FRAME_SIZE.x, row * FRAME_SIZE.y, FRAME_SIZE.x, FRAME_SIZE.y))
			frame.convert(Image.FORMAT_RGBA8)
			var bbox := _alpha_bbox(frame)
			var opaque_pixels := _count_alpha_pixels(frame)
			var pixel_hash := _sha256_bytes(frame.get_data())
			row_hashes[row].append(pixel_hash)
			var baseline := int(bbox[3]) - 1 if int(bbox[3]) > 0 else -1
			var frame_pass := opaque_pixels > 0 and baseline == 59
			frame_pass = frame_pass and int(bbox[0]) > 0 and int(bbox[1]) > 0
			frame_pass = frame_pass and int(bbox[2]) < FRAME_SIZE.x and int(bbox[3]) < FRAME_SIZE.y
			frame_contract_pass = frame_contract_pass and frame_pass
			frame_reports.append({
				"row": row,
				"column": column,
				"opaque_pixels": opaque_pixels,
				"alpha_bbox": bbox,
				"foot_baseline_y": baseline,
				"pixel_sha256": pixel_hash,
				"passed": frame_pass
			})

	var distinct_per_row: Array[int] = []
	for row in range(4):
		var distinct: Array = []
		for pixel_hash in row_hashes[row]:
			if not distinct.has(pixel_hash):
				distinct.append(pixel_hash)
		distinct_per_row.append(distinct.size())
		frame_contract_pass = frame_contract_pass and distinct.size() == 3

	var runtime_contract := player_sprite.texture != null
	runtime_contract = runtime_contract and Vector2i(player_sprite.texture.get_size()) == ATLAS_SIZE
	runtime_contract = runtime_contract and player_sprite.hframes == 3 and player_sprite.vframes == 4
	runtime_contract = runtime_contract and player_sprite.position.distance_to(Vector2(0, -32)) <= 0.01
	runtime_contract = runtime_contract and player_sprite.scale.distance_to(Vector2.ONE) <= 0.001
	runtime_contract = runtime_contract and abs(player_sprite.rotation) <= 0.0001

	_record(
		"atlas_integrity",
		atlas.get_size() == ATLAS_SIZE and border_alpha_pixels == 0 and frame_contract_pass and runtime_contract,
		{
			"atlas_dimensions": [atlas.get_width(), atlas.get_height()],
			"grid": [3, 4],
			"frame_size": [FRAME_SIZE.x, FRAME_SIZE.y],
			"transparent_border_violations": border_alpha_pixels,
			"distinct_frame_hashes_per_row": distinct_per_row,
			"runtime_hframes": player_sprite.hframes,
			"runtime_vframes": player_sprite.vframes,
			"runtime_sprite_position": [player_sprite.position.x, player_sprite.position.y],
			"frames": frame_reports
		}
	)


func _test_direction_mapping() -> void:
	var original_collision_mask := player.collision_mask
	player.collision_mask = 0
	var cases := [
		{"direction": "down", "delta": Vector2(0, 80), "expected_row": 0},
		{"direction": "left", "delta": Vector2(-80, 0), "expected_row": 1},
		{"direction": "right", "delta": Vector2(80, 0), "expected_row": 2},
		{"direction": "up", "delta": Vector2(0, -80), "expected_row": 3}
	]
	var evidence_cases: Array[Dictionary] = []
	var passed := true
	for test_case in cases:
		var start := Vector2(836, 470)
		player.reset_for_test(start)
		player.clear_animation_trace()
		await get_tree().physics_frame
		player.command_move(start + test_case["delta"], 1.5)
		await get_tree().physics_frame
		var observed_row := int(player.facing_row)
		var observed_column := int(player.current_frame_column)
		while player.command_active:
			await get_tree().physics_frame
		var movement: Dictionary = player.last_command_result
		var case_pass := observed_row == int(test_case["expected_row"])
		case_pass = case_pass and movement.get("outcome", "") == "REACHED"
		passed = passed and case_pass
		evidence_cases.append({
			"direction": test_case["direction"],
			"expected_row": test_case["expected_row"],
			"observed_row": observed_row,
			"observed_column_during_motion": observed_column,
			"movement_outcome": movement.get("outcome", "MISSING"),
			"passed": case_pass
		})
	player.collision_mask = original_collision_mask
	player.reset_for_test(SPAWN)
	await get_tree().physics_frame
	_record("direction_mapping", passed, {"cases": evidence_cases})


func _test_temporal_animation() -> void:
	var original_collision_mask := player.collision_mask
	player.collision_mask = 0
	player.reset_for_test(Vector2(500, 820))
	player.clear_animation_trace()
	await get_tree().physics_frame
	var movement: Dictionary = await _run_command(Vector2(1100, 820), 4.0)
	await get_tree().physics_frame
	var columns := _normalized_trace_columns(player.animation_trace)
	var compressed_columns := _compress_values(columns)
	var distinct_columns: Array[int] = []
	for column in columns:
		if not distinct_columns.has(column):
			distinct_columns.append(column)
	var complete_cycle := _contains_subsequence(compressed_columns, [0, 1, 2, 1])
	var idle_after_stop := int(player.current_frame_column) == 1
	var passed: bool = movement.get("outcome", "") == "REACHED"
	passed = passed and int(movement.get("slide_collision_count", -1)) == 0
	passed = passed and distinct_columns.size() == 3 and complete_cycle and idle_after_stop
	var trace_count: int = player.animation_trace.size()
	player.collision_mask = original_collision_mask
	player.reset_for_test(SPAWN)
	await get_tree().physics_frame
	_record(
		"temporal_animation",
		passed,
		{
			"movement": movement,
			"trace_entry_count": trace_count,
			"trace_columns": columns,
			"compressed_trace_columns": compressed_columns,
			"distinct_columns": distinct_columns,
			"expected_cycle": [0, 1, 2, 1],
			"complete_cycle": complete_cycle,
			"idle_after_stop": idle_after_stop
		}
	)


func _test_foreground_asset_contract() -> void:
	if foreground == null or foreground.texture == null:
		_record("foreground_asset_contract", false, {"error": "ForegroundOccluder or its texture is missing"})
		return

	var source := Image.load_from_file(ART_PATH)
	var mask := Image.load_from_file(MASK_PATH)
	var file_foreground := Image.load_from_file(FOREGROUND_PATH)
	var runtime_foreground := foreground.texture.get_image()
	source.convert(Image.FORMAT_RGBA8)
	mask.convert(Image.FORMAT_L8)
	file_foreground.convert(Image.FORMAT_RGBA8)
	runtime_foreground.convert(Image.FORMAT_RGBA8)
	var mask_data := mask.get_data()
	var source_data := source.get_data()
	var foreground_data := file_foreground.get_data()
	var runtime_alpha_count := _count_alpha_pixels(runtime_foreground)
	var file_alpha_count := 0
	var alpha_mask_mismatches := 0
	var source_rgb_mismatches := 0
	for pixel_index in range(mask_data.size()):
		var mask_on := mask_data[pixel_index] > 0
		var alpha_offset := pixel_index * 4 + 3
		var foreground_on := foreground_data[alpha_offset] > 0
		if foreground_on:
			file_alpha_count += 1
		if mask_on != foreground_on:
			alpha_mask_mismatches += 1
		if mask_on:
			var color_offset := pixel_index * 4
			if source_data[color_offset] != foreground_data[color_offset] or source_data[color_offset + 1] != foreground_data[color_offset + 1] or source_data[color_offset + 2] != foreground_data[color_offset + 2]:
				source_rgb_mismatches += 1

	var runtime_resource_path := foreground.texture.resource_path
	var passed := file_alpha_count == EXPECTED_FOREGROUND_ALPHA_PIXELS
	passed = passed and runtime_alpha_count == EXPECTED_FOREGROUND_ALPHA_PIXELS
	passed = passed and alpha_mask_mismatches == 0 and source_rgb_mismatches == 0
	passed = passed and runtime_resource_path == FOREGROUND_PATH
	_record(
		"foreground_asset_contract",
		passed,
		{
			"expected_resource_path": FOREGROUND_PATH,
			"runtime_resource_path": runtime_resource_path,
			"expected_alpha_pixel_count": EXPECTED_FOREGROUND_ALPHA_PIXELS,
			"file_alpha_pixel_count": file_alpha_count,
			"runtime_alpha_pixel_count": runtime_alpha_count,
			"alpha_mask_mismatches": alpha_mask_mismatches,
			"source_rgb_mismatches": source_rgb_mismatches
		}
	)


func _test_foreground_transform_contract() -> void:
	if foreground == null:
		_record("foreground_transform_contract", false, {"error": "ForegroundOccluder is missing"})
		return
	var background := world.get_node("Background") as Sprite2D
	var expected_position := background.position
	var passed := foreground.position.distance_to(expected_position) <= 0.01
	passed = passed and foreground.scale.distance_to(Vector2.ONE) <= 0.001
	passed = passed and abs(foreground.rotation) <= 0.0001
	passed = passed and foreground.centered and foreground.offset.distance_to(Vector2.ZERO) <= 0.001
	_record(
		"foreground_transform_contract",
		passed,
		{
			"expected_position": [expected_position.x, expected_position.y],
			"actual_position": [foreground.position.x, foreground.position.y],
			"actual_scale": [foreground.scale.x, foreground.scale.y],
			"actual_rotation_radians": foreground.rotation,
			"actual_centered": foreground.centered,
			"actual_offset": [foreground.offset.x, foreground.offset.y]
		}
	)


func _test_occlusion_state_contract() -> void:
	if foreground == null or foreground.texture == null:
		_record("occlusion_state_contract", false, {"error": "ForegroundOccluder or its texture is missing"})
		return

	var atlas := Image.load_from_file(ATLAS_PATH)
	var mask := Image.load_from_file(MASK_PATH)
	atlas.convert(Image.FORMAT_RGBA8)
	mask.convert(Image.FORMAT_L8)
	var frame := atlas.get_region(Rect2i(FRAME_SIZE.x, 0, FRAME_SIZE.x, FRAME_SIZE.y))
	var top_left := Vector2i(int(OCCLUSION_POSE.x) - FRAME_SIZE.x / 2, int(OCCLUSION_POSE.y) - FRAME_SIZE.y)
	var overlap_pixels := 0
	var visible_player_pixels := 0
	for frame_y in range(FRAME_SIZE.y):
		for frame_x in range(FRAME_SIZE.x):
			if frame.get_pixel(frame_x, frame_y).a <= 0.0:
				continue
			var screen_point := top_left + Vector2i(frame_x, frame_y)
			if mask.get_pixel(screen_point.x, screen_point.y).r > 0.0:
				overlap_pixels += 1
			else:
				visible_player_pixels += 1

	var background := world.get_node("Background") as Sprite2D
	var runtime_image := foreground.texture.get_image()
	var runtime_alpha_pixels := _count_alpha_pixels(runtime_image)
	var overlap_fraction := _safe_ratio(overlap_pixels, overlap_pixels + visible_player_pixels)
	var passed := overlap_pixels == 130 and visible_player_pixels == 859
	passed = passed and overlap_fraction >= 0.10 and overlap_fraction <= 0.60
	passed = passed and foreground.z_index > player.z_index
	passed = passed and foreground.position.distance_to(background.position) <= 0.01
	passed = passed and foreground.texture.resource_path == FOREGROUND_PATH
	passed = passed and runtime_alpha_pixels == EXPECTED_FOREGROUND_ALPHA_PIXELS
	_record(
		"occlusion_state_contract",
		passed,
		{
			"test_pose": [OCCLUSION_POSE.x, OCCLUSION_POSE.y],
			"fixed_frame": {"row": 0, "column": 1},
			"sprite_screen_top_left": [top_left.x, top_left.y],
			"declared_overlap_pixels": overlap_pixels,
			"expected_overlap_pixels": 130,
			"visible_player_pixels_outside_mask": visible_player_pixels,
			"expected_visible_player_pixels": 859,
			"partial_overlap_fraction": overlap_fraction,
			"foreground_z_index": foreground.z_index,
			"player_z_index": player.z_index,
			"expected_foreground_position": [background.position.x, background.position.y],
			"actual_foreground_position": [foreground.position.x, foreground.position.y],
			"runtime_resource_path": foreground.texture.resource_path,
			"runtime_alpha_pixel_count": runtime_alpha_pixels,
			"actual_viewport_evidence": "validated separately by tests/capture_render.tscn and scripts/verify_render_captures.py using the real renderer"
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
	var movement := await _run_command(FOUNTAIN_CENTER, 2.0)
	var final_position := Vector2(float(movement["final_position"][0]), float(movement["final_position"][1]))
	var normalized := Vector2(
		(final_position.x - FOUNTAIN_CENTER.x) / FOUNTAIN_RADII.x,
		(final_position.y - FOUNTAIN_CENTER.y) / FOUNTAIN_RADII.y
	).length()
	var passed: bool = movement["outcome"] == "BLOCKED" and movement["collider_name"] == "FountainBasin" and int(movement["slide_collision_count"]) > 0 and normalized >= 0.98
	_record(
		"fountain_blocking",
		passed,
		{"movement": movement, "normalized_final_distance": normalized, "minimum_expected": 0.98}
	)


func _test_lower_court_outbound() -> void:
	player.reset_for_test(SPAWN)
	await get_tree().physics_frame
	var legs: Array = []
	var passed := true
	for waypoint in outbound_route:
		var movement := await _run_command(waypoint, 3.0)
		legs.append(movement)
		if movement["outcome"] != "REACHED" or float(movement["target_error_px"]) > 4.0 or int(movement["slide_collision_count"]) != 0:
			passed = false
			break
	var destination_error := player.global_position.distance_to(outbound_route[-1])
	passed = passed and destination_error <= 6.0
	_record(
		"lower_court_outbound",
		passed,
		{"legs": legs, "destination_error_px": destination_error, "maximum_destination_error_px": 6.0}
	)


func _test_lower_court_return() -> void:
	player.reset_for_test(outbound_route[-1])
	await get_tree().physics_frame
	var legs: Array = []
	var passed := true
	for waypoint in return_route:
		var movement := await _run_command(waypoint, 3.0)
		legs.append(movement)
		if movement["outcome"] != "REACHED" or float(movement["target_error_px"]) > 4.0 or int(movement["slide_collision_count"]) != 0:
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
	var movement := await _run_command(Vector2(560, 720), 2.0)
	var passed: bool = movement["outcome"] == "BLOCKED" and movement["collider_name"] == "PlazaBoundary" and int(movement["slide_collision_count"]) > 0
	_record(
		"outer_boundary",
		passed,
		{"movement": movement, "expected_collider": "PlazaBoundary"}
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


func _alpha_bbox(image: Image) -> Array[int]:
	var minimum_x := image.get_width()
	var minimum_y := image.get_height()
	var maximum_x := -1
	var maximum_y := -1
	for y in range(image.get_height()):
		for x in range(image.get_width()):
			if image.get_pixel(x, y).a > 0.0:
				minimum_x = mini(minimum_x, x)
				minimum_y = mini(minimum_y, y)
				maximum_x = maxi(maximum_x, x)
				maximum_y = maxi(maximum_y, y)
	if maximum_x < 0:
		return [-1, -1, -1, -1]
	return [minimum_x, minimum_y, maximum_x + 1, maximum_y + 1]


func _count_alpha_pixels(image: Image) -> int:
	var working := image.duplicate()
	working.convert(Image.FORMAT_RGBA8)
	var data: PackedByteArray = working.get_data()
	var count := 0
	for offset in range(3, data.size(), 4):
		if data[offset] > 0:
			count += 1
	return count


func _sha256_bytes(data: PackedByteArray) -> String:
	var context := HashingContext.new()
	context.start(HashingContext.HASH_SHA256)
	context.update(data)
	return context.finish().hex_encode().to_upper()


func _normalized_trace_columns(trace: Array) -> Array[int]:
	var columns: Array[int] = []
	for entry in trace:
		if entry is Dictionary:
			if entry.has("column"):
				columns.append(int(entry["column"]))
			elif entry.has("frame_column"):
				columns.append(int(entry["frame_column"]))
		elif entry is int or entry is float:
			columns.append(int(entry))
	return columns


func _compress_values(values: Array[int]) -> Array[int]:
	var compressed: Array[int] = []
	for value in values:
		if compressed.is_empty() or compressed[-1] != value:
			compressed.append(value)
	return compressed


func _contains_subsequence(values: Array[int], pattern: Array) -> bool:
	if pattern.is_empty() or values.size() < pattern.size():
		return false
	for start in range(values.size() - pattern.size() + 1):
		var matches := true
		for offset in range(pattern.size()):
			if values[start + offset] != int(pattern[offset]):
				matches = false
				break
		if matches:
			return true
	return false


func _safe_ratio(numerator: int, denominator: int) -> float:
	return float(numerator) / float(denominator) if denominator > 0 else 0.0


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
		"experiment": "experiment_e_character_occlusion",
		"mutation": mutation,
		"godot_version": Engine.get_version_info().get("string", "unknown"),
		"timestamp_utc": Time.get_datetime_string_from_system(true, true),
		"passed": failure_count == 0,
		"failure_count": failure_count,
		"source_hashes": {
			"scene_art": FileAccess.get_sha256(ART_PATH).to_upper(),
			"atlas": FileAccess.get_sha256(ATLAS_PATH).to_upper(),
			"mask": FileAccess.get_sha256(MASK_PATH).to_upper(),
			"foreground": FileAccess.get_sha256(FOREGROUND_PATH).to_upper(),
			"geometry": FileAccess.get_sha256(GEOMETRY_PATH).to_upper(),
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
