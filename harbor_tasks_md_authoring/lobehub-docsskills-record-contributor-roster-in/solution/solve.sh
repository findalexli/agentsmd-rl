#!/usr/bin/env bash
set -euo pipefail

cd /workspace/lobehub

# Idempotency guard
if grep -qF "Render contributors as a **single flat list** (no separate \"Community\" / \"Core T" ".agents/skills/version-release/SKILL.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/.agents/skills/version-release/SKILL.md b/.agents/skills/version-release/SKILL.md
@@ -238,13 +238,34 @@ Use `---` separators between major blocks for long releases.
   - Keep concise.
   - Must include `Migration overview`, operator impact, and rollback/backup note.
 
+### Contributor Ordering
+
+Render contributors as a **single flat list** (no separate "Community" / "Core Team" subsections). Order: **community contributors first, team members after**. Within each group, sort by PR count desc. Bots (`@lobehubbot`, `renovate[bot]`) go on a separate "maintenance" line.
+
+**LobeHub team roster** — anyone in this list is a team member; anyone not in this list is a community contributor:
+
+- @arvinxx
+- @Innei
+- @tjx666 (commit author name: YuTengjing)
+- @LiJian
+- @Neko
+- @Rdmclin2
+- @AmAzing129
+- @sudongyuer
+- @rivertwilight
+- @CanisMinor
+
+> **Resolving handles** — git author names (e.g. `YuTengjing`) are not always the GitHub handle. Verify via `gh pr view <PR> --json author` or `gh api search/users -f q='<email>'` before listing.
+
+If a new contributor appears who is not on this list, treat them as community by default and ask the user whether to add them to the roster.
+
 ### GitHub Release Changelog Template
 
 ```md
 # 🚀 LobeHub v<x.y.z> (<YYYYMMDD>)
 
 **Release Date:** <Month DD, YYYY>  
-**Since <Previous Version>:** <N commits> · <N merged PRs> · <N resolved issues> · <N contributors>
+**Since <Previous Version>:** <N merged PRs> · <N resolved issues> · <N contributors>
 
 > <One release thesis sentence: what this release unlocks in practice.>
 
@@ -296,12 +317,11 @@ Use `---` separators between major blocks for long releases.
 
 ## 👥 Contributors
 
-**<N merged PRs>** from **<N contributors>** across **<N commits>**.
+Huge thanks to **<N contributors>** who shipped **<N merged PRs>** this cycle.
 
-### Community Contributors
+@<community-handle> · @<community-handle> · @<team-handle> · @<team-handle>
 
-- @<username> - <notable contribution area>
-- @<username> - <notable contribution area>
+Plus @lobehubbot and renovate[bot] for maintenance.
 
 ---
 
PATCH

echo "Gold patch applied."
