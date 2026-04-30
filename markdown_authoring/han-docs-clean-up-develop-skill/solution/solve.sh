#!/usr/bin/env bash
set -euo pipefail

cd /workspace/han

# Idempotency guard
if grep -qF "Structured 8-phase process for building new features from requirement gathering " "plugins/core/skills/develop/SKILL.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/plugins/core/skills/develop/SKILL.md b/plugins/core/skills/develop/SKILL.md
@@ -1,33 +1,20 @@
 ---
 name: develop
 user-invocable: false
-description: Comprehensive 8-phase workflow for developing new features with quality enforcement
+description: >-
+  Guides end-to-end feature development through 8 phases: discover requirements,
+  explore codebase patterns, clarify ambiguities with the user, design architecture,
+  implement with TDD, run multi-agent code review, validate all quality gates, and
+  write a blog post. Use when asked to add a feature, implement a new capability,
+  build functionality, or develop a feature end-to-end.
 ---
 
 # Feature Development Workflow
 
-## Name
-
-han-core:develop - Comprehensive 8-phase workflow for developing new features with quality enforcement
-
-## Synopsis
-
-```
-/develop [arguments]
-```
-
-## Description
-
-Comprehensive 8-phase workflow for developing new features with quality enforcement
-
-## Implementation
-
-A comprehensive, structured 8-phase workflow for developing new features with quality enforcement and quality principles.
+Structured 8-phase process for building new features from requirement gathering through documentation. Each phase produces a concrete output that feeds the next.
 
 ## Overview
 
-This command guides you through a systematic feature development process:
-
 1. **Discover** - Understand requirements and context
 2. **Explore** - Analyze existing codebase patterns
 3. **Clarify** - Resolve ambiguities with user input
@@ -342,24 +329,6 @@ Options:
 
 ---
 
-## Usage
-
-### Basic usage
-
-```
-/feature-dev
-```
-
-Then describe the feature you want to build.
-
-### With feature description
-
-```
-/feature-dev Add user authentication with JWT tokens
-```
-
----
-
 ## Best Practices
 
 ### DO
@@ -438,8 +407,7 @@ Testing: Run GET /api/users?page=1&limit=10
 
 ## See Also
 
-- `/review` - Run multi-agent review only
-- `/commit` - Smart commit workflow
-- `/create-blog-post` - Research and write blog posts
-- `tdd:test-driven-development` - TDD skill
-- `han-core:code-reviewer` - Review skill
+- `/review` - Multi-agent code review with confidence-based filtering
+- `/test` - Write tests using TDD principles
+- `/fix` - Debug and fix bugs
+- `/refactor` - Restructure code without changing behavior
PATCH

echo "Gold patch applied."
