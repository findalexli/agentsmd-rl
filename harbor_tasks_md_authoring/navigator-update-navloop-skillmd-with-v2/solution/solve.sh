#!/usr/bin/env bash
set -euo pipefail

cd /workspace/navigator

# Idempotency guard
if grep -qF "The JSON format in a `pilot-signal` code block ensures unambiguous detection by " "skills/nav-loop/SKILL.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/skills/nav-loop/SKILL.md b/skills/nav-loop/SKILL.md
@@ -257,7 +257,11 @@ Options:
 
 ### Step 7: Complete Loop
 
-**When exit conditions met**, display completion:
+**When exit conditions met**, emit the exit signal in JSON format and display completion:
+
+```pilot-signal
+{"v":2,"type":"exit","success":true,"reason":"All criteria met"}
+```
 
 ```
 ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
@@ -304,13 +308,20 @@ The EXIT_SIGNAL is set **explicitly by Claude** when:
 - Code is functional and tested
 - No obvious remaining work
 
-**How to signal completion**:
-```
-I've completed the implementation. All requirements met.
+**How to signal completion** (v2 JSON format):
 
-EXIT_SIGNAL: true
+```pilot-signal
+{"v":2,"type":"exit","success":true,"reason":"All requirements met"}
 ```
 
+The JSON format in a `pilot-signal` code block ensures unambiguous detection by Pilot automation. The `reason` field should briefly describe why the task is complete.
+
+**Signal fields**:
+- `v`: Version (always `2`)
+- `type`: Signal type (always `"exit"` for completion)
+- `success`: Whether task completed successfully (`true`/`false`)
+- `reason`: Brief explanation of completion state
+
 This explicit declaration prevents premature exits when heuristics are met but work remains.
 
 ---
@@ -443,8 +454,13 @@ Iteration 2 (IMPL):
 Iteration 3 (VERIFY):
   - Ran tests: PASS
   - Committed changes
-  EXIT_SIGNAL: true
+```
 
+```pilot-signal
+{"v":2,"type":"exit","success":true,"reason":"isPrime function implemented and tests passing"}
+```
+
+```
 → Loop complete in 3 iterations
 ```
 
@@ -464,8 +480,13 @@ User: "The test needs a mock for the auth service"
 Iteration 4 (IMPL):
   - Added mock
   - Tests pass
-  EXIT_SIGNAL: true
+```
 
+```pilot-signal
+{"v":2,"type":"exit","success":true,"reason":"Auth bug fixed with mock service"}
+```
+
+```
 → Loop complete in 4 iterations
 ```
 
PATCH

echo "Gold patch applied."
