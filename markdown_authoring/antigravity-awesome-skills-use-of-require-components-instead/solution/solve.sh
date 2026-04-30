#!/usr/bin/env bash
set -euo pipefail

cd /workspace/antigravity-awesome-skills

# Idempotency guard
if grep -qF "### Example 1: Spawning Entities with Require Component" "skills/bevy-ecs-expert/SKILL.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/skills/bevy-ecs-expert/SKILL.md b/skills/bevy-ecs-expert/SKILL.md
@@ -83,25 +83,27 @@ fn main() {
 
 ## Examples
 
-### Example 1: Spawning Entities with Bundles
+### Example 1: Spawning Entities with Require Component
 
 ```rust
-#[derive(Bundle)]
-struct PlayerBundle {
-    player: Player,
-    velocity: Velocity,
-    sprite: SpriteBundle,
+use bevy::prelude::*;
+
+#[derive(Component, Reflect, Default)]
+#[require(Velocity, Sprite)]
+struct Player;
+
+#[derive(Component, Default)]
+struct Velocity {
+    x: f32,
+    y: f32,
 }
 
 fn setup(mut commands: Commands, asset_server: Res<AssetServer>) {
-    commands.spawn(PlayerBundle {
-        player: Player,
-        velocity: Velocity { x: 10.0, y: 0.0 },
-        sprite: SpriteBundle {
-            texture: asset_server.load("player.png"),
-            ..default()
-        },
-    });
+    commands.spawn((
+        Player,
+        Velocity { x: 10.0, y: 0.0 },
+        Sprite::from_image(asset_server.load("player.png")), 
+    ));
 }
 ```
 
PATCH

echo "Gold patch applied."
