#!/usr/bin/env bash
set -euo pipefail

cd /workspace/libretto

# Idempotency guard
if grep -qF "- Treat Libretto as a script-authoring workflow: choose or create a workflow fil" ".agents/skills/libretto/SKILL.md" && grep -qF "- Treat Libretto as a script-authoring workflow: choose or create a workflow fil" ".claude/skills/libretto/SKILL.md" && grep -qF "- Treat Libretto as a script-authoring workflow: choose or create a workflow fil" "skills/libretto/SKILL.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/.agents/skills/libretto/SKILL.md b/.agents/skills/libretto/SKILL.md
@@ -1,6 +1,6 @@
 ---
 name: libretto
-description: "Browser automation CLI for inspecting live pages, prototyping interactions, and running browser workflows."
+description: "Browser automation CLI for building, maintaining, and running browser automation workflows by inspecting live pages and prototyping interactions."
 license: MIT
 metadata:
   author: saffron-health
@@ -9,13 +9,17 @@ metadata:
 
 # Libretto
 
-Use `npx libretto` to inspect live browser state, prototype interactions, and run existing browser workflows.
+Libretto is a CLI for building and maintaining browser automation scripts.
+Use `npx libretto` to build or debug automations by inspecting live browser state, executing Playwright code, and running existing workflows.
 
 ## Intro
 
 - Use this skill when the truth is on the page.
-- Prefer Libretto when you need to see what the browser is doing, not when you only need to edit source files.
-- Treat Libretto as a session-based workflow: open a page, inspect it, try a focused action, then turn what you learned into code outside the CLI.
+- Prefer Libretto when you need to build, maintain, or debug a browser automation script against the live site.
+- Treat Libretto as a script-authoring workflow: choose or create a workflow file, inspect the page, try focused actions, then update code outside the CLI and verify it with `run`.
+- If the user asks for a new automation or scrape and no workflow file exists yet, create one in the workspace instead of stopping at interactive exploration.
+- For a new automation, make the workflow file a required deliverable before you finish the task, even if you inspect the site first.
+- If the user does not provide a workflow path, choose a reasonable filename in the current workspace and create it yourself.
 - When building a new integration, prefer reverse-engineering network requests first. Fall back to browser automation when the request path is unclear, too fragile, or blocked by anti-bot systems.
 
 ## Setup
@@ -27,6 +31,9 @@ Use `npx libretto` to inspect live browser state, prototype interactions, and ru
 ## Rules
 
 - Announce which session you are using and what page you are on.
+- When the task is to build or change an automation, create or update the workflow file and use Libretto commands to gather the information needed for that code change.
+- For a new automation, you may use `open`, `snapshot`, or `exec` first to learn the page, but do not finish or reply as if the task is complete until the workflow file exists.
+- Treat scrape and integration requests as requests for reusable automation code by default, not as requests to manually collect the final data in the live session.
 - Ask instead of guessing when it is unclear what to click, type, or submit.
 - Use `snapshot` to understand unknown page state before trying multiple selectors.
 - Get explicit user confirmation before mutating actions or replaying network requests that may have side effects.
@@ -38,6 +45,7 @@ Use `npx libretto` to inspect live browser state, prototype interactions, and ru
 ### `open`
 
 - Open a page before using `exec` or `snapshot`.
+- Use `open` at the start of script authoring when you need live page state to decide how the workflow should work.
 - Use headed mode when the user needs to log in or watch the workflow.
 
 ```bash
@@ -48,6 +56,7 @@ npx libretto open https://example.com --headless --session debug-example
 ### `exec`
 
 - Use `exec` for focused inspection and short-lived interaction experiments.
+- Use `exec` to validate selectors, inspect data, or prototype a step before you encode it in the workflow file.
 - Let failures throw. Do not hide `exec` failures with `try/catch`.
 
 ```bash
@@ -59,6 +68,7 @@ npx libretto exec --visualize "await page.locator('button:has-text(\"Continue\")
 ### `snapshot`
 
 - Use `snapshot` as the primary page observation tool.
+- Use `snapshot` to understand the current page before editing the workflow when the structure or next step is unclear.
 - When you want analysis, provide both `--objective` and `--context`.
 - If you only need the PNG and HTML files, omit `--objective`. That runs capture-only mode and skips AI analysis.
 - When using `--objective`, expect analysis to take time. Use a timeout of at least 2 minutes for shell-wrapped calls.
@@ -75,7 +85,7 @@ npx libretto snapshot \
 
 ### `run`
 
-- Use `run` to execute an existing Libretto workflow.
+- Use `run` to verify a workflow file after creating it or editing it.
 - If the workflow fails, Libretto keeps the browser open. Inspect the failed state with `snapshot` and `exec` before editing code.
 - If the workflow pauses, resume it with `npx libretto resume --session <name>`.
 - Re-run the same workflow after each fix to verify the browser behavior end to end.
@@ -95,7 +105,7 @@ npx libretto run ./integration.ts main --auth-profile app.example.com --headed
 ```text
 <example>
 [Context: The user wants to build a new browser workflow and does not yet know the page structure]
-Assistant: Let me open the target page in headed mode so we can inspect the real workflow.
+Assistant: I'll inspect the real site first if needed, but before I finish I'll create `./target-workflow.mjs` so the task produces reusable automation code.
 Assistant: [Runs `npx libretto open https://target.example.com --headed`]
 Assistant: I'll first determine whether this flow can be built from captured network requests instead of UI-only automation.
 Assistant: [Runs `npx libretto snapshot --objective "Find the next required action" --context "We are starting the workflow from the landing page."`]
diff --git a/.claude/skills/libretto/SKILL.md b/.claude/skills/libretto/SKILL.md
@@ -1,6 +1,6 @@
 ---
 name: libretto
-description: "Browser automation CLI for inspecting live pages, prototyping interactions, and running browser workflows."
+description: "Browser automation CLI for building, maintaining, and running browser automation workflows by inspecting live pages and prototyping interactions."
 license: MIT
 metadata:
   author: saffron-health
@@ -9,13 +9,17 @@ metadata:
 
 # Libretto
 
-Use `npx libretto` to inspect live browser state, prototype interactions, and run existing browser workflows.
+Libretto is a CLI for building and maintaining browser automation scripts.
+Use `npx libretto` to build or debug automations by inspecting live browser state, executing Playwright code, and running existing workflows.
 
 ## Intro
 
 - Use this skill when the truth is on the page.
-- Prefer Libretto when you need to see what the browser is doing, not when you only need to edit source files.
-- Treat Libretto as a session-based workflow: open a page, inspect it, try a focused action, then turn what you learned into code outside the CLI.
+- Prefer Libretto when you need to build, maintain, or debug a browser automation script against the live site.
+- Treat Libretto as a script-authoring workflow: choose or create a workflow file, inspect the page, try focused actions, then update code outside the CLI and verify it with `run`.
+- If the user asks for a new automation or scrape and no workflow file exists yet, create one in the workspace instead of stopping at interactive exploration.
+- For a new automation, make the workflow file a required deliverable before you finish the task, even if you inspect the site first.
+- If the user does not provide a workflow path, choose a reasonable filename in the current workspace and create it yourself.
 - When building a new integration, prefer reverse-engineering network requests first. Fall back to browser automation when the request path is unclear, too fragile, or blocked by anti-bot systems.
 
 ## Setup
@@ -27,6 +31,9 @@ Use `npx libretto` to inspect live browser state, prototype interactions, and ru
 ## Rules
 
 - Announce which session you are using and what page you are on.
+- When the task is to build or change an automation, create or update the workflow file and use Libretto commands to gather the information needed for that code change.
+- For a new automation, you may use `open`, `snapshot`, or `exec` first to learn the page, but do not finish or reply as if the task is complete until the workflow file exists.
+- Treat scrape and integration requests as requests for reusable automation code by default, not as requests to manually collect the final data in the live session.
 - Ask instead of guessing when it is unclear what to click, type, or submit.
 - Use `snapshot` to understand unknown page state before trying multiple selectors.
 - Get explicit user confirmation before mutating actions or replaying network requests that may have side effects.
@@ -38,6 +45,7 @@ Use `npx libretto` to inspect live browser state, prototype interactions, and ru
 ### `open`
 
 - Open a page before using `exec` or `snapshot`.
+- Use `open` at the start of script authoring when you need live page state to decide how the workflow should work.
 - Use headed mode when the user needs to log in or watch the workflow.
 
 ```bash
@@ -48,6 +56,7 @@ npx libretto open https://example.com --headless --session debug-example
 ### `exec`
 
 - Use `exec` for focused inspection and short-lived interaction experiments.
+- Use `exec` to validate selectors, inspect data, or prototype a step before you encode it in the workflow file.
 - Let failures throw. Do not hide `exec` failures with `try/catch`.
 
 ```bash
@@ -59,6 +68,7 @@ npx libretto exec --visualize "await page.locator('button:has-text(\"Continue\")
 ### `snapshot`
 
 - Use `snapshot` as the primary page observation tool.
+- Use `snapshot` to understand the current page before editing the workflow when the structure or next step is unclear.
 - When you want analysis, provide both `--objective` and `--context`.
 - If you only need the PNG and HTML files, omit `--objective`. That runs capture-only mode and skips AI analysis.
 - When using `--objective`, expect analysis to take time. Use a timeout of at least 2 minutes for shell-wrapped calls.
@@ -75,7 +85,7 @@ npx libretto snapshot \
 
 ### `run`
 
-- Use `run` to execute an existing Libretto workflow.
+- Use `run` to verify a workflow file after creating it or editing it.
 - If the workflow fails, Libretto keeps the browser open. Inspect the failed state with `snapshot` and `exec` before editing code.
 - If the workflow pauses, resume it with `npx libretto resume --session <name>`.
 - Re-run the same workflow after each fix to verify the browser behavior end to end.
@@ -95,7 +105,7 @@ npx libretto run ./integration.ts main --auth-profile app.example.com --headed
 ```text
 <example>
 [Context: The user wants to build a new browser workflow and does not yet know the page structure]
-Assistant: Let me open the target page in headed mode so we can inspect the real workflow.
+Assistant: I'll inspect the real site first if needed, but before I finish I'll create `./target-workflow.mjs` so the task produces reusable automation code.
 Assistant: [Runs `npx libretto open https://target.example.com --headed`]
 Assistant: I'll first determine whether this flow can be built from captured network requests instead of UI-only automation.
 Assistant: [Runs `npx libretto snapshot --objective "Find the next required action" --context "We are starting the workflow from the landing page."`]
diff --git a/skills/libretto/SKILL.md b/skills/libretto/SKILL.md
@@ -1,6 +1,6 @@
 ---
 name: libretto
-description: "Browser automation CLI for inspecting live pages, prototyping interactions, and running browser workflows."
+description: "Browser automation CLI for building, maintaining, and running browser automation workflows by inspecting live pages and prototyping interactions."
 license: MIT
 metadata:
   author: saffron-health
@@ -9,13 +9,17 @@ metadata:
 
 # Libretto
 
-Use `npx libretto` to inspect live browser state, prototype interactions, and run existing browser workflows.
+Libretto is a CLI for building and maintaining browser automation scripts.
+Use `npx libretto` to build or debug automations by inspecting live browser state, executing Playwright code, and running existing workflows.
 
 ## Intro
 
 - Use this skill when the truth is on the page.
-- Prefer Libretto when you need to see what the browser is doing, not when you only need to edit source files.
-- Treat Libretto as a session-based workflow: open a page, inspect it, try a focused action, then turn what you learned into code outside the CLI.
+- Prefer Libretto when you need to build, maintain, or debug a browser automation script against the live site.
+- Treat Libretto as a script-authoring workflow: choose or create a workflow file, inspect the page, try focused actions, then update code outside the CLI and verify it with `run`.
+- If the user asks for a new automation or scrape and no workflow file exists yet, create one in the workspace instead of stopping at interactive exploration.
+- For a new automation, make the workflow file a required deliverable before you finish the task, even if you inspect the site first.
+- If the user does not provide a workflow path, choose a reasonable filename in the current workspace and create it yourself.
 - When building a new integration, prefer reverse-engineering network requests first. Fall back to browser automation when the request path is unclear, too fragile, or blocked by anti-bot systems.
 
 ## Setup
@@ -27,6 +31,9 @@ Use `npx libretto` to inspect live browser state, prototype interactions, and ru
 ## Rules
 
 - Announce which session you are using and what page you are on.
+- When the task is to build or change an automation, create or update the workflow file and use Libretto commands to gather the information needed for that code change.
+- For a new automation, you may use `open`, `snapshot`, or `exec` first to learn the page, but do not finish or reply as if the task is complete until the workflow file exists.
+- Treat scrape and integration requests as requests for reusable automation code by default, not as requests to manually collect the final data in the live session.
 - Ask instead of guessing when it is unclear what to click, type, or submit.
 - Use `snapshot` to understand unknown page state before trying multiple selectors.
 - Get explicit user confirmation before mutating actions or replaying network requests that may have side effects.
@@ -38,6 +45,7 @@ Use `npx libretto` to inspect live browser state, prototype interactions, and ru
 ### `open`
 
 - Open a page before using `exec` or `snapshot`.
+- Use `open` at the start of script authoring when you need live page state to decide how the workflow should work.
 - Use headed mode when the user needs to log in or watch the workflow.
 
 ```bash
@@ -48,6 +56,7 @@ npx libretto open https://example.com --headless --session debug-example
 ### `exec`
 
 - Use `exec` for focused inspection and short-lived interaction experiments.
+- Use `exec` to validate selectors, inspect data, or prototype a step before you encode it in the workflow file.
 - Let failures throw. Do not hide `exec` failures with `try/catch`.
 
 ```bash
@@ -59,6 +68,7 @@ npx libretto exec --visualize "await page.locator('button:has-text(\"Continue\")
 ### `snapshot`
 
 - Use `snapshot` as the primary page observation tool.
+- Use `snapshot` to understand the current page before editing the workflow when the structure or next step is unclear.
 - When you want analysis, provide both `--objective` and `--context`.
 - If you only need the PNG and HTML files, omit `--objective`. That runs capture-only mode and skips AI analysis.
 - When using `--objective`, expect analysis to take time. Use a timeout of at least 2 minutes for shell-wrapped calls.
@@ -75,7 +85,7 @@ npx libretto snapshot \
 
 ### `run`
 
-- Use `run` to execute an existing Libretto workflow.
+- Use `run` to verify a workflow file after creating it or editing it.
 - If the workflow fails, Libretto keeps the browser open. Inspect the failed state with `snapshot` and `exec` before editing code.
 - If the workflow pauses, resume it with `npx libretto resume --session <name>`.
 - Re-run the same workflow after each fix to verify the browser behavior end to end.
@@ -95,7 +105,7 @@ npx libretto run ./integration.ts main --auth-profile app.example.com --headed
 ```text
 <example>
 [Context: The user wants to build a new browser workflow and does not yet know the page structure]
-Assistant: Let me open the target page in headed mode so we can inspect the real workflow.
+Assistant: I'll inspect the real site first if needed, but before I finish I'll create `./target-workflow.mjs` so the task produces reusable automation code.
 Assistant: [Runs `npx libretto open https://target.example.com --headed`]
 Assistant: I'll first determine whether this flow can be built from captured network requests instead of UI-only automation.
 Assistant: [Runs `npx libretto snapshot --objective "Find the next required action" --context "We are starting the workflow from the landing page."`]
PATCH

echo "Gold patch applied."
