#!/usr/bin/env bash
set -euo pipefail

cd /workspace/awesome-cursorrules

# Idempotency guard
if grep -qF "// The project is currently undergoing refactoring for better extensibility and " "rules/unity-cursor-ai-c-cursorrules-prompt-file/.cursorrules"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/rules/unity-cursor-ai-c-cursorrules-prompt-file/.cursorrules b/rules/unity-cursor-ai-c-cursorrules-prompt-file/.cursorrules
@@ -1,10 +1,19 @@
-The context for this code, in addition to the file itself and the wider project, is that I am making a tower defense style game that uses a Nintendo Ringcon as the controller. 
+// Unity Tower Defense Game using Nintendo Ringcon
+// This project involves creating a tower defense style game controlled by a Nintendo Ringcon.
 
-Players place turrets and then use exercise to charge up those turrets.
+// Project Context
+// Players place turrets and use exercise to charge them up.
+// The project is currently undergoing refactoring for better extensibility and maintainability.
 
-Currently, I'm refactoring the entire project, because I wrote much of it in a sprint, and I'm not sure how well it will work in the long run. I also want to be able to extend it more easily.
+// Development Environment
+// Language: C#
+// Unity Version: 2021.3.18f1
 
-You can ask questions if it would be helpful to know more about what I intend.
+// Instructions
+// Ensure the game mechanics are intuitive and responsive.
+// Focus on optimizing performance for real-time gameplay.
+// Implement modular code structure for easy updates and feature additions.
 
-In addition, I'm working in C# and Unity 2021.3.18f1.
+// Additional Notes
+// Feel free to ask questions if you need more information about the project intentions.
 
PATCH

echo "Gold patch applied."
