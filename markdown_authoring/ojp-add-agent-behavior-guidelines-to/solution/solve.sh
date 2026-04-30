#!/usr/bin/env bash
set -euo pipefail

cd /workspace/ojp

# Idempotency guard
if grep -qF "- Proactively offer questions, opinions, suggestions, and concerns rather than w" ".github/copilot-instructions.md" && grep -qF "- Proactively offer questions, opinions, suggestions, and concerns rather than w" "Agents.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/.github/copilot-instructions.md b/.github/copilot-instructions.md
@@ -4,6 +4,16 @@ This file provides guidance for GitHub Copilot working inside this repository. R
 
 ---
 
+## Agent Behavior Guidelines
+
+- Use simple language and simple examples to explain things.
+- Be honest, even when the honest answer is "I don't know" or "this approach has problems."
+- Look for the best technical solution, not just the most convenient one.
+- Don't default to agreement — push back when something seems wrong or suboptimal.
+- Proactively offer questions, opinions, suggestions, and concerns rather than waiting to be asked.
+
+---
+
 ## Java Runtime Requirement
 
 **This project uses Java 21. Use the Java 21 runtime for all build and test tasks.**
diff --git a/Agents.md b/Agents.md
@@ -4,6 +4,16 @@ This file provides guidance for AI coding agents (GitHub Copilot, etc.) working
 
 ---
 
+## Agent Behavior Guidelines
+
+- Use simple language and simple examples to explain things.
+- Be honest, even when the honest answer is "I don't know" or "this approach has problems."
+- Look for the best technical solution, not just the most convenient one.
+- Don't default to agreement — push back when something seems wrong or suboptimal.
+- Proactively offer questions, opinions, suggestions, and concerns rather than waiting to be asked.
+
+---
+
 ## What OJP Is
 
 OJP is the **world's first open-source JDBC Type 3 driver**. It consists of two main deployable artefacts:
PATCH

echo "Gold patch applied."
