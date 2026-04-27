#!/usr/bin/env bash
set -euo pipefail

cd /workspace/godogen

# Idempotency guard
if grep -qF "**Script section ordering:** signals \u2192 @onready vars \u2192 private state \u2192 lifecycle" ".claude/skills/godot-task/SKILL.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/.claude/skills/godot-task/SKILL.md b/.claude/skills/godot-task/SKILL.md
@@ -232,38 +232,11 @@ car.owner = root  # Child internals already have owner — just set on instance
 
 **2D uses pixels.** Standard viewport: 1920x1080 or 1280x720. Player sprite: 64-128px; Tiles: 16/32/64px.
 
-### Scene @export Parameters
-
-Use `@export` for ALL tunable build-time values:
-```gdscript
-extends SceneTree
-
-# Object placement and orientation
-@export var player_position: Vector3 = Vector3(0, 1, 0)  ## Player spawn point
-@export var player_rotation: Vector3 = Vector3(0, 0, 0)  ## Facing direction (radians)
-@export var model_rotation: Vector3 = Vector3(0, PI, 0)  ## Fix GLB orientation (often needs 180 Y)
-
-# Layout and structure
-@export var floor_size: Vector3 = Vector3(20, 0.5, 20)  ## Floor dimensions
-@export var platform_count: int = 5  ## Number of platforms
-
-# Camera setup
-@export var camera_position: Vector3 = Vector3(0, 15, 10)  ## Camera world position
-@export var camera_rotation: Vector3 = Vector3(-PI/4, 0, 0)  ## Camera angle (radians)
-```
-
-**Export for scenes:** positions, rotations, scales, layout counts, dimensions.
-**NOT for scenes** (use runtime scripts instead): speeds, forces, health, damage — anything that changes during gameplay.
-
 ### Scene Template
 
 ```gdscript
 extends SceneTree
 
-@export var ball_position: Vector3 = Vector3(0, 2, 0)  ## Ball spawn point
-@export var camera_position: Vector3 = Vector3(0, 10, 8)  ## Camera placement
-@export var camera_rotation: Vector3 = Vector3(-PI/4, 0, 0)  ## Camera angle
-
 func _initialize() -> void:
     print("Generating: {scene_name}")
 
@@ -324,7 +297,6 @@ Generate a `.gd` file that:
 2. Uses proper Godot lifecycle methods
 3. References sibling/child nodes via correct paths
 4. Defines and connects signals as needed
-5. **Exposes ALL tuneable parameters via `@export`** for easy modification
 
 ### Script Template
 
@@ -336,10 +308,6 @@ extends {NodeType}
 signal health_changed(new_value: int)
 signal died
 
-# Exported parameters (tuneable in editor or via code)
-@export var speed: float = 200.0  ## Movement speed in pixels/second
-@export var max_health: int = 100  ## Maximum health points
-
 # Node references (resolved at _ready)
 @onready var sprite: Sprite2D = $Sprite2D
 @onready var collision: CollisionShape2D = $CollisionShape2D
@@ -354,38 +322,16 @@ func _physics_process(delta: float) -> void:
     pass
 ```
 
-**Script section ordering:** signals → exports → @onready vars → private state → lifecycle methods → public methods → private methods → signal handlers
-
-### Script @export Parameters
-
-```gdscript
-# Movement and physics
-@export var speed: float = 200.0          ## Movement speed
-@export var acceleration: float = 1000.0  ## Ground acceleration
-@export var jump_velocity: float = -400.0 ## Jump impulse (negative = up)
-@export var move_force: float = 15.0      ## Force for RigidBody movement
-
-# Combat and gameplay
-@export var max_health: int = 100         ## Maximum HP
-@export var damage: int = 10              ## Damage dealt on hit
-@export var attack_cooldown: float = 0.5  ## Seconds between attacks
-
-# Timing and behavior
-@export var spawn_interval: float = 2.0   ## Seconds between spawns
-@export var detection_range: float = 10.0 ## AI detection distance
-```
-
-**Export for scripts:** speeds, forces, health, damage, cooldowns, timings, any magic number.
-**NOT for scripts** (use scene gen instead): object positions, rotations, scales (baked into scene).
+**Script section ordering:** signals → @onready vars → private state → lifecycle methods → public methods → private methods → signal handlers
 
 ### Movement Patterns
 
 **CharacterBody2D/3D (Kinematic):**
 ```gdscript
 extends CharacterBody2D
 
-@export var speed: float = 200.0
-@export var jump_velocity: float = -400.0
+var speed: float = 200.0
+var jump_velocity: float = -400.0
 
 func _physics_process(delta: float) -> void:
     if not is_on_floor():
@@ -401,7 +347,7 @@ func _physics_process(delta: float) -> void:
 ```gdscript
 extends RigidBody3D
 
-@export var move_force: float = 10.0
+var move_force: float = 10.0
 
 func _physics_process(_delta: float) -> void:
     var input := Vector3.ZERO
PATCH

echo "Gold patch applied."
