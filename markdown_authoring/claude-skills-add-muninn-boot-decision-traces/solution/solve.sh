#!/usr/bin/env bash
set -euo pipefail

cd /workspace/claude-skills

# Idempotency guard
if grep -qF "Credentials auto-detect from environment or well-known paths (`/mnt/project/turs" "CLAUDE.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/CLAUDE.md b/CLAUDE.md
@@ -1,5 +1,39 @@
 @AGENTS.md
 
+## Muninn Boot
+
+This repository is developed by two wings of the same raven. Claude Code implements; Claude.ai (Muninn) plans, tests, and operates the memory system. Both share a persistent memory store — boot it to maintain continuity.
+
+Unless the message contains "skip boot", execute at session start:
+
+```bash
+python3 << 'EOF'
+import sys
+sys.path.insert(0, '/home/user/claude-skills/remembering')
+from scripts import boot
+print(boot())
+EOF
+```
+
+Credentials auto-detect from environment or well-known paths (`/mnt/project/turso.env`, `/mnt/project/muninn.env`, `~/.muninn/.env`). If boot fails on missing credentials, note it and continue — not all sessions require memory access.
+
+### Decision Traces
+
+After completing meaningful work (implementation, bugfix, architecture decision), store a memory. This is how the other wing learns what happened.
+
+```python
+remember(
+    "Closed #NNN: [what was learned]. Key decision: [rationale]. "
+    "Constraint: [if any]. Future note: [what next session needs to know].",
+    "decision",
+    tags=["issue-NNN", "relevant-tags"],
+    priority=1  # 1=significant, 0=routine
+)
+```
+
+Good traces lead with *why*, not *what* — the diff shows what. Include constraints discovered, alternatives rejected, and gotchas for future sessions.
+
+
 ## Claude Code on the Web Development
 
 This repository is frequently developed via Claude Code on the web. Key workflow considerations:
@@ -215,10 +249,8 @@ If a skill has a `CLAUDE.md` file:
 Some skills (like `remembering`) should be used to track their own development:
 
 ```python
-# Example: Use remembering to track work on remembering
-import sys
-sys.path.insert(0, '/home/user/claude-skills/remembering')
-from scripts import remember, journal
+# After Muninn boot, remembering functions are available:
+from remembering.scripts import remember, journal
 
 journal(topics=["muninn-v0.4.0"],
         my_intent="Adding hybrid retrieval with embeddings")
@@ -393,9 +425,8 @@ cat /home/user/claude-skills/remembering/references/CLAUDE.md
 
 Then use the remembering skill to query handoffs:
 ```python
-import sys
-sys.path.insert(0, '/home/user/claude-skills/remembering')
-from scripts import recall, handoff_pending
+# After boot, remembering functions are available:
+from remembering.scripts import recall, handoff_pending
 
 # Check for handoffs - multiple approaches:
 # 1. Formal pending handoffs (tagged "handoff" + "pending")
@@ -419,6 +450,6 @@ The remembering skill uses **external Turso database storage** for both context
 Key implications:
 - **`muninn_utils/*.py` files don't exist in this repo** — they are generated at runtime from memory content
 - Utilities like `strengthen_memory.py`, `therapy.py`, `connection_finder.py` are stored as memories and written to disk during boot
-- These utilities import from the `scripts` package (e.g., `from scripts import _exec, reprioritize`), with the skill directory on `sys.path`
+- These utilities import from the `scripts` package (e.g., `from remembering.scripts import _exec, reprioritize`), with the skill directory on `sys.path`
 - To fix a utility's code, you must update the memory content in the database, not edit a file in this repo
 - The `_exec` function is exported in `scripts/__init__.py`'s `__all__` specifically to support these runtime utilities
PATCH

echo "Gold patch applied."
