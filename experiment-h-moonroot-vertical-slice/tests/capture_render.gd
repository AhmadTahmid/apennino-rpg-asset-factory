extends Node

const MAIN_SCENE := preload("res://scenes/main.tscn")


func _ready() -> void:
	call_deferred("_capture")


func _capture() -> void:
	var location := "town"
	var mode := "player"
	for argument in OS.get_cmdline_user_args():
		if argument.begins_with("--location="):
			location = argument.trim_prefix("--location=")
		elif argument.begins_with("--mode="):
			mode = argument.trim_prefix("--mode=")
	var world := MAIN_SCENE.instantiate()
	add_child(world)
	await get_tree().physics_frame
	world.get_node("Player").accept_manual_input = false
	world.set_location(location)
	world.get_node("Interface").visible = false
	world.get_node("Player").visible = mode == "player"
	await get_tree().process_frame
	await RenderingServer.frame_post_draw
	var image := get_viewport().get_texture().get_image()
	var path := "res://diagnostics/runtime_%s_%s.png" % [location, mode]
	var error := image.save_png(path)
	print(JSON.stringify({"location":location, "mode":mode, "path":path, "size":[image.get_width(),image.get_height()], "save_error":error}))
	get_tree().quit(0 if error == OK else 1)
