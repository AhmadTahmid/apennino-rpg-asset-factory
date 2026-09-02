extends Node

const MAIN_SCENE := preload("res://scenes/main.tscn")
const CAPTURE_ANCHOR := Vector2(836, 800)


func _ready() -> void:
	call_deferred("_capture_sequence")


func _capture_sequence() -> void:
	var world := MAIN_SCENE.instantiate()
	add_child(world)
	var player: CharacterBody2D = world.get_node("Player")
	player.accept_manual_input = false
	player.teleport_to(CAPTURE_ANCHOR, 0)
	world.get_node("Interface").visible = false
	await _settle_frames()
	var player_ok := _save_viewport("res://diagnostics/runtime_town_capture.png")
	player.visible = false
	await _settle_frames()
	var baseline_ok := _save_viewport("res://diagnostics/runtime_town_baseline.png")
	get_tree().quit(0 if player_ok and baseline_ok else 1)


func _settle_frames() -> void:
	for _index in range(4):
		await get_tree().process_frame


func _save_viewport(path: String) -> bool:
	var image := get_viewport().get_texture().get_image()
	if image == null or image.is_empty() or image.get_size() != Vector2i(1672, 941):
		return false
	return image.save_png(path) == OK
