extends CharacterBody2D

signal reached_target

@export var speed: float = 280.0
@export var is_test_mode: bool = true

var target_position: Vector2 = Vector2.ZERO
var has_target: bool = false
var elevation_z: float = 0.0
var stuck_timer: float = 0.0
var target_timeout: float = 0.0

@onready var sprite: Sprite2D = $Sprite2D

func _ready() -> void:
	target_position = global_position

func _physics_process(delta: float) -> void:
	if is_test_mode:
		_process_automated_movement(delta)
	else:
		_process_manual_movement(delta)
		
	_update_elevation()
	move_and_slide()
	
	# Collision blocking detection (for Test B and obstacles)
	if is_test_mode and has_target:
		target_timeout += delta
		if get_slide_collision_count() > 0:
			stuck_timer += delta
			if stuck_timer > 0.4:
				stuck_timer = 0.0
				target_timeout = 0.0
				has_target = false
				velocity = Vector2.ZERO
				reached_target.emit()
		elif target_timeout > 4.0: # Fallback timeout
			target_timeout = 0.0
			stuck_timer = 0.0
			has_target = false
			velocity = Vector2.ZERO
			reached_target.emit()

func _process_automated_movement(_delta: float) -> void:
	if not has_target:
		velocity = Vector2.ZERO
		return
		
	var diff = target_position - global_position
	var dist = diff.length()
	
	if dist < 8.0:
		global_position = target_position
		velocity = Vector2.ZERO
		has_target = false
		stuck_timer = 0.0
		target_timeout = 0.0
		reached_target.emit()
	else:
		velocity = diff.normalized() * speed

func _process_manual_movement(_delta: float) -> void:
	var input_vector = Input.get_vector("ui_left", "ui_right", "ui_up", "ui_down")
	velocity = input_vector * speed

func set_target(pos: Vector2) -> void:
	target_position = pos
	has_target = true
	stuck_timer = 0.0
	target_timeout = 0.0

func _update_elevation() -> void:
	# Stairs corridor X in [840, 1000], Y in [430, 620]
	if global_position.x >= 840 and global_position.x <= 1000 and global_position.y >= 430 and global_position.y <= 620:
		var t = clampf((620.0 - global_position.y) / (620.0 - 430.0), 0.0, 1.0)
		elevation_z = t * 2.8
	elif global_position.y < 430:
		elevation_z = 2.8
	else:
		elevation_z = 0.0
