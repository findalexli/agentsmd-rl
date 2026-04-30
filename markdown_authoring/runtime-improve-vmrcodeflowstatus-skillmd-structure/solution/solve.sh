#!/usr/bin/env bash
set -euo pipefail

cd /workspace/runtime

# Idempotency guard
if grep -qF "description: Analyze VMR codeflow PR status for dotnet repositories. Use when in" ".github/skills/vmr-codeflow-status/SKILL.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/.github/skills/vmr-codeflow-status/SKILL.md b/.github/skills/vmr-codeflow-status/SKILL.md
@@ -1,6 +1,6 @@
 ---
 name: vmr-codeflow-status
-description: Analyze VMR codeflow PR status for dotnet repositories. Use when investigating stale codeflow PRs, checking if fixes have flowed through the VMR pipeline, or debugging dependency update issues in PRs authored by dotnet-maestro[bot].
+description: Analyze VMR codeflow PR status for dotnet repositories. Use when investigating stale codeflow PRs, checking if fixes have flowed through the VMR pipeline, debugging dependency update issues in PRs authored by dotnet-maestro[bot], checking overall flow status for a repo, or diagnosing why backflow PRs are missing or blocked.
 ---
 
 # VMR Codeflow Status
@@ -9,6 +9,8 @@ Analyze the health of VMR codeflow PRs in both directions:
 - **Backflow**: `dotnet/dotnet` → product repos (e.g., `dotnet/sdk`)
 - **Forward flow**: product repos → `dotnet/dotnet`
 
+> 🚨 **NEVER** use `gh pr review --approve` or `--request-changes`. Only `--comment` is allowed. Approval and blocking are human-only actions.
+
 ## Prerequisites
 
 - **GitHub CLI (`gh`)** — must be installed and authenticated (`gh auth login`)
@@ -22,7 +24,17 @@ Use this skill when:
 - A PR has a Maestro staleness warning ("codeflow cannot continue") or conflict
 - You need to understand what manual commits would be lost if a codeflow PR is closed
 - You want to check the overall state of flow for a repo (backflow and forward flow health)
-- Asked questions like "is this codeflow PR up to date", "has the runtime revert reached this PR", "why is the codeflow blocked", "what is the state of flow for the sdk"
+- You need to know why backflow PRs are missing or when the last VMR build was published
+- You're asked questions like "is this codeflow PR up to date", "has the runtime revert reached this PR", "why is the codeflow blocked", "what is the state of flow for the sdk", "what's the flow status for net11"
+
+## Two Modes
+
+| Mode | Use When | Required Params |
+|------|----------|-----------------|
+| **PR analysis** | Investigating a specific codeflow PR | `-PRNumber` (and optionally `-Repository`) |
+| **Flow health** (`-CheckMissing`) | Checking overall repo flow status | `-CheckMissing` (optional: `-Repository`, `-Branch`) |
+
+> ⚠️ **Common mistake**: Don't use `-PRNumber` and `-CheckMissing` together — they are separate modes. `-CheckMissing` scans branches discovered from open and recent backflow PRs (unless `-Branch` is provided), not a specific PR.
 
 ## Quick Start
 
@@ -56,17 +68,25 @@ Use this skill when:
 
 ## What the Script Does
 
+### PR Analysis Mode (default)
 1. **Parses PR metadata** — Extracts VMR commit, subscription ID, build info from PR body
 2. **Validates snapshot** — Cross-references PR body commit against branch commit messages to detect stale metadata
 3. **Checks VMR freshness** — Compares PR's VMR snapshot against current VMR branch HEAD
 4. **Shows pending forward flow** — For behind backflow PRs, finds open forward flow PRs that would close part of the gap
 5. **Detects staleness & conflicts** — Finds Maestro "codeflow cannot continue" warnings and "Conflict detected" messages with file lists and resolve commands
 6. **Analyzes PR commits** — Categorizes as auto-updates vs manual commits
-7. **Traces fixes** (optional) — Checks if a specific fix has flowed through VMR → codeflow PR
+7. **Traces fixes** (with `-TraceFix`) — Checks if a specific fix has flowed through VMR → codeflow PR
 8. **Recommends actions** — Suggests force trigger, close/reopen, merge as-is, resolve conflicts, or wait
-9. **Checks for missing backflow** (optional) — Finds branches where a backflow PR should exist but doesn't
-10. **Scans forward flow** (optional) — Checks open forward flow PRs into `dotnet/dotnet` for staleness and conflicts
-11. **Checks official build freshness** (optional) — When missing backflow is detected, queries `aka.ms` shortlinks to check when the last successful VMR build was published, helping diagnose whether Maestro is stuck or the VMR build is broken
+
+### Flow Health Mode (`-CheckMissing`)
+1. **Checks official build freshness** — Queries `aka.ms` shortlinks for latest published VMR build dates per channel
+2. **Scans backflow PRs** — Finds branches where a backflow PR should exist but doesn't, and checks health of open PRs (conflict/staleness/resolved status)
+3. **Scans forward flow** — Checks open forward flow PRs into `dotnet/dotnet` for staleness and conflicts
+4. **Produces summary** — Counts healthy/blocked/missing PRs across both directions
+
+> ❌ **Never assume "Unknown" health means healthy.** When `gh` API calls fail (auth, rate limiting), the script returns "Unknown" status — this is explicitly excluded from healthy/covered counts.
+
+> ⚠️ **aka.ms redirect behavior**: 301 is expected and treated as a valid product URL (→ ci.dot.net). Non-301 redirects (often 302, which goes to Bing) indicate an invalid URL. The script only accepts 301.
 
 ## Interpreting Results
 
PATCH

echo "Gold patch applied."
