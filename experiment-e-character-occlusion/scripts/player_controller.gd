extends CharacterBody2D

signal command_finished(result: Dictionary)

enum MovementOutcome { REACHED, BLOCKED, TIMEOUT }

const ROW_DOWN := 0
const ROW_LEFT := 1
const ROW_RIGHT := 2
const ROW_UP := 3
const IDLE_COLUMN := 1
const WALK_SEQUENCE := [0, 1, 2, 1]

@export var speed := 260.0
@export var command_tolerance_px := 3.0
@export var accept_manual_input := true
@export var animation_fps := 7.0

var command_active := false
var command_target := Vector2.ZERO
var command_timeout := 0.0
var command_elapsed := 0.0
var command_collision_count := 0
var last_command_result: Dictionary = {}

# Test mutations are in-memory only; the source atlas is never rewritten.
var freeze_animation := false
var swap_left_right_rows := false

var facing_row := ROW_DOWN
var current_frame_column := IDLE_COLUMN
var animation_trace: Array[Dictionary] = []
var _walk_phase := 0
var _animation_elapsed := 0.0
var _was_moving := false

@onready var sprite: Sprite2D = $Sprite


func _ready() -> void:
	_apply_frame(IDLE_COLUMN, ROW_DOWN, "ready")


func _physics_process(delta: float) -> void:
	if command_active:
		_process_command(delta)
	elif accept_manual_input:
		_process_manual_input()
	else:
		velocity = Vector2.ZERO
	_update_animation(delta)


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
	_walk_phase = 0
	_animation_elapsed = 0.0
	_was_moving = false
	_apply_frame(IDLE_COLUMN, facing_row, "test_reset")


func clear_animation_trace() -> void:
	animation_trace.clear()


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


func _update_animation(delta: float) -> void:
	var moving := velocity.length_squared() > 0.01
	if not moving:
		_animation_elapsed = 0.0
		_walk_phase = 0
		_was_moving = false
		_apply_frame(IDLE_COLUMN, facing_row, "idle")
		return

	var selected_row := _row_for_velocity(velocity)
	if swap_left_right_rows:
		if selected_row == ROW_LEFT:
			selected_row = ROW_RIGHT
		elif selected_row == ROW_RIGHT:
			selected_row = ROW_LEFT

	if not _was_moving or selected_row != facing_row:
		_walk_phase = 0
		_animation_elapsed = 0.0
		_apply_frame(WALK_SEQUENCE[_walk_phase], selected_row, "movement_start")
	_was_moving = true

	if freeze_animation:
		_apply_frame(IDLE_COLUMN, selected_row, "mutation_frozen")
		return

	_animation_elapsed += delta
	var frame_duration := 1.0 / animation_fps
	while _animation_elapsed >= frame_duration:
		_animation_elapsed -= frame_duration
		_walk_phase = (_walk_phase + 1) % WALK_SEQUENCE.size()
		_apply_frame(WALK_SEQUENCE[_walk_phase], selected_row, "movement_tick")


func _row_for_velocity(direction: Vector2) -> int:
	if abs(direction.x) > abs(direction.y):
		return ROW_RIGHT if direction.x > 0.0 else ROW_LEFT
	return ROW_DOWN if direction.y > 0.0 else ROW_UP


func _apply_frame(column: int, row: int, reason: String) -> void:
	if current_frame_column == column and facing_row == row and sprite.frame_coords == Vector2i(column, row):
		return
	current_frame_column = column
	facing_row = row
	sprite.frame_coords = Vector2i(column, row)
	animation_trace.append({
		"physics_frame": Engine.get_physics_frames(),
		"time_msec": Time.get_ticks_msec(),
		"column": column,
		"row": row,
		"reason": reason,
		"velocity": [velocity.x, velocity.y]
	})


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
