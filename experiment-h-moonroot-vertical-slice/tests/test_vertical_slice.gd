extends Node

const MAIN_SCENE := preload("res://scenes/main.tscn")
const TEST_SAVE_PATH := "user://experiment_h_validation_save.json"
const HASHES := {
	"res://assets/moonroot_hollow.png": "7B4DF1C2EB62D1E1C12893E5F9D4B3E3DF28249C5323F8C6D9C9294194D09674",
	"res://assets/lumenwood_crossing.png": "1B79BBC4ABE4011860D867EA54A5F2183A1E028F57AD650AEA35DDB7D1D34FF8",
	"res://assets/heartroot_sanctuary.png": "0234F095E91097B296051DBF73A702C5470F9138148597127B74C649E4A621C0",
	"res://assets/traveler_walk_sheet.png": "4433340653530325DA27FE497E17226741B926404283383F1006FE7FE0FB6876"
}

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
	await get_tree().physics_frame
	player = world.get_node("Player")
	player.accept_manual_input = false
	world.save_path = TEST_SAVE_PATH
	world.apply_test_mutation(mutation)
	await get_tree().physics_frame
	_test_asset_integrity()
	_test_visible_art_policy()
	_test_manifest_contract()
	_test_initial_state()
	_test_locked_portal_contract()
	await _test_complete_vertical_slice()
	_test_inventory_contract()
	_test_save_load_roundtrip()
	_test_invalid_save_rejected()
	_test_new_game_reset()
	await _test_landmark_collisions()
	await _test_location_boundaries()
	_cleanup_save()
	_finish_suite()


func _test_asset_integrity() -> void:
	var actual := {}
	var dimensions := {}
	var passed := true
	for path in HASHES:
		actual[path] = FileAccess.get_sha256(path).to_upper()
		passed = passed and actual[path] == HASHES[path]
		var texture := load(path) as Texture2D
		dimensions[path] = [texture.get_width(), texture.get_height()]
		if path.contains("traveler"):
			passed = passed and texture.get_size() == Vector2(144, 256)
		else:
			passed = passed and texture.get_size() == Vector2(1672, 941)
	_record("asset_integrity", passed, {"actual_hashes": actual, "expected_hashes": HASHES, "dimensions": dimensions})


func _test_visible_art_policy() -> void:
	var banned_types := ["ColorRect", "Polygon2D", "Line2D", "NinePatchRect"]
	var violations: Array[String] = []
	for node in _descendants(world):
		if banned_types.has(node.get_class()):
			violations.append("%s:%s" % [node.get_path(), node.get_class()])
	var textures := [String(world.background.texture.resource_path), String(world.get_node("Player/Sprite").texture.resource_path)]
	var raster_only := true
	for path in textures:
		raster_only = raster_only and path.ends_with(".png")
	_record("visible_art_policy", violations.is_empty() and raster_only, {"violations": violations, "runtime_textures": textures, "policy": "visible illustration is raster PNG; engine text is UI; collision is invisible"})


func _test_manifest_contract() -> void:
	var failures: Array[String] = []
	var locations: Dictionary = world.manifest["locations"]
	if locations.keys().size() != 3:
		failures.append("expected exactly three locations")
	for location_id in locations:
		var spec: Dictionary = locations[location_id]
		var polygon := _vectors(spec["walkable_boundary"])
		var points := [_vector(spec["spawn"])]
		for interaction in spec["interactions"].values():
			points.append(_vector(interaction["anchor"]))
		for route_points in spec["tested_routes"].values():
			for point in route_points:
				points.append(_vector(point))
		for point in points:
			if not Geometry2D.is_point_in_polygon(point, polygon):
				failures.append("%s point outside boundary: %s" % [location_id, point])
		if not String(spec["art"]).ends_with(".png"):
			failures.append("%s art is not PNG" % location_id)
	_record("manifest_contract", failures.is_empty(), {"location_ids": locations.keys(), "failures": failures})


func _test_initial_state() -> void:
	world.start_new_game(false)
	var passed: bool = world.current_location == "town" and world.quest_state == "find_mora" and world.inventory.is_empty()
	passed = passed and player.global_position.distance_to(Vector2(836, 860)) < 0.01
	_record("initial_state", passed, _snapshot())


func _test_locked_portal_contract() -> void:
	world.start_new_game(false)
	world.quest_state = "gather_star_seed"
	world.set_location("forest")
	player.teleport_to(world.interaction_anchor("root_arch"), 3)
	var accepted: bool = world.try_interact()
	var passed: bool = not accepted and world.current_location == "forest" and world.quest_state == "gather_star_seed"
	_record("locked_portal_contract", passed, {"accepted_without_star_seed": accepted, "snapshot": _snapshot()})


func _test_complete_vertical_slice() -> void:
	world.start_new_game(false)
	var route_evidence: Array = []
	var interaction_evidence: Array = []
	var passed := true
	for stage in [
		{"location":"town", "route":"spawn_to_apothecary", "interaction":"apothecary", "state":"seek_moonwater"},
		{"location":"town", "route":"apothecary_to_moonwell", "interaction":"moonwell", "state":"deliver_moonwater"},
		{"location":"town", "route":"moonwell_to_gatekeeper", "interaction":"gatekeeper", "state":"enter_lumenwood"}
	]:
		var movement: Dictionary = await _follow_route(stage["route"], stage["location"])
		route_evidence.append(movement)
		var accepted: bool = world.try_interact()
		interaction_evidence.append({"id": stage["interaction"], "accepted": accepted, "state": world.quest_state})
		passed = passed and movement["reached_all"] and accepted and world.quest_state == stage["state"]
	var crossed_town_gate: bool = world.try_interact()
	passed = passed and crossed_town_gate and world.current_location == "forest" and world.quest_state == "gather_star_seed"
	interaction_evidence.append({"id":"gatekeeper_transition", "accepted":crossed_town_gate, "snapshot":_snapshot()})
	if world.current_location == "forest":
		var forest_seed_route := await _follow_route("spawn_to_star_seed", "forest")
		route_evidence.append(forest_seed_route)
		var seed_accepted: bool = world.try_interact()
		passed = passed and forest_seed_route["reached_all"] and seed_accepted and world.quest_state == "enter_sanctuary" and world.inventory.has("star_seed")
		interaction_evidence.append({"id":"star_seed", "accepted":seed_accepted, "snapshot":_snapshot()})
		var forest_arch_route := await _follow_route("star_seed_to_root_arch", "forest")
		route_evidence.append(forest_arch_route)
		var arch_accepted: bool = world.try_interact()
		passed = passed and forest_arch_route["reached_all"] and arch_accepted and world.current_location == "sanctuary" and world.quest_state == "restore_heartroot"
		interaction_evidence.append({"id":"root_arch", "accepted":arch_accepted, "snapshot":_snapshot()})
	else:
		passed = false
	if world.current_location == "sanctuary":
		var altar_route := await _follow_route("spawn_to_heartroot", "sanctuary")
		route_evidence.append(altar_route)
		var altar_accepted: bool = world.try_interact()
		passed = passed and altar_route["reached_all"] and altar_accepted and world.quest_state == "complete" and world.inventory.is_empty() and world.get_node("Interface/Ending").visible
		interaction_evidence.append({"id":"heartroot_altar", "accepted":altar_accepted, "snapshot":_snapshot()})
	else:
		passed = false
	_record("complete_vertical_slice", passed, {"routes": route_evidence, "interactions": interaction_evidence, "final": _snapshot()})


func _test_inventory_contract() -> void:
	world.start_new_game(false)
	player.teleport_to(world.interaction_anchor("apothecary"), 3)
	world.try_interact()
	player.teleport_to(world.interaction_anchor("moonwell"), 3)
	var collected_water: bool = world.try_interact() and world.inventory == ["moonwater"]
	player.teleport_to(world.interaction_anchor("gatekeeper"), 3)
	var delivered_water: bool = world.try_interact() and world.inventory.is_empty()
	world.quest_state = "gather_star_seed"
	world.set_location("forest")
	player.teleport_to(world.interaction_anchor("star_seed"), 3)
	var collected_seed: bool = world.try_interact() and world.inventory == ["star_seed"]
	_record("inventory_contract", collected_water and delivered_water and collected_seed, {"collected_water": collected_water, "delivered_water": delivered_water, "collected_seed": collected_seed, "snapshot": _snapshot()})


func _test_save_load_roundtrip() -> void:
	world.quest_state = "enter_sanctuary"
	world.inventory.clear()
	world.inventory.append("star_seed")
	world.set_location("forest", Vector2(610, 620))
	var saved: bool = world.save_game()
	world.quest_state = "find_mora"
	world.inventory.clear()
	world.set_location("town", Vector2(836, 860))
	var loaded: bool = world.load_game()
	var passed: bool = saved and loaded and world.current_location == "forest" and world.quest_state == "enter_sanctuary" and world.inventory == ["star_seed"]
	passed = passed and player.global_position.distance_to(Vector2(610, 620)) < 0.01
	_record("save_load_roundtrip", passed, {"saved": saved, "loaded": loaded, "snapshot": _snapshot(), "expected_position": [610,620]})


func _test_invalid_save_rejected() -> void:
	var before := _snapshot()
	var cases := [
		{"name":"wrong_schema", "payload":{"schema_version":999,"location":"void"}},
		{"name":"outside_boundary", "payload":{"schema_version":1,"location":"town","quest_state":"find_mora","inventory":[],"player_position":[-20,-20]}},
		{"name":"state_location_mismatch", "payload":{"schema_version":1,"location":"forest","quest_state":"find_mora","inventory":[],"player_position":[836,850]}}
	]
	var evidence: Array = []
	var passed := true
	for case in cases:
		var file := FileAccess.open(TEST_SAVE_PATH, FileAccess.WRITE)
		file.store_string(JSON.stringify(case["payload"]))
		file.close()
		var loaded: bool = world.load_game()
		var unchanged: bool = before == _snapshot()
		evidence.append({"case":case["name"], "loaded":loaded, "live_state_unchanged":unchanged})
		passed = passed and not loaded and unchanged
	_record("invalid_save_rejected", passed, {"cases":evidence, "snapshot":before})


func _test_new_game_reset() -> void:
	world.quest_state = "complete"
	world.inventory.append("star_seed")
	world.set_location("sanctuary", Vector2(836, 405))
	world.get_node("Interface/Ending").visible = true
	world.start_new_game(false)
	var passed: bool = world.current_location == "town" and world.quest_state == "find_mora" and world.inventory.is_empty() and not world.get_node("Interface/Ending").visible
	passed = passed and player.global_position.distance_to(Vector2(836,860)) < 0.01
	_record("new_game_reset", passed, _snapshot())


func _test_landmark_collisions() -> void:
	var cases := [
		{"location":"town", "start":Vector2(842,700), "target":Vector2(842,545), "collider":"MoonwellBasin"},
		{"location":"forest", "start":Vector2(1230,600), "target":Vector2(1230,465), "collider":"ForestMoonBasin"},
		{"location":"sanctuary", "start":Vector2(836,430), "target":Vector2(836,285), "collider":"HeartrootAltar"}
	]
	var evidence: Array = []
	var passed := true
	for case in cases:
		world.set_location(case["location"], case["start"])
		var result := await _move(case["target"])
		evidence.append({"location":case["location"], "result":result})
		passed = passed and result["outcome"] == "BLOCKED" and result["collider_name"] == case["collider"]
	_record("landmark_collisions", passed, evidence)


func _test_location_boundaries() -> void:
	var evidence: Array = []
	var passed := true
	for location_id in ["town", "forest", "sanctuary"]:
		world.set_location(location_id)
		var result := await _move(Vector2(player.global_position.x, 980))
		evidence.append({"location":location_id, "result":result})
		passed = passed and result["outcome"] == "BLOCKED" and String(result["collider_name"]).ends_with("Boundary")
	_record("location_boundaries", passed, evidence)


func _follow_route(route_id: String, location_id: String) -> Dictionary:
	var evidence: Array = []
	var reached_all: bool = world.current_location == location_id
	if reached_all:
		for value in world.route(route_id, location_id):
			var result := await _move(_vector(value))
			evidence.append(result)
			if result["outcome"] != "REACHED":
				reached_all = false
				break
	return {"location": location_id, "route": route_id, "reached_all": reached_all, "movements": evidence}


func _move(target: Vector2) -> Dictionary:
	player.command_move(target, 5.0)
	return await player.command_finished


func _record(test_name: String, passed: bool, evidence) -> void:
	results.append({"name": test_name, "passed": passed, "evidence": evidence})
	if not passed:
		failure_count += 1


func _snapshot() -> Dictionary:
	return {"location":world.current_location, "quest_state":world.quest_state, "inventory":world.inventory.duplicate(), "player_position":[player.global_position.x, player.global_position.y], "ending_visible":world.get_node("Interface/Ending").visible}


func _descendants(root: Node) -> Array[Node]:
	var result: Array[Node] = []
	for child in root.get_children():
		result.append(child)
		result.append_array(_descendants(child))
	return result


func _vector(value: Array) -> Vector2:
	return Vector2(float(value[0]), float(value[1]))


func _vectors(values: Array) -> PackedVector2Array:
	var result := PackedVector2Array()
	for value in values:
		result.append(_vector(value))
	return result


func _read_mutation() -> String:
	for argument in OS.get_cmdline_user_args():
		if argument.begins_with("--mutation="):
			return argument.trim_prefix("--mutation=")
	return "none"


func _cleanup_save() -> void:
	var absolute := ProjectSettings.globalize_path(TEST_SAVE_PATH)
	if FileAccess.file_exists(TEST_SAVE_PATH):
		DirAccess.remove_absolute(absolute)


func _finish_suite() -> void:
	var report := {"suite":"experiment_h_vertical_slice", "mutation":mutation, "passed":failure_count == 0, "assertions":results.size(), "failures":failure_count, "failed_test_names":results.filter(func(result): return not result["passed"]).map(func(result): return result["name"]), "results":results}
	var suffix := "" if mutation == "none" else "_" + mutation
	var path := "res://diagnostics/test_results%s.json" % suffix
	var file := FileAccess.open(path, FileAccess.WRITE)
	file.store_string(JSON.stringify(report, "  "))
	file.close()
	print(JSON.stringify(report))
	get_tree().quit(0 if failure_count == 0 else 1)
