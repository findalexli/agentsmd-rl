#!/usr/bin/env bash
set -euo pipefail

cd /workspace/libretto

# Idempotency guard
if grep -qF "Sessions start in **read-only mode** by default. **Every time you launch a brows" ".agents/skills/libretto/SKILL.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/.agents/skills/libretto/SKILL.md b/.agents/skills/libretto/SKILL.md
@@ -7,6 +7,36 @@ description: "Browser automation CLI for building integrations, with a network-f
 
 Use the `npx libretto` CLI to automate web interactions, debug browser agent jobs, and prototype fixes interactively.
 
+## CRITICAL: Session Modes
+
+Sessions start in **read-only mode** by default. **Every time you launch a browser — whether via `open` or `run` — you MUST immediately announce the session mode.** This is non-negotiable. Do NOT skip the announcement. Do NOT abbreviate it.
+
+### Read-only mode (default)
+
+> **Session mode: READ-ONLY**
+>
+> I've opened the browser in **read-only mode**. I can observe the page, take snapshots, and inspect network traffic, but I **cannot** click, type, fill forms, submit, or execute any actions that modify the page.
+>
+> If you'd like me to interact with elements (clicking buttons, filling forms, submitting data, scrolling, or making network requests), let me know and I'll switch to **full-access mode**.
+
+**Rules:**
+- Use ONLY read-only-safe commands (`snapshot`, `network`, `actions`) until the user explicitly grants full access.
+- Do NOT proceed with any `exec` or `run` commands until the user explicitly grants full access.
+
+### Full-access mode (user-approved)
+
+> **Session mode: FULL-ACCESS**
+>
+> I've opened the browser in **full-access mode**. I have full control to click, type, fill forms, navigate, scroll, make network requests, and execute Playwright commands on the page.
+>
+> If you'd like me to switch to **read-only mode** (observe only, no page modifications), let me know.
+
+### Switching modes
+
+- When the user requests full-access mode, run `npx libretto session-mode full-access --session <name>` and then proceed with `exec`/`run`.
+- Never change session mode unless the user explicitly approves.
+- If the user says something like "go ahead", "interact", "click around", or "do whatever you need" — that counts as granting full access. Switch the mode and confirm.
+
 ## Ask, Don't Guess
 
 If it's not obvious which element to click or what value to enter, **ask the user** — don't try multiple things hoping one works. Present what you see on the page and let the user tell you where to go. One question is faster than a 30-second timeout from a wrong guess.
@@ -17,7 +47,7 @@ If it's not obvious which element to click or what value to enter, **ask the use
 npx libretto open <url> [--headed]     # Launch browser and navigate (headless by default)
 npx libretto exec <code> [--visualize] # Execute Playwright TypeScript code (--visualize enables ghost cursor + highlight)
 npx libretto run <integrationFile> <integrationExport> # Execute integration actions
-npx libretto session-mode <read-only|interactive> [--session <name>] # Set session mode explicitly
+npx libretto session-mode <read-only|full-access> [--session <name>] # Set session mode explicitly
 npx libretto snapshot --objective "<what to find>" --context "<situational info>"
 npx libretto save <url|domain>         # Save session (cookies, localStorage) to .libretto-cli/profiles/
 npx libretto network                   # Show last 20 captured network requests
@@ -28,16 +58,6 @@ npx libretto close                     # Close the browser
 All commands accept `--session <name>` for isolated browser instances (default: `default`).
 Built-in sessions: `default`, `dev-server`, `browser-agent`.
 
-## Session Mode: Read-Only by Default
-
-Sessions start in **read-only mode** by default. When opening a browser, tell the user:
-
-> "Starting in read-only mode — I'll observe the page without clicking or making requests. If you'd like me to interact with elements (click, fill, submit) or make network requests, let me know and I'll switch to interactive mode."
-
-- Use read-only-safe commands (`snapshot`, `network`, `actions`) until the user grants write access.
-- When the user requests interactive mode, run `npx libretto session-mode interactive --session <name>` and then proceed with `exec`/`run`.
-- Never change session mode unless the user explicitly approves.
-
 ## Visualize Mode (`--visualize`)
 
 Add `--visualize` to any `exec` command to show a ghost cursor and element highlight before each action executes. Use it when the user wants to see what will be clicked/filled before it happens.
@@ -54,8 +74,8 @@ The `state` object persists across `exec` calls within the same session — use
 # Open a page (starts in read-only mode)
 npx libretto open https://example.com
 
-# When user grants interactive access:
-npx libretto session-mode interactive --session default
+# When user grants full access:
+npx libretto session-mode full-access --session default
 
 # Interact with elements
 npx libretto exec "await page.locator('button:has-text(\"Sign in\")').click()"
@@ -99,8 +119,8 @@ When browser automation jobs fail (selectors timing out, clicks not working), us
 1. Add `page.pause()` before the problematic code section
 2. Start the job with `npx browser-agent start` (debug mode is always enabled locally)
 3. Wait ~60 seconds for the browser to hit the breakpoint
-4. Ask user if they approve interactive mode for `browser-agent`
-5. If approved, run `npx libretto session-mode interactive --session browser-agent`
+4. Ask user if they approve full-access mode for `browser-agent`
+5. If approved, run `npx libretto session-mode full-access --session browser-agent`
 6. Use `npx libretto exec` (with `--session browser-agent`) to inspect and prototype fixes
 7. Once the fix works, codify it in source files
 8. Restart the job to verify end-to-end
@@ -113,7 +133,7 @@ npx browser-agent start \
   --params '{"vendorName":"eClinicalWorks"}'
 
 # Inspect page state
-npx libretto session-mode interactive --session browser-agent
+npx libretto session-mode full-access --session browser-agent
 npx libretto exec --session browser-agent "return await page.url();"
 npx libretto snapshot --session browser-agent \
   --objective "Find dropdown menus and their current selections" \
PATCH

echo "Gold patch applied."
