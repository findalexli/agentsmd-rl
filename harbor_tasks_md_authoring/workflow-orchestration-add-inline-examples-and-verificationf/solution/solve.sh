#!/usr/bin/env bash
set -euo pipefail

cd /workspace/workflow-orchestration

# Idempotency guard
if grep -qF "prompt: \"Find all authentication middleware in src/ and list file paths with a o" "SKILL.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/SKILL.md b/SKILL.md
@@ -40,6 +40,15 @@ Keep the main context window clean:
 - For complex problems, throw more compute at it via subagents
 - One task per subagent for focused execution
 
+**Template:**
+
+```
+Agent({
+  description: "Search auth patterns",
+  prompt: "Find all authentication middleware in src/ and list file paths with a one-line summary of each."
+})
+```
+
 ## 3. Self-Improvement Loop
 
 After ANY correction from the user:
@@ -48,14 +57,23 @@ After ANY correction from the user:
 2. Write rules that prevent the same mistake
 3. Review lessons at session start
 
-See [references/lessons-format.md](references/lessons-format.md) for the template.
+**Inline example** (full template in [references/lessons-format.md](references/lessons-format.md)):
+
+```markdown
+## 2024-01-10 - Testing
+**Mistake**: Mocks hid real API behavior; production broke
+**Pattern**: Over-mocking created false confidence
+**Rule**: Include at least one integration test hitting real services
+**Applied**: All API endpoints, external service integrations
+```
 
 ## 4. Verification Before Done
 
 - Never mark a task complete without proving it works
 - Diff behavior between main and your changes when relevant
 - Ask yourself: "Would a staff engineer approve this?"
 - Run tests, check logs, demonstrate corrections
+- If verification fails → return to the plan step and revise before retrying
 
 ## 5. Demand Elegance (Balanced)
 
@@ -75,10 +93,21 @@ See [references/lessons-format.md](references/lessons-format.md) for the templat
 2. **Verify Plan**: Check in before starting implementation
 3. **Track Progress**: Mark items complete as you go
 4. **Explain Changes**: High-level summary at each step
-5. **Document Results**: Add review to `tasks/todo.md`
-6. **Capture Lessons**: Update `tasks/lessons.md` after corrections
-
-See [references/task-templates.md](references/task-templates.md) for file templates.
+5. **Verify Results**: Run tests and confirm behavior before marking done
+6. **Handle Failures**: If verification fails → re-plan (step 1), don't push through
+7. **Document Results**: Add review to `tasks/todo.md`
+8. **Capture Lessons**: Update `tasks/lessons.md` after corrections
+
+**Inline example** (full templates in [references/task-templates.md](references/task-templates.md)):
+
+```markdown
+# Task: Fix memory leak in WebSocket handler
+## Plan
+- [ ] Reproduce the issue locally
+- [ ] Identify leak source with profiler
+- [ ] Implement fix
+- [ ] Verification: Memory stable over 1000 connections
+```
 
 ## Core Principles
 
PATCH

echo "Gold patch applied."
