#!/usr/bin/env bash
set -euo pipefail

cd /workspace/auto-claude-code-research-in-sleep

# Idempotency guard
if grep -qF "description: \"Autonomously improve a generated paper via Claude review through c" "skills/skills-codex-claude-review/auto-paper-improvement-loop/SKILL.md" && grep -qF "description: \"Generate publication-quality figures and tables from experiment re" "skills/skills-codex-claude-review/paper-figure/SKILL.md" && grep -qF "description: \"Generate a structured paper outline from review conclusions and ex" "skills/skills-codex-claude-review/paper-plan/SKILL.md" && grep -qF "description: \"Draft LaTeX paper section by section from an outline. Use when use" "skills/skills-codex-claude-review/paper-write/SKILL.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/skills/skills-codex-claude-review/auto-paper-improvement-loop/SKILL.md b/skills/skills-codex-claude-review/auto-paper-improvement-loop/SKILL.md
@@ -1,6 +1,6 @@
 ---
 name: "auto-paper-improvement-loop"
-description: "Autonomously improve a generated paper via Claude review through claude-review MCP → implement fixes → recompile, for 2 rounds. Use when user says \\"改论文\\", \\"improve paper\\", \\"论文润色循环\\", \\"auto improve\\", or wants to iteratively polish a generated paper."
+description: "Autonomously improve a generated paper via Claude review through claude-review MCP → implement fixes → recompile, for 2 rounds. Use when user says \"改论文\", \"improve paper\", \"论文润色循环\", \"auto improve\", or wants to iteratively polish a generated paper."
 ---
 
 > Override for Codex users who want **Claude Code**, not a second Codex agent, to act as the reviewer. Install this package **after** `skills/skills-codex/*`.
diff --git a/skills/skills-codex-claude-review/paper-figure/SKILL.md b/skills/skills-codex-claude-review/paper-figure/SKILL.md
@@ -1,6 +1,6 @@
 ---
 name: "paper-figure"
-description: "Generate publication-quality figures and tables from experiment results. Use when user says \\"画图\\", \\"作图\\", \\"generate figures\\", \\"paper figures\\", or needs plots for a paper."
+description: "Generate publication-quality figures and tables from experiment results. Use when user says \"画图\", \"作图\", \"generate figures\", \"paper figures\", or needs plots for a paper."
 ---
 
 > Override for Codex users who want **Claude Code**, not a second Codex agent, to act as the reviewer. Install this package **after** `skills/skills-codex/*`.
diff --git a/skills/skills-codex-claude-review/paper-plan/SKILL.md b/skills/skills-codex-claude-review/paper-plan/SKILL.md
@@ -1,6 +1,6 @@
 ---
 name: "paper-plan"
-description: "Generate a structured paper outline from review conclusions and experiment results. Use when user says \\"写大纲\\", \\"paper outline\\", \\"plan the paper\\", \\"论文规划\\", or wants to create a paper plan before writing."
+description: "Generate a structured paper outline from review conclusions and experiment results. Use when user says \"写大纲\", \"paper outline\", \"plan the paper\", \"论文规划\", or wants to create a paper plan before writing."
 ---
 
 > Override for Codex users who want **Claude Code**, not a second Codex agent, to act as the reviewer. Install this package **after** `skills/skills-codex/*`.
diff --git a/skills/skills-codex-claude-review/paper-write/SKILL.md b/skills/skills-codex-claude-review/paper-write/SKILL.md
@@ -1,6 +1,6 @@
 ---
 name: "paper-write"
-description: "Draft LaTeX paper section by section from an outline. Use when user says \\"写论文\\", \\"write paper\\", \\"draft LaTeX\\", \\"开始写\\", or wants to generate LaTeX content from a paper plan."
+description: "Draft LaTeX paper section by section from an outline. Use when user says \"写论文\", \"write paper\", \"draft LaTeX\", \"开始写\", or wants to generate LaTeX content from a paper plan."
 ---
 
 > Override for Codex users who want **Claude Code**, not a second Codex agent, to act as the reviewer. Install this package **after** `skills/skills-codex/*`.
PATCH

echo "Gold patch applied."
