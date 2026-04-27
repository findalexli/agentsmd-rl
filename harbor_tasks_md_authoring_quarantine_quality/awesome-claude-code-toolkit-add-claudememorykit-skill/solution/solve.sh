#!/usr/bin/env bash
set -euo pipefail

cd /workspace/awesome-claude-code-toolkit

# Idempotency guard
if grep -qF "description: \"Persistent memory system for Claude Code. Two-layer architecture (" "skills/claude-memory-kit/SKILL.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/skills/claude-memory-kit/SKILL.md b/skills/claude-memory-kit/SKILL.md
@@ -0,0 +1,33 @@
+---
+name: claude-memory-kit
+description: "Persistent memory system for Claude Code. Two-layer architecture (hot cache + knowledge wiki), safety hooks, /close-day end-of-day synthesis. Zero external dependencies."
+author: awrshift
+version: 3.2.0
+tags: [memory, context-management, productivity, agent-memory]
+repository: https://github.com/awrshift/claude-memory-kit
+license: MIT
+---
+
+# Claude Memory Kit
+
+Your Claude agent remembers everything across sessions and projects.
+
+## What it does
+
+- **Persistent memory** — MEMORY.md hot cache + knowledge wiki with [[wikilinks]]
+- **Multi-project support** — per-project backlogs and context isolation
+- **Safety hooks** — prevent context loss during compression and long sessions
+- **`/close-day`** — one command captures your entire day
+- **`/tour`** — interactive guided walkthrough
+
+## Quick Start
+
+```bash
+git clone https://github.com/awrshift/claude-memory-kit.git my-project
+cd my-project
+claude
+```
+
+## Built from production
+
+700+ sessions across 7 projects. Adapted from Karpathy/Cole Medin's knowledge base pattern, simplified for daily CLI use.
PATCH

echo "Gold patch applied."
