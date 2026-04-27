#!/usr/bin/env bash
set -euo pipefail

cd /workspace/memsearch

# Idempotency guard
if grep -qF "description: \"Search and recall relevant memories from past sessions via memsear" "plugins/claude-code/skills/memory-recall/SKILL.md" && grep -qF "description: \"Search and recall relevant memories from past sessions via memsear" "plugins/codex/skills/memory-recall/SKILL.md" && grep -qF "description: \"Search and recall relevant memories from past sessions via memsear" "plugins/openclaw/skills/memory-recall/SKILL.md" && grep -qF "description: \"Search and recall relevant memories from past sessions via memsear" "plugins/opencode/skills/memory-recall/SKILL.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/plugins/claude-code/skills/memory-recall/SKILL.md b/plugins/claude-code/skills/memory-recall/SKILL.md
@@ -1,6 +1,6 @@
 ---
 name: memory-recall
-description: "Search and recall relevant memories from past sessions. Use when the user's question could benefit from historical context, past decisions, debugging notes, previous conversations, or project knowledge. Also use when you see '[memsearch] Memory available' hints."
+description: "Search and recall relevant memories from past sessions via memsearch. Use when the user's question could benefit from historical context, past decisions, debugging notes, previous conversations, or project knowledge -- especially questions like 'what did I decide about X', 'why did we do Y', or 'have I seen this before'. Also use when you see `[memsearch] Memory available` hints injected via SessionStart or UserPromptSubmit. Typical flow: search for 3-5 chunks, expand the most relevant, optionally deep-drill into original transcripts via the anchor format. Skip when the question is purely about current code state (use Read/Grep), ephemeral (today's task only), or the user has explicitly asked to ignore memory."
 context: fork
 allowed-tools: Bash
 ---
diff --git a/plugins/codex/skills/memory-recall/SKILL.md b/plugins/codex/skills/memory-recall/SKILL.md
@@ -1,6 +1,6 @@
 ---
 name: memory-recall
-description: "Search and recall relevant memories from past sessions. Use when the user's question could benefit from historical context, past decisions, debugging notes, previous conversations, or project knowledge. Also use when you see '[memsearch] Memory available' hints."
+description: "Search and recall relevant memories from past sessions via memsearch. Use when the user's question could benefit from historical context, past decisions, debugging notes, previous conversations, or project knowledge -- especially questions like 'what did I decide about X', 'why did we do Y', or 'have I seen this before'. Also use when you see `[memsearch] Memory available` hints injected via SessionStart or UserPromptSubmit. Typical flow: search for 3-5 chunks, expand the most relevant, optionally deep-drill into original transcripts via the anchor format. Skip when the question is purely about current code state (use Read/Grep), ephemeral (today's task only), or the user has explicitly asked to ignore memory."
 ---
 
 You are performing memory retrieval for memsearch. Search past memories and return the most relevant context to the current conversation.
diff --git a/plugins/openclaw/skills/memory-recall/SKILL.md b/plugins/openclaw/skills/memory-recall/SKILL.md
@@ -1,6 +1,6 @@
 ---
 name: memory-recall
-description: "Search and recall relevant memories from past sessions. Use when the user's question could benefit from historical context, past decisions, debugging notes, previous conversations, or project knowledge."
+description: "Search and recall relevant memories from past sessions via memsearch. Use when the user's question could benefit from historical context, past decisions, debugging notes, previous conversations, or project knowledge -- especially questions like 'what did I decide about X', 'why did we do Y', or 'have I seen this before'. Also use when you see `[memsearch] Memory available` hints injected via SessionStart or UserPromptSubmit. Typical flow: search for 3-5 chunks, expand the most relevant, optionally deep-drill into original transcripts via the anchor format. Skip when the question is purely about current code state (use Read/Grep), ephemeral (today's task only), or the user has explicitly asked to ignore memory."
 metadata:
   openclaw:
     emoji: "🧠"
diff --git a/plugins/opencode/skills/memory-recall/SKILL.md b/plugins/opencode/skills/memory-recall/SKILL.md
@@ -1,6 +1,6 @@
 ---
 name: memory-recall
-description: "Search and recall relevant memories from past sessions. Use when the user's question could benefit from historical context, past decisions, debugging notes, previous conversations, or project knowledge."
+description: "Search and recall relevant memories from past sessions via memsearch. Use when the user's question could benefit from historical context, past decisions, debugging notes, previous conversations, or project knowledge -- especially questions like 'what did I decide about X', 'why did we do Y', or 'have I seen this before'. Also use when you see `[memsearch] Memory available` hints injected via SessionStart or UserPromptSubmit. Typical flow: search for 3-5 chunks, expand the most relevant, optionally deep-drill into original transcripts via the anchor format. Skip when the question is purely about current code state (use Read/Grep), ephemeral (today's task only), or the user has explicitly asked to ignore memory."
 allowed-tools: Bash
 ---
 
PATCH

echo "Gold patch applied."
