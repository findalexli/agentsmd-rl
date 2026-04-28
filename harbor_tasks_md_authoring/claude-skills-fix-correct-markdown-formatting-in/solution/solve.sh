#!/usr/bin/env bash
set -euo pipefail

cd /workspace/claude-skills

# Idempotency guard
if grep -qF "skills/prompt-engineer/references/prompt-patterns.md" "skills/prompt-engineer/references/prompt-patterns.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/skills/prompt-engineer/references/prompt-patterns.md b/skills/prompt-engineer/references/prompt-patterns.md
@@ -226,7 +226,7 @@ Final Answer:
 
 ### Example: Debugging with CoT
 
-```
+````
 Debug the following code by analyzing it step by step.
 
 Code:
@@ -263,7 +263,7 @@ def calculate_average(numbers):
     total = sum(numbers)
     return total / len(numbers)
 ```
-```
+````
 
 ### CoT Variants
 
PATCH

echo "Gold patch applied."
