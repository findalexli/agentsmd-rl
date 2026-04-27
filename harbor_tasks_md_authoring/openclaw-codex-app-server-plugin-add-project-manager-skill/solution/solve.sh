#!/usr/bin/env bash
set -euo pipefail

cd /workspace/openclaw-codex-app-server

# Idempotency guard
if grep -qF "- GitHub Projects custom views are not well-supported by `gh` or GraphQL mutatio" ".agents/skills/project-manager/SKILL.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/.agents/skills/project-manager/SKILL.md b/.agents/skills/project-manager/SKILL.md
@@ -22,6 +22,7 @@ Use this skill for repo-specific project management on [OpenClaw Codex App Serve
 
 Current repo-specific locations:
 
+- Canonical repo: `pwrdrvr/openclaw-codex-app-server`
 - Project board: `https://github.com/orgs/pwrdrvr/projects/7`
 - Local tracker: `.local/work-items.yaml`
 - Issue drafts: `.local/issue-drafts/`
@@ -53,12 +54,13 @@ pnpm project:sync
 4. Add the issue or PR to project `7`.
 
 - Use `gh project item-add 7 --owner pwrdrvr --url <issue-or-pr-url>`.
-- Set `Status`, `Priority`, `Size`, and `Workflow`.
+- For issues, set `Status`, `Priority`, `Size`, and `Workflow`.
+- For PRs, usually set `Status` and `Workflow`; `Priority` and `Size` are issue-planning fields unless there is a specific reason to set them on the PR item.
 
 5. Sync `.local/work-items.yaml`.
 
-- Add or update the item entry with issue number, URLs, project item id, workflow, status, priority, size, and concise notes.
-- Update `last_synced_at` whenever the tracker changes.
+- Treat the tracker as derived state, not a hand-edited source of truth.
+- Regenerate it with `pnpm project:sync` after issue/project changes.
 - Prefer pushing durable notes into GitHub issues or `.local/issue-drafts/`; the tracker should stay compact.
 
 6. Reconcile if anything drifted.
@@ -88,6 +90,8 @@ Size heuristic:
 Start by discovering current project field ids instead of assuming they never change:
 
 ```bash
+gh repo view --json nameWithOwner,url
+gh project view 7 --owner pwrdrvr --format json
 gh project field-list 7 --owner pwrdrvr --format json
 ```
 
@@ -106,6 +110,14 @@ Refresh the local tracker:
 pnpm project:sync
 ```
 
+## Gotchas
+
+- Verify the repo slug before issue commands. The canonical repo is `pwrdrvr/openclaw-codex-app-server`; older shorthand like `pwrdrvr/openclaw-app-server` is wrong and will make `gh issue ...` fail.
+- `gh project item-edit` needs opaque ids for the project, item, field, and single-select option. Always discover them with `gh project view ...` and `gh project field-list ...` instead of assuming cached ids still match.
+- GitHub Projects custom views are not well-supported by `gh` or GraphQL mutations. Reading views works, but creating/editing/copying views is still better done in the web UI or browser automation. `gh project copy` does not carry over custom views.
+- `.local/work-items.yaml` is currently issue-only. Add PRs to project `7`, but do not expect `pnpm project:sync` to mirror PR items into the local tracker.
+- `.local/issue-drafts/<nn>-<slug>.md` filenames are local scratch ids, not GitHub issue numbers. Keep them stable enough to reuse, but do not try to force them to match the eventual GitHub issue number.
+
 ## Tracker Shape
 
 Each `.local/work-items.yaml` item should keep:
PATCH

echo "Gold patch applied."
