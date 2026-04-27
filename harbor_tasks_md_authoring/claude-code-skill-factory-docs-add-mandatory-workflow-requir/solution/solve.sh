#!/usr/bin/env bash
set -euo pipefail

cd /workspace/claude-code-skill-factory

# Idempotency guard
if grep -qF "- \u2705 **Automation leverage**: Uses the excellent GitHub automation built into thi" "CLAUDE.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/CLAUDE.md b/CLAUDE.md
@@ -2,6 +2,74 @@
 
 This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.
 
+---
+
+## 🚨 MANDATORY WORKFLOW REQUIREMENT
+
+**CRITICAL**: All work on this project MUST follow this workflow. **NO EXCEPTIONS.**
+
+### Required Process for Every User Request
+
+1. **PLAN MODE FIRST**
+   - Use plan mode to create a detailed implementation plan
+   - Break down the work into clear, actionable steps
+   - Estimate effort and identify potential challenges
+
+2. **GET USER APPROVAL**
+   - Present the plan to the user
+   - Wait for explicit approval before proceeding
+   - Address any questions or concerns
+
+3. **CREATE GITHUB ISSUE**
+   - Create a GitHub issue with the `plan` label
+   - Include the approved plan in the issue body
+   - Use markdown checkboxes for tasks: `- [ ] Task name`
+   - The plan-to-issues automation will automatically create subtasks
+
+4. **AUTOMATION CREATES SUBTASKS**
+   - GitHub workflow creates individual issues for each task
+   - All subtasks are linked to the parent issue
+   - All added to project board for tracking
+
+5. **START IMPLEMENTATION**
+   - Begin work on subtasks in priority order
+   - Update issue status as you progress
+   - Reference issue numbers in commits
+
+### Why This Matters
+
+- ✅ **Proper tracking**: Every task is tracked in GitHub issues and project board
+- ✅ **Clear planning**: Prevents scope creep and ensures thoughtful approach
+- ✅ **Team visibility**: Everyone can see what's being worked on
+- ✅ **Audit trail**: Complete history of decisions and implementation
+- ✅ **Automation leverage**: Uses the excellent GitHub automation built into this repo
+
+### Example Workflow
+
+```
+User: "Add a new skill for data visualization"
+
+❌ WRONG: Start implementing immediately
+
+✅ CORRECT:
+1. Enter plan mode
+2. Create plan with tasks:
+   - Research data visualization libraries
+   - Design SKILL.md structure
+   - Implement Python visualization classes
+   - Create sample data and examples
+   - Write HOW_TO_USE.md
+   - Test with real data
+3. Present plan to user, get approval
+4. Create GitHub issue with 'plan' label containing tasks
+5. Wait for automation to create subtasks
+6. Begin implementation
+```
+
+**NEVER START WORK WITHOUT FOLLOWING THIS PROCESS.**
+
+---
+
 ## Repository Purpose
 
 This repository is a **Claude Code Skills factory** - a collection of example skills that demonstrate how to create specialized capabilities for Claude Code. Skills are folders with instructions and resources that Claude loads when relevant to the user's task.
PATCH

echo "Gold patch applied."
