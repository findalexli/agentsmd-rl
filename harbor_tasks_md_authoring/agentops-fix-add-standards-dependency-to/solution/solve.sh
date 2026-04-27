#!/usr/bin/env bash
set -euo pipefail

cd /workspace/agentops

# Idempotency guard
if grep -qF "When `/crank` is invoked without an epic-id, check the preceding conversation fo" "plugins/core-kit/skills/crank/SKILL.md" && grep -qF "plugins/general-kit/skills/validation-chain/SKILL.md" "plugins/general-kit/skills/validation-chain/SKILL.md" && grep -qF "plugins/general-kit/skills/vibe-docs/SKILL.md" "plugins/general-kit/skills/vibe-docs/SKILL.md" && grep -qF "2. **Recent code changes in conversation** - If code was just written or edited," "plugins/general-kit/skills/vibe/SKILL.md" && grep -qF "plugins/vibe-kit/skills/validation-chain/SKILL.md" "plugins/vibe-kit/skills/validation-chain/SKILL.md" && grep -qF "plugins/vibe-kit/skills/vibe-docs/SKILL.md" "plugins/vibe-kit/skills/vibe-docs/SKILL.md" && grep -qF "2. **Recent code changes in conversation** - If code was just written or edited," "plugins/vibe-kit/skills/vibe/SKILL.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/plugins/core-kit/skills/crank/SKILL.md b/plugins/core-kit/skills/crank/SKILL.md
@@ -54,6 +54,57 @@ fi
 /crank <epic-id> --mode=mayor    # Parallel via polecats
 ```
 
+---
+
+## Context Inference
+
+When `/crank` is invoked without an epic-id, check the preceding conversation for context:
+
+### Priority Order
+
+1. **Explicit epic-id** - If user provides an epic ID, use it
+2. **Recently discussed epic** - If an epic was mentioned in conversation, use it
+3. **Hooked work** - Check `gt hook` for assigned epic
+4. **In-progress epic** - Check `bd list --type=epic --status=in_progress`
+5. **Ask user** - If no context found, ask which epic to crank
+
+### Detection Logic
+
+```markdown
+## On Invocation Without Epic ID
+
+1. Scan conversation for epic references:
+   - Look for issue IDs with epic type (e.g., "ap-68ohb")
+   - Check for "epic", "parent issue" mentions
+   - Extract from recent bd commands in conversation
+
+2. Check Gas Town hook:
+   ```bash
+   gt hook  # Returns hooked work including parent epic
+   ```
+
+3. Check beads state:
+   ```bash
+   bd list --type=epic --status=in_progress | head -1
+   ```
+
+4. If nothing found, ask:
+   "Which epic should I crank? Run `bd list --type=epic` to see available epics."
+```
+
+### Example
+
+```
+User: let's work on ap-68ohb - it has 27 children to implement
+User: [does some planning work]
+User: /crank
+
+→ Crank infers epic from conversation: ap-68ohb
+→ Starts autonomous execution without requiring re-specification
+```
+
+---
+
 ## The ODMCR Loop
 
 Both modes use the same reconciliation loop, just different dispatch mechanisms:
diff --git a/plugins/general-kit/skills/validation-chain/SKILL.md b/plugins/general-kit/skills/validation-chain/SKILL.md
@@ -10,6 +10,7 @@ allowed-tools: Read, Grep, Glob, Task, TodoWrite
 skills:
   - beads
   - vibe
+  - standards
 triggers:
   - "validate changes"
   - "run validation"
diff --git a/plugins/general-kit/skills/vibe-docs/SKILL.md b/plugins/general-kit/skills/vibe-docs/SKILL.md
@@ -9,6 +9,8 @@ version: 1.0.0
 author: "AI Platform Team"
 context: fork
 allowed-tools: "Read,Glob,Grep,Bash,Task"
+skills:
+  - standards
 ---
 
 # Vibe-Docs Skill
diff --git a/plugins/general-kit/skills/vibe/SKILL.md b/plugins/general-kit/skills/vibe/SKILL.md
@@ -16,6 +16,7 @@ context-budget:
   typical-session: 15KB
 skills:
   - beads
+  - standards
 ---
 
 # Vibe - Talos Comprehensive Validation
@@ -47,6 +48,49 @@ architecture, accessibility, complexity, and more.
 
 ---
 
+## Context Inference
+
+When `/vibe` is invoked without a target, check the preceding conversation for context:
+
+### Priority Order
+
+1. **Explicit target** - If user provides a path/target, use it
+2. **Recent code changes in conversation** - If code was just written or edited, validate those files
+3. **Staged git changes** - If `git diff --cached` shows staged files, validate those
+4. **Unstaged changes** - If `git diff` shows modified files, validate those
+5. **Default to `recent`** - Fall back to recent git changes
+
+### Detection Logic
+
+```markdown
+## On Invocation Without Target
+
+1. Check if files were edited in this conversation:
+   - Look for recent Edit/Write tool calls
+   - Extract file paths from tool results
+   - If found: validate those specific files
+
+2. Check git state:
+   ```bash
+   git diff --cached --name-only  # Staged changes
+   git diff --name-only           # Unstaged changes
+   ```
+
+3. If nothing found, use `recent` (HEAD~1..HEAD)
+```
+
+### Example
+
+```
+User: [writes some code to services/auth/handler.py]
+User: /vibe
+
+→ Vibe infers target from conversation: services/auth/handler.py
+→ Validates that specific file instead of requiring explicit path
+```
+
+---
+
 ## Aspects
 
 Vibe validates across 8 aspects. By default, all aspects run.
diff --git a/plugins/vibe-kit/skills/validation-chain/SKILL.md b/plugins/vibe-kit/skills/validation-chain/SKILL.md
@@ -10,6 +10,7 @@ allowed-tools: Read, Grep, Glob, Task, TodoWrite
 skills:
   - beads
   - vibe
+  - standards
 triggers:
   - "validate changes"
   - "run validation"
diff --git a/plugins/vibe-kit/skills/vibe-docs/SKILL.md b/plugins/vibe-kit/skills/vibe-docs/SKILL.md
@@ -9,6 +9,8 @@ version: 1.0.0
 author: "AI Platform Team"
 context: fork
 allowed-tools: "Read,Glob,Grep,Bash,Task"
+skills:
+  - standards
 ---
 
 # Vibe-Docs Skill
diff --git a/plugins/vibe-kit/skills/vibe/SKILL.md b/plugins/vibe-kit/skills/vibe/SKILL.md
@@ -16,6 +16,7 @@ context-budget:
   typical-session: 15KB
 skills:
   - beads
+  - standards
 ---
 
 # Vibe - Talos Comprehensive Validation
@@ -44,6 +45,49 @@ architecture, accessibility, complexity, and more.
 
 ---
 
+## Context Inference
+
+When `/vibe` is invoked without a target, check the preceding conversation for context:
+
+### Priority Order
+
+1. **Explicit target** - If user provides a path/target, use it
+2. **Recent code changes in conversation** - If code was just written or edited, validate those files
+3. **Staged git changes** - If `git diff --cached` shows staged files, validate those
+4. **Unstaged changes** - If `git diff` shows modified files, validate those
+5. **Default to `recent`** - Fall back to recent git changes
+
+### Detection Logic
+
+```markdown
+## On Invocation Without Target
+
+1. Check if files were edited in this conversation:
+   - Look for recent Edit/Write tool calls
+   - Extract file paths from tool results
+   - If found: validate those specific files
+
+2. Check git state:
+   ```bash
+   git diff --cached --name-only  # Staged changes
+   git diff --name-only           # Unstaged changes
+   ```
+
+3. If nothing found, use `recent` (HEAD~1..HEAD)
+```
+
+### Example
+
+```
+User: [writes some code to services/auth/handler.py]
+User: /vibe
+
+→ Vibe infers target from conversation: services/auth/handler.py
+→ Validates that specific file instead of requiring explicit path
+```
+
+---
+
 ## Aspects
 
 Vibe validates across 8 aspects. By default, all aspects run.
PATCH

echo "Gold patch applied."
