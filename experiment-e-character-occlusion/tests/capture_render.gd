extends Node

const MAIN_SCENE := preload("res://scenes/main.tscn")
const CAPTURE_ANCHOR := Vector2(704, 675)


func _ready() -> void:
	call_deferred("_capture_sequence")


func _capture_sequence() -> void:
	var world := MAIN_SCENE.instantiate()
	add_child(world)
	var player: CharacterBody2D = world.get_node("Player")
	var foreground: Sprite2D = world.get_node("ForegroundOccluder")
	player.accept_manual_input = false
	player.global_position = CAPTURE_ANCHOR
	player.get_node("Sprite").frame_coords = Vector2i(1, 0)
	await _settle_frames()
	var normal_ok := _save_viewport("res://diagnostics/runtime_occlusion_capture.png")

	foreground.z_index = 5
	await _settle_frames()
	var mutation_ok := _save_viewport("res://diagnostics/runtime_occlusion_capture_player_above.png")

	player.visible = false
	await _settle_frames()
	var baseline_ok := _save_viewport("res://diagnostics/runtime_occlusion_baseline.png")

	print("CAPTURE_SUMMARY normal=%s mutation=%s baseline=%s" % [normal_ok, mutation_ok, baseline_ok])
	get_tree().quit(0 if normal_ok and mutation_ok and baseline_ok else 1)


func _settle_frames() -> void:
	for _index in range(4):
		await get_tree().process_frame


func _save_viewport(path: String) -> bool:
	var image: Image = get_viewport().get_texture().get_image()
	var expected_size := Vector2i(1672, 941)
	if image == null:
		printerr("Capture failed for %s: renderer returned no image" % path)
		return false
	if image.is_empty() or image.get_size() != expected_size:
		printerr("Capture failed for %s: size=%s" % [path, image.get_size()])
		return false
	var error := image.save_png(path)
	if error != OK:
		printerr("Capture save failed for %s: error=%s" % [path, error])
		return false
	return true
