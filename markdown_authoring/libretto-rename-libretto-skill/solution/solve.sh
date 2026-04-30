#!/usr/bin/env bash
set -euo pipefail

cd /workspace/libretto

# Idempotency guard
if grep -qF "name: libretto" ".agents/skills/libretto/SKILL.md" && grep -qF "2. If GitHub returns `no checks reported`, treat it as possible propagation dela" ".agents/skills/push/SKILL.md" && grep -qF "name: libretto" "packages/libretto/skill/SKILL.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/.agents/skills/libretto/SKILL.md b/.agents/skills/libretto/SKILL.md
@@ -1,5 +1,5 @@
 ---
-name: libretto-network-skill
+name: libretto
 description: "Browser automation CLI for building integrations, with a network-first approach.\n\nWHEN TO USE THIS SKILL:\n- When building a new integration or data extraction workflow against a website\n- When you need to interact with a web page (click, fill, navigate) rather than just read it\n- When debugging browser agent job failures (selectors timing out, clicks not working, elements not found)\n- When you need to test or prototype Playwright interactions before codifying them\n- When you need to save or restore login sessions for authenticated pages\n- When you need to understand what's on a page (use the snapshot command)\n- When scraping dynamic content that requires JavaScript execution\n\nWHEN NOT TO USE THIS SKILL:\n- When you only need to read static web content (use read_web_page instead)\n- When you need to modify browser agent source code (edit files directly)\n- When you need to run a full browser agent job end-to-end (use npx browser-agent CLI)"
 ---
 
diff --git a/.agents/skills/push/SKILL.md b/.agents/skills/push/SKILL.md
@@ -45,10 +45,11 @@ Do not report completion to the user until all required GitHub PR checks pass.
 
 After every push:
 
-1. Watch the PR checks with `gh pr checks --watch`.
-2. Wait for all required checks to complete.
-3. If any test or type-check command fails, inspect logs immediately, fix the issue, commit, push, and repeat this CI loop until checks pass.
-4. If checks are blocked on AI review bots, wait for bot completion and read all bot reviews before reporting completion.
+1. Watch PR checks with `gh pr checks --watch`.
+2. If GitHub returns `no checks reported`, treat it as possible propagation delay. Wait 15 seconds and retry `gh pr checks --watch`. Repeat up to 8 times (about 2 minutes total) before concluding there are no checks configured.
+3. Once checks appear, wait for all required checks to complete.
+4. If any test or type-check command fails, inspect logs immediately, fix the issue, commit, push, and repeat this CI loop until checks pass.
+5. If checks are blocked on AI review bots, wait for bot completion and read all bot reviews before reporting completion.
 
 AI review bot handling:
 
diff --git a/packages/libretto/skill/SKILL.md b/packages/libretto/skill/SKILL.md
@@ -1,5 +1,5 @@
 ---
-name: libretto-network-skill
+name: libretto
 description: "Browser automation CLI for building integrations, with a network-first approach.\n\nWHEN TO USE THIS SKILL:\n- When building a new integration or data extraction workflow against a website\n- When you need to interact with a web page (click, fill, navigate) rather than just read it\n- When debugging browser agent job failures (selectors timing out, clicks not working, elements not found)\n- When you need to test or prototype Playwright interactions before codifying them\n- When you need to save or restore login sessions for authenticated pages\n- When you need to understand what's on a page (use the snapshot command)\n- When scraping dynamic content that requires JavaScript execution\n\nWHEN NOT TO USE THIS SKILL:\n- When you only need to read static web content (use read_web_page instead)\n- When you need to modify browser agent source code (edit files directly)\n- When you need to run a full browser agent job end-to-end (use npx browser-agent CLI)"
 ---
 
PATCH

echo "Gold patch applied."
