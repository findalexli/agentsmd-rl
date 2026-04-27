#!/usr/bin/env bash
set -euo pipefail

cd /workspace/libretto

# Idempotency guard
if grep -qF "- Available globals: `page`, `context`, `browser`, `state`, `networkLog(opts?)`," ".agents/skills/libretto/SKILL.md" && grep -qF "- Available globals: `page`, `context`, `browser`, `state`, `networkLog(opts?)`," ".claude/skills/libretto/SKILL.md" && grep -qF "- Available globals: `page`, `context`, `browser`, `state`, `networkLog(opts?)`," "skills/libretto/SKILL.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/.agents/skills/libretto/SKILL.md b/.agents/skills/libretto/SKILL.md
@@ -35,6 +35,11 @@ metadata:
 - Never run multiple `exec` commands at the same time.
 - Keep the browser session open until the user says the session is done.
 
+## Session Storage
+
+- Session state is stored in `.libretto/sessions/<session>/state.json`.
+- CLI logs are stored in `.libretto/sessions/<session>/logs.jsonl`.
+
 ## Commands
 
 ### `open`
@@ -81,13 +86,14 @@ npx libretto snapshot \
 
 - Use `exec` for focused inspection and short-lived interaction experiments.
 - Use `exec` to validate selectors, inspect data, or prototype a step before you encode it in the workflow file.
+- Available globals: `page`, `context`, `browser`, `state`, `networkLog(opts?)`, `actionLog(opts?)`, `fetch`, `Buffer`.
 - Let failures throw. Do not hide `exec` failures with `try/catch` or `.catch()`.
 - Do not run multiple `exec` commands in parallel.
 
 ```bash
 npx libretto exec "return await page.url()"
 npx libretto exec "return await page.locator('button').count()"
-npx libretto exec --visualize "await page.locator('button:has-text(\"Continue\")').click()"
+npx libretto exec "await page.locator('button:has-text(\"Continue\")').click()"
 ```
 
 ### `pages`
@@ -105,21 +111,25 @@ npx libretto exec --session debug-example --page <page-id> "return await page.ur
 - Use `network` to inspect the requests the page already made.
 - Prefer this when discovering how a site loads data or when validating whether a network-first approach is workable.
 - Filter aggressively by method, URL pattern, and page when the log is noisy.
+- Use `--clear` to reset the network log before reproducing an issue.
 
 ```bash
 npx libretto network --session debug-example --last 20
 npx libretto network --session debug-example --method POST --filter 'referral|patient'
 npx libretto network --session debug-example --page <page-id>
+npx libretto network --session debug-example --clear
 ```
 
 ### `actions`
 
 - Use `actions` when you need a quick record of recent user or agent interactions in the current session.
 - Keep it lightweight. It is a helper for orientation, not the main integration-building workflow.
+- Use `--clear` to reset the action log before reproducing an issue.
 
 ```bash
 npx libretto actions --session debug-example --last 20
 npx libretto actions --session debug-example --action click --source user
+npx libretto actions --session debug-example --clear
 ```
 
 ### `run`
@@ -128,6 +138,7 @@ npx libretto actions --session debug-example --action click --source user
 - If the workflow fails, Libretto keeps the browser open. Inspect the failed state with `snapshot` and `exec` before editing code.
 - If the workflow pauses, resume it with `npx libretto resume --session <name>`.
 - Re-run the same workflow after each fix to verify the browser behavior end to end.
+- By default in headed mode, a ghost cursor and element highlights are shown. Use `--no-visualize` to disable.
 
 ```bash
 npx libretto run ./integration.ts main
@@ -137,8 +148,9 @@ npx libretto run ./integration.ts main --auth-profile app.example.com --headed
 
 ### `resume`
 
-- Workflows pause by calling `await pause()` in the workflow file.
-- Use `resume` when a workflow hit `await pause()`.
+- Workflows pause by calling `await pause("session-name")` in the workflow file. Import `pause` from `"libretto"`.
+- `pause(session)` is a no-op when `NODE_ENV === "production"`.
+- Use `resume` when a workflow hit a `pause()` call.
 - Keep resuming the same session until the workflow completes or pauses again.
 
 ```bash
diff --git a/.claude/skills/libretto/SKILL.md b/.claude/skills/libretto/SKILL.md
@@ -35,6 +35,11 @@ metadata:
 - Never run multiple `exec` commands at the same time.
 - Keep the browser session open until the user says the session is done.
 
+## Session Storage
+
+- Session state is stored in `.libretto/sessions/<session>/state.json`.
+- CLI logs are stored in `.libretto/sessions/<session>/logs.jsonl`.
+
 ## Commands
 
 ### `open`
@@ -81,13 +86,14 @@ npx libretto snapshot \
 
 - Use `exec` for focused inspection and short-lived interaction experiments.
 - Use `exec` to validate selectors, inspect data, or prototype a step before you encode it in the workflow file.
+- Available globals: `page`, `context`, `browser`, `state`, `networkLog(opts?)`, `actionLog(opts?)`, `fetch`, `Buffer`.
 - Let failures throw. Do not hide `exec` failures with `try/catch` or `.catch()`.
 - Do not run multiple `exec` commands in parallel.
 
 ```bash
 npx libretto exec "return await page.url()"
 npx libretto exec "return await page.locator('button').count()"
-npx libretto exec --visualize "await page.locator('button:has-text(\"Continue\")').click()"
+npx libretto exec "await page.locator('button:has-text(\"Continue\")').click()"
 ```
 
 ### `pages`
@@ -105,21 +111,25 @@ npx libretto exec --session debug-example --page <page-id> "return await page.ur
 - Use `network` to inspect the requests the page already made.
 - Prefer this when discovering how a site loads data or when validating whether a network-first approach is workable.
 - Filter aggressively by method, URL pattern, and page when the log is noisy.
+- Use `--clear` to reset the network log before reproducing an issue.
 
 ```bash
 npx libretto network --session debug-example --last 20
 npx libretto network --session debug-example --method POST --filter 'referral|patient'
 npx libretto network --session debug-example --page <page-id>
+npx libretto network --session debug-example --clear
 ```
 
 ### `actions`
 
 - Use `actions` when you need a quick record of recent user or agent interactions in the current session.
 - Keep it lightweight. It is a helper for orientation, not the main integration-building workflow.
+- Use `--clear` to reset the action log before reproducing an issue.
 
 ```bash
 npx libretto actions --session debug-example --last 20
 npx libretto actions --session debug-example --action click --source user
+npx libretto actions --session debug-example --clear
 ```
 
 ### `run`
@@ -128,6 +138,7 @@ npx libretto actions --session debug-example --action click --source user
 - If the workflow fails, Libretto keeps the browser open. Inspect the failed state with `snapshot` and `exec` before editing code.
 - If the workflow pauses, resume it with `npx libretto resume --session <name>`.
 - Re-run the same workflow after each fix to verify the browser behavior end to end.
+- By default in headed mode, a ghost cursor and element highlights are shown. Use `--no-visualize` to disable.
 
 ```bash
 npx libretto run ./integration.ts main
@@ -137,8 +148,9 @@ npx libretto run ./integration.ts main --auth-profile app.example.com --headed
 
 ### `resume`
 
-- Workflows pause by calling `await pause()` in the workflow file.
-- Use `resume` when a workflow hit `await pause()`.
+- Workflows pause by calling `await pause("session-name")` in the workflow file. Import `pause` from `"libretto"`.
+- `pause(session)` is a no-op when `NODE_ENV === "production"`.
+- Use `resume` when a workflow hit a `pause()` call.
 - Keep resuming the same session until the workflow completes or pauses again.
 
 ```bash
diff --git a/skills/libretto/SKILL.md b/skills/libretto/SKILL.md
@@ -35,6 +35,11 @@ metadata:
 - Never run multiple `exec` commands at the same time.
 - Keep the browser session open until the user says the session is done.
 
+## Session Storage
+
+- Session state is stored in `.libretto/sessions/<session>/state.json`.
+- CLI logs are stored in `.libretto/sessions/<session>/logs.jsonl`.
+
 ## Commands
 
 ### `open`
@@ -81,13 +86,14 @@ npx libretto snapshot \
 
 - Use `exec` for focused inspection and short-lived interaction experiments.
 - Use `exec` to validate selectors, inspect data, or prototype a step before you encode it in the workflow file.
+- Available globals: `page`, `context`, `browser`, `state`, `networkLog(opts?)`, `actionLog(opts?)`, `fetch`, `Buffer`.
 - Let failures throw. Do not hide `exec` failures with `try/catch` or `.catch()`.
 - Do not run multiple `exec` commands in parallel.
 
 ```bash
 npx libretto exec "return await page.url()"
 npx libretto exec "return await page.locator('button').count()"
-npx libretto exec --visualize "await page.locator('button:has-text(\"Continue\")').click()"
+npx libretto exec "await page.locator('button:has-text(\"Continue\")').click()"
 ```
 
 ### `pages`
@@ -105,21 +111,25 @@ npx libretto exec --session debug-example --page <page-id> "return await page.ur
 - Use `network` to inspect the requests the page already made.
 - Prefer this when discovering how a site loads data or when validating whether a network-first approach is workable.
 - Filter aggressively by method, URL pattern, and page when the log is noisy.
+- Use `--clear` to reset the network log before reproducing an issue.
 
 ```bash
 npx libretto network --session debug-example --last 20
 npx libretto network --session debug-example --method POST --filter 'referral|patient'
 npx libretto network --session debug-example --page <page-id>
+npx libretto network --session debug-example --clear
 ```
 
 ### `actions`
 
 - Use `actions` when you need a quick record of recent user or agent interactions in the current session.
 - Keep it lightweight. It is a helper for orientation, not the main integration-building workflow.
+- Use `--clear` to reset the action log before reproducing an issue.
 
 ```bash
 npx libretto actions --session debug-example --last 20
 npx libretto actions --session debug-example --action click --source user
+npx libretto actions --session debug-example --clear
 ```
 
 ### `run`
@@ -128,6 +138,7 @@ npx libretto actions --session debug-example --action click --source user
 - If the workflow fails, Libretto keeps the browser open. Inspect the failed state with `snapshot` and `exec` before editing code.
 - If the workflow pauses, resume it with `npx libretto resume --session <name>`.
 - Re-run the same workflow after each fix to verify the browser behavior end to end.
+- By default in headed mode, a ghost cursor and element highlights are shown. Use `--no-visualize` to disable.
 
 ```bash
 npx libretto run ./integration.ts main
@@ -137,8 +148,9 @@ npx libretto run ./integration.ts main --auth-profile app.example.com --headed
 
 ### `resume`
 
-- Workflows pause by calling `await pause()` in the workflow file.
-- Use `resume` when a workflow hit `await pause()`.
+- Workflows pause by calling `await pause("session-name")` in the workflow file. Import `pause` from `"libretto"`.
+- `pause(session)` is a no-op when `NODE_ENV === "production"`.
+- Use `resume` when a workflow hit a `pause()` call.
 - Keep resuming the same session until the workflow completes or pauses again.
 
 ```bash
PATCH

echo "Gold patch applied."
