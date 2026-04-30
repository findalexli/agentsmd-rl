#!/usr/bin/env bash
set -euo pipefail

cd /workspace/posthog

# Idempotency guard
if grep -qF "allowed-tools: mcp__posthog__skill-list, mcp__posthog__skill-get, mcp__posthog__" "products/llm_analytics/skills/skills-store/SKILL.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/products/llm_analytics/skills/skills-store/SKILL.md b/products/llm_analytics/skills/skills-store/SKILL.md
@@ -14,14 +14,17 @@ PostHog is the primary store for team-shared skills — always use the PostHog M
 
 ## Available tools
 
-| Tool                      | Purpose                                                     |
-| ------------------------- | ----------------------------------------------------------- |
-| `posthog:skill-list`      | List all available skills (Level 1 — names + descriptions)  |
-| `posthog:skill-get`       | Fetch a skill by name (Level 2 — body + file manifest)      |
-| `posthog:skill-file-get`  | Fetch a single bundled file by path (Level 3 — on demand)   |
-| `posthog:skill-create`    | Store a new skill (optionally with bundled files)           |
-| `posthog:skill-update`    | Publish a new version (with `base_version` for concurrency) |
-| `posthog:skill-duplicate` | Duplicate an existing skill under a new name                |
+| Tool                        | Purpose                                                    |
+| --------------------------- | ---------------------------------------------------------- |
+| `posthog:skill-list`        | List all available skills (Level 1 — names + descriptions) |
+| `posthog:skill-get`         | Fetch a skill by name (Level 2 — body + file manifest)     |
+| `posthog:skill-file-get`    | Fetch a single bundled file by path (Level 3 — on demand)  |
+| `posthog:skill-create`      | Store a new skill (optionally with bundled files)          |
+| `posthog:skill-update`      | Publish a new version (body, `edits`, or `file_edits`)     |
+| `posthog:skill-file-create` | Add one bundled file to a skill (publishes a new version)  |
+| `posthog:skill-file-delete` | Remove one bundled file from a skill                       |
+| `posthog:skill-file-rename` | Rename one bundled file (move without rewriting content)   |
+| `posthog:skill-duplicate`   | Duplicate an existing skill under a new name               |
 
 Skills use progressive disclosure: discover by description, fetch the body only when relevant, and pull individual files on demand. Do not fetch every file eagerly.
 
@@ -103,14 +106,18 @@ posthog:skill-create
 
 ## Updating a skill
 
-Each `skill-update` publishes a new immutable version. Always fetch first to get the current version, then update with `base_version` for concurrency checks:
+Each write publishes a new immutable version. Always fetch first to get the current version, then update with `base_version` for concurrency checks:
 
 ```json
 posthog:skill-get
 { "skill_name": "make-fractals" }
 ```
 
-Publish a new version. Fields you don't provide are carried forward from the current latest. If you pass `files`, they replace the previous version's file set; if you omit `files`, they're carried forward:
+Pick the most surgical primitive for what you're changing — the API offers several so you don't have to round-trip the whole skill to tweak one part. Anything you don't touch is carried forward from the current latest.
+
+### Editing the body
+
+Full replacement (good for substantial rewrites):
 
 ```json
 posthog:skill-update
@@ -121,6 +128,66 @@ posthog:skill-update
 }
 ```
 
+Incremental find/replace (good for small tweaks — no round-tripping the whole body):
+
+```json
+posthog:skill-update
+{
+  "skill_name": "make-fractals",
+  "edits": [
+    { "old": "Use Pillow for rendering.", "new": "Use Pillow ≥10.0 for rendering." }
+  ],
+  "base_version": 2
+}
+```
+
+Each `edits[].old` must match exactly once. `body` and `edits` are mutually exclusive.
+
+### Editing one bundled file
+
+Use `file_edits` to patch a single file without resending any other file:
+
+```json
+posthog:skill-update
+{
+  "skill_name": "make-fractals",
+  "file_edits": [
+    {
+      "path": "scripts/mandelbrot.py",
+      "edits": [
+        { "old": "ITERATIONS = 100", "new": "ITERATIONS = 250" }
+      ]
+    }
+  ],
+  "base_version": 2
+}
+```
+
+Non-targeted files carry forward unchanged. `file_edits` cannot add, remove, or rename files — use the per-file tools below for that.
+
+### Adding, removing, or renaming a file
+
+Atomic per-file tools — each publishes a new version and returns the updated skill (read its `version` to chain further edits via `base_version`):
+
+```json
+posthog:skill-file-create
+{ "skill_name": "make-fractals", "path": "scripts/julia.py", "content": "...", "base_version": 2 }
+```
+
+```json
+posthog:skill-file-delete
+{ "skill_name": "make-fractals", "file_path": "scripts/old.py", "base_version": 3 }
+```
+
+```json
+posthog:skill-file-rename
+{ "skill_name": "make-fractals", "old_path": "scripts/julia.py", "new_path": "scripts/julia_set.py", "base_version": 4 }
+```
+
+### Replacing the whole bundle (rare)
+
+Passing `files` to `skill-update` replaces ALL bundled files — anything not in the array is dropped. Only use this when you intentionally want to wipe and reseed the bundle. For everything else, prefer `file_edits` or the per-file CRUD tools above.
+
 ## Porting a local skill
 
 To move a skill from a local SKILL.md directory (e.g. a local skills folder with `scripts/`, `references/`, `assets/` subdirs) into PostHog:
@@ -145,7 +212,7 @@ description: >-
   Use when the user asks to list, run, or manage PostHog skills,
   or references /phs, "ph skills", or "posthog skills".
 user-invocable: true
-allowed-tools: mcp__posthog__skill-list, mcp__posthog__skill-get, mcp__posthog__skill-create, mcp__posthog__skill-update, mcp__posthog__skill-file-get, mcp__posthog__skill-duplicate
+allowed-tools: mcp__posthog__skill-list, mcp__posthog__skill-get, mcp__posthog__skill-create, mcp__posthog__skill-update, mcp__posthog__skill-file-get, mcp__posthog__skill-file-create, mcp__posthog__skill-file-delete, mcp__posthog__skill-file-rename, mcp__posthog__skill-duplicate
 ---
 
 # PostHog Skills Store
@@ -169,6 +236,14 @@ skill-list(search="llma") # filter by keyword
 
 skill-create(name="my-skill", description="...", body="# Instructions...")
 skill-get → note version → skill-update(skill_name="...", base_version=N, body="...")
+
+## Edit one part of an existing skill
+
+skill-get → note version → pick the smallest primitive:
+
+- body tweak: skill-update(skill_name="...", base_version=N, edits=[{old, new}])
+- one bundled file: skill-update(skill_name="...", base_version=N, file_edits=[{path, edits:[{old, new}]}])
+- add/remove/rename a file: skill-file-create / skill-file-delete / skill-file-rename
 ```
 
 The bridge is intentionally minimal — it just routes to the MCP tools. The real instructions live in PostHog and update without touching local files.
PATCH

echo "Gold patch applied."
