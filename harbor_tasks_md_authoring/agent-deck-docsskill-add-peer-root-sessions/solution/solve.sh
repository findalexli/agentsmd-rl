#!/usr/bin/env bash
set -euo pipefail

cd /workspace/agent-deck

# Idempotency guard
if grep -qF "**The default \u2014 sub-agent linkage:** `agent-deck launch` and `agent-deck add`, w" "skills/agent-deck/SKILL.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/skills/agent-deck/SKILL.md b/skills/agent-deck/SKILL.md
@@ -167,6 +167,39 @@ agent-deck remove "Consult Codex"
 agent-deck remove "Codex Review" && agent-deck remove "Gemini Arch"
 ```
 
+## Peer (Root) Sessions vs Sub-Agents
+
+**The default — sub-agent linkage:** `agent-deck launch` and `agent-deck add`, when invoked from *inside* an existing agent-deck session, automatically link the new session as a child of the calling session (sets `parent_session_id`, inherits the parent's group when `-g` is omitted, and grants `--add-dir` to the parent's project path). This is usually what you want for short-lived work sessions (plan / verify / release / consult).
+
+**When the default is wrong — root-level peer sessions:** if you are creating a session that should stand independently at the root — a peer conductor, a standalone project session, a session that should outlive the current one, or anything that semantically is NOT a child of the calling session — pass the `-no-parent` flag.
+
+| Use case | Parent linkage | Flag |
+|---|---|---|
+| Plan / impl / verify worker for the current task | ✅ child | (default) |
+| Consultation (codex / gemini / research) | ✅ child | (default) |
+| Another conductor (root-level peer) | ❌ child | `-no-parent` |
+| Project session unrelated to current work | ❌ child | `-no-parent` |
+| Session intended to outlive the caller | ❌ child | `-no-parent` |
+
+```bash
+# Root-level peer conductor, no parent linkage:
+agent-deck launch ~/projects/foo -t "conductor-foo" -g "conductor" -c claude -no-parent -m "..."
+
+# Verify after spawn:
+agent-deck list --json | jq '.[] | select(.title=="conductor-foo") | .parent_session_id'
+# Must print: null
+```
+
+**Symptoms you created a sub-agent when you wanted a peer:**
+- `parent_session_id` is non-null in `list --json` output
+- The new session's baked `pane_start_command` contains `--add-dir <caller's path>` even though you gave it a different project path
+- Transition events for the new session's children flow to the caller instead of the new peer
+- Event routing and heartbeat parent-linkage puts it under the caller's tree in the TUI
+
+**Fix for an already-created sub-agent:** stop + remove the session, re-launch with `-no-parent`. There is no in-place un-parent flag.
+
+**Note on the launch-subagent.sh script:** that script is specifically designed to create sub-agents (the name says so). It does NOT support `-no-parent`. For peer sessions, skip the script and invoke `agent-deck launch -no-parent` directly.
+
 ## TUI Keyboard Shortcuts
 
 ### Navigation
PATCH

echo "Gold patch applied."
