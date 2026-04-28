#!/usr/bin/env bash
set -euo pipefail

cd /workspace/dd-sdk-ios

# Idempotency guard
if grep -qF "name: dd-sdk-ios:git-branch" ".claude/skills/git-branch/SKILL.md" && grep -qF "name: dd-sdk-ios:git-commit" ".claude/skills/git-commit/SKILL.md" && grep -qF "**Before running the command**, show the user the proposed PR title and full bod" ".claude/skills/open-pr/SKILL.md" && grep -qF "name: dd-sdk-ios:running-tests" ".claude/skills/running-tests/SKILL.md" && grep -qF "name: dd-sdk-ios:xcode-file-management" ".claude/skills/xcode-file-management/SKILL.md" && grep -qF "| `dd-sdk-ios:xcode-file-management` | Adding, removing, moving, or renaming Swi" "CLAUDE.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/.claude/skills/git-branch/SKILL.md b/.claude/skills/git-branch/SKILL.md
@@ -1,5 +1,5 @@
 ---
-name: git-branch
+name: dd-sdk-ios:git-branch
 description: Use when creating a new branch in dd-sdk-ios for a JIRA ticket or feature. Use when choosing a branch name or base branch for development work.
 ---
 
diff --git a/.claude/skills/git-commit/SKILL.md b/.claude/skills/git-commit/SKILL.md
@@ -1,5 +1,5 @@
 ---
-name: git-commit
+name: dd-sdk-ios:git-commit
 description: Use when committing changes in dd-sdk-ios. Use when writing commit messages, signing commits, or staging files before a commit.
 ---
 
diff --git a/.claude/skills/open-pr/SKILL.md b/.claude/skills/open-pr/SKILL.md
@@ -1,5 +1,5 @@
 ---
-name: git-pr
+name: dd-sdk-ios:open-pr
 description: Use when creating a pull request in dd-sdk-ios. Use when writing PR titles, PR body, or choosing the target branch.
 ---
 
@@ -25,7 +25,9 @@ description: Use when creating a pull request in dd-sdk-ios. Use when writing PR
 
 ## Creating via gh
 
-The repo has a PR template at `.github/PULL_REQUEST_TEMPLATE.md`. Read it and fill in all sections:
+The repo has a PR template at `.github/PULL_REQUEST_TEMPLATE.md`. Read it and fill in all sections.
+
+**Before running the command**, show the user the proposed PR title and full body and ask for confirmation. Only run `gh pr create` after the user approves.
 
 ```bash
 gh pr create \
diff --git a/.claude/skills/running-tests/SKILL.md b/.claude/skills/running-tests/SKILL.md
@@ -1,5 +1,5 @@
 ---
-name: running-tests
+name: dd-sdk-ios:running-tests
 description: Use when asked to run tests in the dd-sdk-ios project — whether a full module suite, a specific test class, or a single test method. Use when choosing between make, xcodebuild, or Xcode MCP for running iOS/tvOS/visionOS tests.
 ---
 
diff --git a/.claude/skills/xcode-file-management/SKILL.md b/.claude/skills/xcode-file-management/SKILL.md
@@ -1,5 +1,5 @@
 ---
-name: xcode-file-management
+name: dd-sdk-ios:xcode-file-management
 description: Use when adding, removing, moving, or renaming Swift source files in the dd-sdk-ios Xcode project. Use when the task involves file creation, deletion, or relocation in any module (DatadogRUM, DatadogLogs, DatadogCore, etc.). Use when you would otherwise reach for Write, Bash mv/mkdir/rm, or manual pbxproj editing for file management.
 ---
 
diff --git a/CLAUDE.md b/CLAUDE.md
@@ -10,6 +10,18 @@ This file provides guidance to Claude Code (claude.ai/code) when working with co
 
 This is the Datadog SDK for iOS and tvOS - a modular Swift/Objective-C library for observability (Logs, Traces, RUM, Session Replay, Crash Reporting, WebView Tracking, and Feature Flags).
 
+## Available Skills
+
+Use these skills (via `/skill-name`) for common workflows in this project:
+
+| Skill | When to use |
+|---|---|
+| `dd-sdk-ios:git-branch` | Creating a new branch for a JIRA ticket or feature |
+| `dd-sdk-ios:git-commit` | Committing changes (signed commits, message format) |
+| `dd-sdk-ios:open-pr` | Opening a pull request against `develop` |
+| `dd-sdk-ios:running-tests` | Running unit, module, or integration tests |
+| `dd-sdk-ios:xcode-file-management` | Adding, removing, moving, or renaming Swift source files |
+
 ## Build & Test Commands
 
 ### Initial Setup
PATCH

echo "Gold patch applied."
