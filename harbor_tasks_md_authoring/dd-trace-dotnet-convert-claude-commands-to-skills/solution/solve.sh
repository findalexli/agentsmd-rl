#!/usr/bin/env bash
set -euo pipefail

cd /workspace/dd-trace-dotnet

# Idempotency guard
if grep -qF "description: Stack Trace Crash Analysis for dd-trace-dotnet" ".claude/skills/analyze-crash/SKILL.md" && grep -qF "description: Error Stack Trace Analysis for dd-trace-dotnet" ".claude/skills/analyze-error/SKILL.md" && grep -qF "allowed-tools: Bash(gh pr view:*), Bash(gh pr diff:*), Bash(gh pr comment:*), Ba" ".claude/skills/review-pr/SKILL.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/.claude/skills/analyze-crash/SKILL.md b/.claude/skills/analyze-crash/SKILL.md
@@ -1,3 +1,12 @@
+---
+name: analyze-crash
+description: Stack Trace Crash Analysis for dd-trace-dotnet
+argument-hint: <paste-stack-trace>
+disable-model-invocation: true
+context: fork
+agent: general-purpose
+---
+
 # Stack Trace Crash Analysis for dd-trace-dotnet
 
 You are analyzing a crash stack trace for the dd-trace-dotnet repository. Perform a comprehensive investigation to help engineers understand and triage the crash. Focus on de-mystifying the crashing thread and explaining how the crash occurred.
diff --git a/.claude/skills/analyze-error/SKILL.md b/.claude/skills/analyze-error/SKILL.md
@@ -1,3 +1,12 @@
+---
+name: analyze-error
+description: Error Stack Trace Analysis for dd-trace-dotnet
+argument-hint: <paste-error-stack-trace>
+disable-model-invocation: true
+context: fork
+agent: general-purpose
+---
+
 # Error Stack Trace Analysis for dd-trace-dotnet
 
 You are analyzing an error stack trace from the dd-trace-dotnet library. These errors originated from customer applications but are caused by dd-trace-dotnet. Your goal is to understand the error, determine if it provides enough information to identify the root cause, and recommend a fix ONLY if the error is actionable within dd-trace-dotnet.
diff --git a/.claude/skills/review-pr/SKILL.md b/.claude/skills/review-pr/SKILL.md
@@ -1,8 +1,15 @@
 ---
+name: review-pr
 description: Perform a review on a GitHub PR, leaving comments on the PR
 argument-hint: <pr-number-or-url>
-allowed-tools: Bash(gh pr view:*), Bash(gh pr diff:*), Bash(gh pr comment:*)
+disable-model-invocation: true
+allowed-tools: Bash(gh pr view:*), Bash(gh pr diff:*), Bash(gh pr comment:*), Bash(gh --version), Bash(gh auth status)
+context: fork
+agent: general-purpose
 ---
+
+# Review GitHub PR
+
 You are an expert code reviewer. Review this PR and post your findings to GitHub: $ARGUMENTS
 
 Prerequisites:
PATCH

echo "Gold patch applied."
