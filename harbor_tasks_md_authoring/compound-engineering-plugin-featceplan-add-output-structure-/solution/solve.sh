#!/usr/bin/env bash
set -euo pipefail

cd /workspace/compound-engineering-plugin

# Idempotency guard
if grep -qF "The tree is a scope declaration showing the expected output shape. It is not a c" "plugins/compound-engineering/skills/ce-plan/SKILL.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/plugins/compound-engineering/skills/ce-plan/SKILL.md b/plugins/compound-engineering/skills/ce-plan/SKILL.md
@@ -348,6 +348,20 @@ Frame every sketch with: *"This illustrates the intended approach and is directi
 
 Keep sketches concise — enough to validate direction, not enough to copy-paste into production.
 
+#### 3.4b Output Structure (Optional)
+
+For greenfield plans that create a new directory structure (new plugin, service, package, or module), include an `## Output Structure` section with a file tree showing the expected layout. This gives reviewers the overall shape before diving into per-unit details.
+
+**When to include it:**
+- The plan creates 3+ new files in a new directory hierarchy
+- The directory layout itself is a meaningful design decision
+
+**When to skip it:**
+- The plan only modifies existing files
+- The plan creates 1-2 files in an existing directory — the per-unit file lists are sufficient
+
+The tree is a scope declaration showing the expected output shape. It is not a constraint — the implementer may adjust the structure if implementation reveals a better layout. The per-unit `**Files:**` sections remain authoritative for what each unit creates or modifies.
+
 #### 3.5 Define Each Implementation Unit
 
 For each unit, include:
@@ -454,6 +468,12 @@ deepened: YYYY-MM-DD  # optional, set when the confidence check substantively st
 
 - [Explicit non-goal or exclusion]
 
+<!-- Optional: When some items are planned work that will happen in a separate PR, issue,
+     or repo, use this sub-heading to distinguish them from true non-goals. -->
+### Deferred to Separate Tasks
+
+- [Work that will be done separately]: [Where or when -- e.g., "separate PR in repo-x", "future iteration"]
+
 ## Context & Research
 
 ### Relevant Code and Patterns
@@ -482,6 +502,14 @@ deepened: YYYY-MM-DD  # optional, set when the confidence check substantively st
 
 - [Question or unknown]: [Why it is intentionally deferred]
 
+<!-- Optional: Include when the plan creates a new directory structure (greenfield plugin,
+     new service, new package). Shows the expected output shape at a glance. Omit for plans
+     that only modify existing files. This is a scope declaration, not a constraint --
+     the implementer may adjust the structure if implementation reveals a better layout. -->
+## Output Structure
+
+    [directory tree showing new directories and files]
+
 <!-- Optional: Include this section only when the work involves DSL design, multi-component
      integration, complex data flow, state-heavy lifecycle, or other cases where prose alone
      would leave the approach shape ambiguous. Omit it entirely for well-patterned or
@@ -621,6 +649,8 @@ Before finalizing, check:
 - Deferred items are explicit and not hidden as fake certainty
 - If a High-Level Technical Design section is included, it uses the right medium for the work, carries the non-prescriptive framing, and does not contain implementation code (no imports, exact signatures, or framework-specific syntax)
 - Per-unit technical design fields, if present, are concise and directional rather than copy-paste-ready
+- If the plan creates a new directory structure, would an Output Structure tree help reviewers see the overall shape?
+- If Scope Boundaries lists items that are planned work for a separate PR or task, are they under `### Deferred to Separate Tasks` rather than mixed with true non-goals?
 - Would a visual aid (dependency graph, interaction diagram, comparison table) help a reader grasp the plan structure faster than scanning prose alone?
 
 If the plan originated from a requirements document, re-read that document and verify:
PATCH

echo "Gold patch applied."
