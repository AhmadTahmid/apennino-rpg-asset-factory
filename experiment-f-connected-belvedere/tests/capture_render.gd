extends Node

const MAIN_SCENE := preload("res://scenes/main.tscn")
const CAPTURE_ANCHOR := Vector2(836, 720)


func _ready() -> void:
	call_deferred("_capture_sequence")


func _capture_sequence() -> void:
	var world := MAIN_SCENE.instantiate()
	add_child(world)
	var player: CharacterBody2D = world.get_node("Player")
	player.accept_manual_input = false
	world.enter_node_for_test("belvedere", CAPTURE_ANCHOR, 3)
	world.get_node("Interface").visible = false
	await _settle_frames()
	var player_ok := _save_viewport("res://diagnostics/runtime_belvedere_capture.png")
	player.visible = false
	await _settle_frames()
	var baseline_ok := _save_viewport("res://diagnostics/runtime_belvedere_baseline.png")
	print("CAPTURE_SUMMARY player=%s baseline=%s" % [player_ok, baseline_ok])
	get_tree().quit(0 if player_ok and baseline_ok else 1)


func _settle_frames() -> void:
	for _index in range(4):
		await get_tree().process_frame


func _save_viewport(path: String) -> bool:
	var image: Image = get_viewport().get_texture().get_image()
	if image == null or image.is_empty() or image.get_size() != Vector2i(1672, 941):
		printerr("Capture failed for %s: size=%s" % [path, image.get_size() if image != null else Vector2i.ZERO])
		return false
	var error := image.save_png(path)
	if error != OK:
		printerr("Capture save failed for %s: error=%s" % [path, error])
		return false
	return true
