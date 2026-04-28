#!/usr/bin/env bash
set -euo pipefail

cd /workspace/lobehub

# Idempotency guard
if grep -qF "- **Stale topic on agent switch** \u2014 Switching from `/agent/agt_A/tpc_X` to `/age" ".agents/skills/version-release/reference/changelog-example/hotfix.md" && grep -qF "3. **Write a short hotfix changelog** \u2014 See `changelog-example/hotfix.md`. Keep " ".agents/skills/version-release/reference/patch-release-scenarios.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/.agents/skills/version-release/reference/changelog-example/hotfix.md b/.agents/skills/version-release/reference/changelog-example/hotfix.md
@@ -0,0 +1,21 @@
+# 🚀 LobeHub v2.1.54 (20260427)
+
+**Hotfix Scope:** Agent topic-switching regression — stale chat state on agent change
+
+> Clears residual topic state when navigating between agents and restores blank-canvas behavior on agent switch.
+
+## 🐛 What's Fixed
+
+- **Stale topic on agent switch** — Switching from `/agent/agt_A/tpc_X` to `/agent/agt_B` no longer leaves the previous topic's messages on screen, and _Start new topic_ responds again. (#14231)
+- **Header & sidebar consistency** — Conversation header now shows the active subtopic's title, and the sidebar keeps the parent topic's thread list expanded while a thread is open.
+
+## ⚙️ Upgrade
+
+- Self-hosted: pull the new image and restart. No schema or env changes.
+- Cloud: applied automatically.
+
+## 👥 Owner
+
+@{pr-author}
+
+> **Note for Claude**: Replace `{pr-author}` with the actual PR author. Retrieve via `gh pr view <number> --json author --jq '.author.login'`. Do not hardcode a username.
diff --git a/.agents/skills/version-release/reference/patch-release-scenarios.md b/.agents/skills/version-release/reference/patch-release-scenarios.md
@@ -59,7 +59,10 @@ git push -u origin hotfix/v{version}-{short-hash}
 
 2. **Create PR to main** with a gitmoji prefix title (e.g. `🐛 fix: description`)
 
-3. **After merge**: auto-tag-release detects `hotfix/*` branch → auto patch +1.
+3. **Write a short hotfix changelog** — See `changelog-example/hotfix.md`. Keep it minimal: scope line, 1-3 fix bullets (symptom + fix in one sentence), upgrade note, owner. No long root-cause section — that lives in the commit message.
+   - **Hotfix owner**: Use the actual PR author (retrieve via `gh pr view <number> --json author --jq '.author.login'`), never hardcode a username.
+
+4. **After merge**: auto-tag-release detects `hotfix/*` branch → auto patch +1.
 
 ### Script
 
PATCH

echo "Gold patch applied."
