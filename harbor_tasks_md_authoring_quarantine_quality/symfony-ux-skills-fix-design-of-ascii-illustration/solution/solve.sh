#!/usr/bin/env bash
set -euo pipefail

cd /workspace/symfony-ux-skills

# Idempotency guard
if grep -qF "|                     Page                            |" "skills/symfony-ux/SKILL.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/skills/symfony-ux/SKILL.md b/skills/symfony-ux/SKILL.md
@@ -252,20 +252,20 @@ class Message
 
 ```
 +-----------------------------------------------------+
-|                     Page                             |
-|  +------------------------------------------------+  |
-|  | Turbo Drive (automatic full-page AJAX)          |  |
-|  |  +------------------------------------------+  |  |
-|  |  | Turbo Frame (partial section)             |  |  |
-|  |  |  +------------------------------------+  |  |  |
-|  |  |  | LiveComponent (reactive)            |  |  |  |
-|  |  |  |  +------------------------------+  |  |  |  |
-|  |  |  |  | TwigComponent (static)        |  |  |  |  |
-|  |  |  |  |  + Stimulus (JS behavior)     |  |  |  |  |
-|  |  |  |  +------------------------------+  |  |  |  |
-|  |  |  +------------------------------------+  |  |  |
-|  |  +------------------------------------------+  |  |
-|  +------------------------------------------------+  |
+|                     Page                            |
+|  +------------------------------------------------+ |
+|  | Turbo Drive (automatic full-page AJAX)         | |
+|  |  +------------------------------------------+  | |
+|  |  | Turbo Frame (partial section)            |  | |
+|  |  |  +------------------------------------+  |  | |
+|  |  |  | LiveComponent (reactive)           |  |  | |
+|  |  |  |  +------------------------------+  |  |  | |
+|  |  |  |  | TwigComponent (static)       |  |  |  | |
+|  |  |  |  |  + Stimulus (JS behavior)    |  |  |  | |
+|  |  |  |  +------------------------------+  |  |  | |
+|  |  |  +------------------------------------+  |  | |
+|  |  +------------------------------------------+  | |
+|  +------------------------------------------------+ |
 +-----------------------------------------------------+
 ```
 
PATCH

echo "Gold patch applied."
