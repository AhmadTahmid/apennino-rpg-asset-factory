extends CharacterBody2D

signal command_finished(result: Dictionary)

enum MovementOutcome { REACHED, BLOCKED, TIMEOUT }

@export var speed := 260.0
@export var command_tolerance_px := 3.0
@export var accept_manual_input := true

var command_active := false
var command_target := Vector2.ZERO
var command_timeout := 0.0
var command_elapsed := 0.0
var command_collision_count := 0
var last_command_result: Dictionary = {}


func _physics_process(delta: float) -> void:
	if command_active:
		_process_command(delta)
	elif accept_manual_input:
		_process_manual_input()
	else:
		velocity = Vector2.ZERO


func command_move(target: Vector2, timeout_seconds := 3.0) -> void:
	command_target = target
	command_timeout = timeout_seconds
	command_elapsed = 0.0
	command_collision_count = 0
	last_command_result = {}
	command_active = true


func reset_for_test(position_px: Vector2) -> void:
	command_active = false
	velocity = Vector2.ZERO
	global_position = position_px
	last_command_result = {}


func _process_command(delta: float) -> void:
	var error := global_position.distance_to(command_target)
	if error <= command_tolerance_px:
		_finish_command(MovementOutcome.REACHED, "")
		return

	command_elapsed += delta
	if command_elapsed > command_timeout:
		_finish_command(MovementOutcome.TIMEOUT, "")
		return

	velocity = global_position.direction_to(command_target) * speed
	move_and_slide()
	if get_slide_collision_count() > 0:
		command_collision_count += get_slide_collision_count()
		var collision := get_slide_collision(0)
		var collider_name := ""
		if collision.get_collider() is Node:
			collider_name = String(collision.get_collider().name)
		_finish_command(MovementOutcome.BLOCKED, collider_name)


func _process_manual_input() -> void:
	var horizontal := float(Input.is_key_pressed(KEY_D) or Input.is_key_pressed(KEY_RIGHT)) - float(Input.is_key_pressed(KEY_A) or Input.is_key_pressed(KEY_LEFT))
	var vertical := float(Input.is_key_pressed(KEY_S) or Input.is_key_pressed(KEY_DOWN)) - float(Input.is_key_pressed(KEY_W) or Input.is_key_pressed(KEY_UP))
	velocity = Vector2(horizontal, vertical).normalized() * speed
	move_and_slide()


func _finish_command(outcome: MovementOutcome, collider_name: String) -> void:
	velocity = Vector2.ZERO
	command_active = false
	last_command_result = {
		"outcome": MovementOutcome.keys()[outcome],
		"target": [command_target.x, command_target.y],
		"final_position": [global_position.x, global_position.y],
		"target_error_px": global_position.distance_to(command_target),
		"collider_name": collider_name,
		"elapsed_seconds": command_elapsed,
		"slide_collision_count": command_collision_count
	}
	command_finished.emit(last_command_result)
