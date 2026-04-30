#!/usr/bin/env bash
set -euo pipefail

cd /workspace/openai-agents-js

# Idempotency guard: skip if already applied
if grep -q 'name: pnpm-upgrade' .codex/skills/pnpm-upgrade/SKILL.md 2>/dev/null; then
    echo "Patch already applied, skipping."
    exit 0
fi

git apply --verbose <<'PATCH'
diff --git a/.codex/skills/pnpm-upgrade/SKILL.md b/.codex/skills/pnpm-upgrade/SKILL.md
new file mode 100644
index 000000000..869bf3346
--- /dev/null
+++ b/.codex/skills/pnpm-upgrade/SKILL.md
@@ -0,0 +1,43 @@
+---
+name: pnpm-upgrade
+description: 'Keep pnpm current: run pnpm self-update/corepack prepare, align packageManager in package.json, and bump pnpm/action-setup + pinned pnpm versions in .github/workflows to the latest release. Use this when refreshing the pnpm toolchain manually or in automation.'
+---
+
+# pnpm Upgrade
+
+Use these steps to update pnpm and CI pins without blunt search/replace.
+
+## Steps (run from repo root)
+
+1. Update pnpm locally
+   - Try `pnpm self-update`; if pnpm is missing or self-update fails, run `corepack prepare pnpm@latest --activate`.
+   - Capture the resulting version as `PNPM_VERSION=$(pnpm -v)`.
+
+2. Align package.json
+   - Open `package.json` and set `packageManager` to `pnpm@${PNPM_VERSION}` (preserve trailing newline and formatting).
+
+3. Find latest pnpm/action-setup tag
+   - Query GitHub API: `curl -fsSL https://api.github.com/repos/pnpm/action-setup/releases/latest | jq -r .tag_name`.
+   - Use `GITHUB_TOKEN`/`GH_TOKEN` if available for higher rate limits.
+   - Store as `ACTION_TAG` (e.g., `v4.2.0`). Abort if missing.
+
+4. Update workflows carefully (no broad regex)
+   - Files: everything under `.github/workflows/` that uses `pnpm/action-setup`.
+   - For each file, edit by hand:
+     - Set `uses: pnpm/action-setup@${ACTION_TAG}`.
+     - If a `with: version:` field exists, set it to `${PNPM_VERSION}` (keep quoting style/indent).
+   - Do not touch unrelated steps. Avoid multiline sed/perl one-liners.
+
+5. Verify
+   - Run `pnpm -v` and confirm it matches `packageManager`.
+   - `git diff` to ensure only intended workflow/package.json changes.
+
+6. Follow-up
+   - If runtime code/build/test config was changed (not typical here), run `$code-change-verification`; otherwise, a light check is enough.
+   - Commit with `chore: upgrade pnpm toolchain` and open a PR (automation may do this).
+
+## Notes
+
+- Tools needed: `curl`, `jq`, `node`, `pnpm`/`corepack`. Install if missing.
+- Keep edits minimal and readable—prefer explicit file edits over global replacements.
+- If GitHub API is rate-limited, retry with a token or bail out rather than guessing the tag.
diff --git a/.github/codex/prompts/pnpm-upgrade.md b/.github/codex/prompts/pnpm-upgrade.md
new file mode 100644
index 000000000..de633c355
--- /dev/null
+++ b/.github/codex/prompts/pnpm-upgrade.md
@@ -0,0 +1,9 @@
+You are running in CI for the scheduled pnpm toolchain refresh.
+
+Follow the `$pnpm-upgrade` skill instructions from the repo root. Key points:
+
+- Update pnpm via `pnpm self-update` (or `corepack prepare pnpm@latest --activate`), record PNPM_VERSION.
+- Update `package.json` packageManager to match.
+- Fetch the latest `pnpm/action-setup` tag via GitHub API; use it when editing workflows.
+- Manually edit each workflow that uses pnpm/action-setup to set the tag and pnpm version (no blanket regex replacements).
+- Do not commit or push; leave changes unstaged. Keep output brief; tests are not required.
diff --git a/.github/workflows/changeset.yml b/.github/workflows/changeset.yml
index bbec7e643..7b307d8a2 100644
--- a/.github/workflows/changeset.yml
+++ b/.github/workflows/changeset.yml
@@ -18,7 +18,7 @@ jobs:
           fetch-depth: 0
           ref: ${{ github.event.pull_request.head.sha }}
       - name: Install pnpm
-        uses: pnpm/action-setup@v4
+        uses: pnpm/action-setup@v4.2.0
         with:
           version: 10.28.0
           run_install: false
diff --git a/.github/workflows/docs.yml b/.github/workflows/docs.yml
index 17e0ad7df..ee73b8cca 100644
--- a/.github/workflows/docs.yml
+++ b/.github/workflows/docs.yml
@@ -20,9 +20,10 @@ jobs:
         uses: actions/checkout@v6
       - name: Setup Node.js
         uses: actions/setup-node@v6
-      - name: Install dependencies
-        uses: pnpm/action-setup@v4
+      - name: Install pnpm
+        uses: pnpm/action-setup@v4.2.0
         with:
+          version: 10.28.0
           run_install: true
       - name: Run build
         run: pnpm build
diff --git a/.github/workflows/pnpm-upgrade.yml b/.github/workflows/pnpm-upgrade.yml
new file mode 100644
index 000000000..007395737
--- /dev/null
+++ b/.github/workflows/pnpm-upgrade.yml
@@ -0,0 +1,63 @@
+name: pnpm upgrade
+
+on:
+  schedule:
+    - cron: '0 8 * * *'
+  workflow_dispatch:
+
+permissions:
+  contents: write
+  pull-requests: write
+
+concurrency:
+  group: pnpm-upgrade
+  cancel-in-progress: false
+
+jobs:
+  pnpm-upgrade:
+    runs-on: ubuntu-latest
+    env:
+      GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
+    steps:
+      - name: Checkout repository
+        uses: actions/checkout@v6
+
+      - name: Setup Node.js
+        uses: actions/setup-node@v6
+        with:
+          node-version: 22
+          cache: 'pnpm'
+
+      - name: Enable Corepack
+        run: corepack enable
+
+      - name: Install jq
+        run: sudo apt-get update && sudo apt-get install -y jq
+
+      - name: Run pnpm-upgrade skill
+        id: codex
+        uses: openai/codex-action@v1
+        with:
+          openai-api-key: ${{ secrets.PROD_OPENAI_API_KEY }}
+          prompt-file: .github/codex/prompts/pnpm-upgrade.md
+          sandbox: danger-full-access
+          safety-strategy: drop-sudo
+          codex-args: --skill pnpm-upgrade --full-auto --max-steps 200
+
+      - name: Create pull request
+        if: ${{ success() }}
+        uses: peter-evans/create-pull-request@v8
+        with:
+          token: ${{ secrets.GITHUB_TOKEN }}
+          commit-message: "chore: upgrade pnpm toolchain"
+          branch: automation/pnpm-upgrade
+          title: "chore: upgrade pnpm toolchain"
+          body: |
+            Automated pnpm upgrade run.
+
+            - updates pnpm via pnpm self-update and aligns packageManager
+            - bumps pnpm/action-setup pins in workflows
+            - opened by scheduled Codex run if changes exist
+          labels: automation,pnpm
+          signoff: true
+          draft: false
diff --git a/.github/workflows/release.yml b/.github/workflows/release.yml
index d3a3eb3c0..ea924db35 100644
--- a/.github/workflows/release.yml
+++ b/.github/workflows/release.yml
@@ -25,7 +25,9 @@ jobs:
         uses: actions/checkout@v6

       - name: Setup pnpm
-        uses: pnpm/action-setup@v4
+        uses: pnpm/action-setup@v4.2.0
+        with:
+          version: 10.28.0

       - name: Setup node.js
         uses: actions/setup-node@v6
diff --git a/.github/workflows/test.yml b/.github/workflows/test.yml
index 9f830b02a..40f9c04e3 100644
--- a/.github/workflows/test.yml
+++ b/.github/workflows/test.yml
@@ -19,7 +19,7 @@ jobs:
       - name: Checkout repository
         uses: actions/checkout@v6
       - name: Install pnpm
-        uses: pnpm/action-setup@v4
+        uses: pnpm/action-setup@v4.2.0
         with:
           version: 10.28.0
           run_install: false
diff --git a/.github/workflows/update-docs.yml b/.github/workflows/update-docs.yml
index 2ad341614..d631c5a8e 100644
--- a/.github/workflows/update-docs.yml
+++ b/.github/workflows/update-docs.yml
@@ -38,7 +38,7 @@ jobs:
         with:
           fetch-depth: 0
       - name: Install pnpm
-        uses: pnpm/action-setup@v4
+        uses: pnpm/action-setup@v4.2.0
         with:
           version: 10.28.0
           run_install: false
PATCH
