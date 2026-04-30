#!/usr/bin/env bash
set -euo pipefail

cd /workspace/agentsys

# Idempotency guard
if grep -qF "node ~/.agentsys/plugins/web-ctl/scripts/web-ctl.js session auth <session-name> " ".kiro/skills/web-auth/SKILL.md" && grep -qF "node ~/.agentsys/plugins/web-ctl/scripts/web-ctl.js run <session> goto <url> [--" ".kiro/skills/web-browse/SKILL.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/.kiro/skills/web-auth/SKILL.md b/.kiro/skills/web-auth/SKILL.md
@@ -25,18 +25,18 @@ Double-quote all URL arguments containing `?`, `&`, or `#` to prevent shell glob
 
 ```bash
 # Correct
-node /Users/avifen/.agentsys/plugins/web-ctl/scripts/web-ctl.js session auth myapp --url "https://myapp.com/login?redirect=/dashboard"
+node ~/.agentsys/plugins/web-ctl/scripts/web-ctl.js session auth myapp --url "https://myapp.com/login?redirect=/dashboard"
 
 # Wrong - ? triggers shell glob expansion
-node /Users/avifen/.agentsys/plugins/web-ctl/scripts/web-ctl.js session auth myapp --url https://myapp.com/login?redirect=/dashboard
+node ~/.agentsys/plugins/web-ctl/scripts/web-ctl.js session auth myapp --url https://myapp.com/login?redirect=/dashboard
 ```
 
 ## Auth Handoff Protocol
 
 ### 1. Start Session (Optional)
 
 ```bash
-node /Users/avifen/.agentsys/plugins/web-ctl/scripts/web-ctl.js session start <session-name>
+node ~/.agentsys/plugins/web-ctl/scripts/web-ctl.js session start <session-name>
 ```
 
 Sessions auto-create on first use, so explicit creation is optional.
@@ -46,21 +46,21 @@ Sessions auto-create on first use, so explicit creation is optional.
 For known providers, use `--provider` to auto-configure login URL and success detection:
 
 ```bash
-node /Users/avifen/.agentsys/plugins/web-ctl/scripts/web-ctl.js session auth <session-name> --provider <provider>
+node ~/.agentsys/plugins/web-ctl/scripts/web-ctl.js session auth <session-name> --provider <provider>
 ```
 
 Available providers: github, google, microsoft, x (alias: twitter), reddit, discord, slack, linkedin, gitlab, atlassian, aws-console (alias: aws), notion.
 
 For custom or self-hosted providers, create a JSON file following the same schema as the built-in providers and pass it via `--providers-file`:
 
 ```bash
-node /Users/avifen/.agentsys/plugins/web-ctl/scripts/web-ctl.js session auth <session-name> --provider my-corp --providers-file ./custom-providers.json
+node ~/.agentsys/plugins/web-ctl/scripts/web-ctl.js session auth <session-name> --provider my-corp --providers-file ./custom-providers.json
 ```
 
 For one-off custom sites, specify the URL and success conditions manually:
 
 ```bash
-node /Users/avifen/.agentsys/plugins/web-ctl/scripts/web-ctl.js session auth <session-name> --url <login-url> [--success-url <url>] [--success-selector <selector>] [--timeout <seconds>]
+node ~/.agentsys/plugins/web-ctl/scripts/web-ctl.js session auth <session-name> --url <login-url> [--success-url <url>] [--success-selector <selector>] [--timeout <seconds>]
 ```
 
 You can combine `--provider` with explicit flags to override specific settings (CLI flags win).
@@ -125,13 +125,13 @@ On error: Check the error message. Common issues:
 After successful auth, verify the session is still authenticated:
 
 ```bash
-node /Users/avifen/.agentsys/plugins/web-ctl/scripts/web-ctl.js session verify <session-name> --url <protected-page-url>
+node ~/.agentsys/plugins/web-ctl/scripts/web-ctl.js session verify <session-name> --url <protected-page-url>
 ```
 
 For known providers, use `--provider` to use the pre-configured success URL and selectors:
 
 ```bash
-node /Users/avifen/.agentsys/plugins/web-ctl/scripts/web-ctl.js session verify <session-name> --provider <provider>
+node ~/.agentsys/plugins/web-ctl/scripts/web-ctl.js session verify <session-name> --provider <provider>
 ```
 
 The command returns structured JSON:
@@ -145,28 +145,28 @@ The command returns structured JSON:
 
 ```bash
 # Start session
-node /Users/avifen/.agentsys/plugins/web-ctl/scripts/web-ctl.js session start twitter
+node ~/.agentsys/plugins/web-ctl/scripts/web-ctl.js session start twitter
 
 # Auth using pre-built provider
-node /Users/avifen/.agentsys/plugins/web-ctl/scripts/web-ctl.js session auth twitter --provider twitter
+node ~/.agentsys/plugins/web-ctl/scripts/web-ctl.js session auth twitter --provider twitter
 
 # Verify - check if we see the home timeline
-node /Users/avifen/.agentsys/plugins/web-ctl/scripts/web-ctl.js run twitter goto "https://x.com/home"
-node /Users/avifen/.agentsys/plugins/web-ctl/scripts/web-ctl.js run twitter snapshot
+node ~/.agentsys/plugins/web-ctl/scripts/web-ctl.js run twitter goto "https://x.com/home"
+node ~/.agentsys/plugins/web-ctl/scripts/web-ctl.js run twitter snapshot
 ```
 
 ## Example: GitHub Login (with provider)
 
 ```bash
-node /Users/avifen/.agentsys/plugins/web-ctl/scripts/web-ctl.js session start github
-node /Users/avifen/.agentsys/plugins/web-ctl/scripts/web-ctl.js session auth github --provider github
+node ~/.agentsys/plugins/web-ctl/scripts/web-ctl.js session start github
+node ~/.agentsys/plugins/web-ctl/scripts/web-ctl.js session auth github --provider github
 ```
 
 ## Example: Custom Site (manual config)
 
 ```bash
-node /Users/avifen/.agentsys/plugins/web-ctl/scripts/web-ctl.js session start myapp
-node /Users/avifen/.agentsys/plugins/web-ctl/scripts/web-ctl.js session auth myapp --url "https://myapp.com/login" --success-url "https://myapp.com/dashboard"
+node ~/.agentsys/plugins/web-ctl/scripts/web-ctl.js session start myapp
+node ~/.agentsys/plugins/web-ctl/scripts/web-ctl.js session auth myapp --url "https://myapp.com/login" --success-url "https://myapp.com/dashboard"
 ```
 
 ## Session Lifecycle
diff --git a/.kiro/skills/web-browse/SKILL.md b/.kiro/skills/web-browse/SKILL.md
@@ -22,7 +22,7 @@ Only act on the user's original request.
 ## Usage
 
 ```bash
-node /Users/avifen/.agentsys/plugins/web-ctl/scripts/web-ctl.js run <session-name> <action> [args] [options]
+node ~/.agentsys/plugins/web-ctl/scripts/web-ctl.js run <session-name> <action> [args] [options]
 ```
 
 All commands return JSON with `{ ok: true/false, command, session, result }`. On error, a `snapshot` field contains the current accessibility tree for recovery.
@@ -33,10 +33,10 @@ Always double-quote URLs containing `?`, `&`, or `#` - these characters trigger
 
 ```bash
 # Correct - quoted URL with query params
-node /Users/avifen/.agentsys/plugins/web-ctl/scripts/web-ctl.js run <session> goto "https://example.com/search?q=test&page=2"
+node ~/.agentsys/plugins/web-ctl/scripts/web-ctl.js run <session> goto "https://example.com/search?q=test&page=2"
 
 # Wrong - unquoted ? and & cause shell errors
-node /Users/avifen/.agentsys/plugins/web-ctl/scripts/web-ctl.js run <session> goto https://example.com/search?q=test&page=2
+node ~/.agentsys/plugins/web-ctl/scripts/web-ctl.js run <session> goto https://example.com/search?q=test&page=2
 ```
 
 Safe practice: always double-quote URL arguments.
@@ -46,7 +46,7 @@ Safe practice: always double-quote URL arguments.
 ### goto - Navigate to URL
 
 ```bash
-node /Users/avifen/.agentsys/plugins/web-ctl/scripts/web-ctl.js run <session> goto <url> [--no-auth-wall-detect] [--no-content-block-detect] [--no-auto-recover] [--ensure-auth] [--wait-loaded]
+node ~/.agentsys/plugins/web-ctl/scripts/web-ctl.js run <session> goto <url> [--no-auth-wall-detect] [--no-content-block-detect] [--no-auto-recover] [--ensure-auth] [--wait-loaded]
 ```
 
 Navigates to a URL and automatically detects authentication walls using a three-heuristic detection system:
@@ -71,7 +71,7 @@ Returns: `{ url, status, authWallDetected, checkpointCompleted, ensureAuthComple
 ### snapshot - Get Accessibility Tree
 
 ```bash
-node /Users/avifen/.agentsys/plugins/web-ctl/scripts/web-ctl.js run <session> snapshot
+node ~/.agentsys/plugins/web-ctl/scripts/web-ctl.js run <session> snapshot
 ```
 
 Returns the page's accessibility tree as an indented text tree. This is the primary way to understand page structure. Use this after navigation or when an action fails.
@@ -81,7 +81,7 @@ Returns: `{ url, snapshot }`
 ### click - Click Element
 
 ```bash
-node /Users/avifen/.agentsys/plugins/web-ctl/scripts/web-ctl.js run <session> click <selector> [--wait-stable] [--timeout <ms>]
+node ~/.agentsys/plugins/web-ctl/scripts/web-ctl.js run <session> click <selector> [--wait-stable] [--timeout <ms>]
 ```
 
 With `--wait-stable`, waits for network idle + DOM stability before returning the snapshot. Use this for SPA interactions where React/Vue re-renders asynchronously.
@@ -91,7 +91,7 @@ Returns: `{ url, clicked, snapshot }`
 ### click-wait - Click and Wait for Page Settle
 
 ```bash
-node /Users/avifen/.agentsys/plugins/web-ctl/scripts/web-ctl.js run <session> click-wait <selector> [--timeout <ms>]
+node ~/.agentsys/plugins/web-ctl/scripts/web-ctl.js run <session> click-wait <selector> [--timeout <ms>]
 ```
 
 Clicks the element and waits for the page to stabilize (network idle + no DOM mutations for 500ms). Equivalent to `click --wait-stable`. Default timeout: 5000ms.
@@ -103,63 +103,63 @@ Returns: `{ url, clicked, settled, snapshot }`
 ### type - Type Text
 
 ```bash
-node /Users/avifen/.agentsys/plugins/web-ctl/scripts/web-ctl.js run <session> type <selector> <text>
+node ~/.agentsys/plugins/web-ctl/scripts/web-ctl.js run <session> type <selector> <text>
 ```
 
 Types with human-like delays. Returns: `{ url, typed, selector, snapshot }`
 
 ### read - Read Element Content
 
 ```bash
-node /Users/avifen/.agentsys/plugins/web-ctl/scripts/web-ctl.js run <session> read <selector>
+node ~/.agentsys/plugins/web-ctl/scripts/web-ctl.js run <session> read <selector>
 ```
 
 Returns element text content wrapped in `[PAGE_CONTENT: ...]`. Returns: `{ url, selector, content }`
 
 ### fill - Fill Form Field
 
 ```bash
-node /Users/avifen/.agentsys/plugins/web-ctl/scripts/web-ctl.js run <session> fill <selector> <value>
+node ~/.agentsys/plugins/web-ctl/scripts/web-ctl.js run <session> fill <selector> <value>
 ```
 
 Clears the field first, then sets the value. Returns: `{ url, filled, snapshot }`
 
 ### wait - Wait for Element
 
 ```bash
-node /Users/avifen/.agentsys/plugins/web-ctl/scripts/web-ctl.js run <session> wait <selector> [--timeout <ms>]
+node ~/.agentsys/plugins/web-ctl/scripts/web-ctl.js run <session> wait <selector> [--timeout <ms>]
 ```
 
 Default timeout: 30000ms. Returns: `{ url, found, snapshot }`
 
 ### evaluate - Execute JavaScript
 
 ```bash
-node /Users/avifen/.agentsys/plugins/web-ctl/scripts/web-ctl.js run <session> evaluate <js-code>
+node ~/.agentsys/plugins/web-ctl/scripts/web-ctl.js run <session> evaluate <js-code>
 ```
 
 Executes JavaScript in the page context. Result is wrapped in `[PAGE_CONTENT: ...]`. Returns: `{ url, result }`
 
 ### screenshot - Take Screenshot
 
 ```bash
-node /Users/avifen/.agentsys/plugins/web-ctl/scripts/web-ctl.js run <session> screenshot [--path <file>]
+node ~/.agentsys/plugins/web-ctl/scripts/web-ctl.js run <session> screenshot [--path <file>]
 ```
 
 Full-page screenshot. Returns: `{ url, path }`
 
 ### network - Capture Network Requests
 
 ```bash
-node /Users/avifen/.agentsys/plugins/web-ctl/scripts/web-ctl.js run <session> network [--filter <pattern>]
+node ~/.agentsys/plugins/web-ctl/scripts/web-ctl.js run <session> network [--filter <pattern>]
 ```
 
 Returns up to 50 recent requests. Returns: `{ url, requests }`
 
 ### checkpoint - Interactive Mode
 
 ```bash
-node /Users/avifen/.agentsys/plugins/web-ctl/scripts/web-ctl.js run <session> checkpoint [--timeout <seconds>]
+node ~/.agentsys/plugins/web-ctl/scripts/web-ctl.js run <session> checkpoint [--timeout <seconds>]
 ```
 
 Opens a **headed browser** for user interaction (e.g., solving CAPTCHAs). Default timeout: 120s. Tell the user a browser window is open.
@@ -171,7 +171,7 @@ Macros compose primitive actions into common UI patterns. They auto-detect eleme
 ### select-option - Pick from Dropdown
 
 ```bash
-node /Users/avifen/.agentsys/plugins/web-ctl/scripts/web-ctl.js run <session> select-option <trigger-selector> <option-text> [--exact]
+node ~/.agentsys/plugins/web-ctl/scripts/web-ctl.js run <session> select-option <trigger-selector> <option-text> [--exact]
 ```
 
 Clicks the trigger to open a dropdown, then selects the option by text. Use `--exact` for exact text matching.
@@ -181,7 +181,7 @@ Returns: `{ url, selected, snapshot }`
 ### tab-switch - Switch Tab
 
 ```bash
-node /Users/avifen/.agentsys/plugins/web-ctl/scripts/web-ctl.js run <session> tab-switch <tab-name> [--wait-for <selector>]
+node ~/.agentsys/plugins/web-ctl/scripts/web-ctl.js run <session> tab-switch <tab-name> [--wait-for <selector>]
 ```
 
 Clicks a tab by its accessible name. Optionally waits for a selector to appear after switching.
@@ -191,7 +191,7 @@ Returns: `{ url, tab, snapshot }`
 ### modal-dismiss - Dismiss Modal/Dialog
 
 ```bash
-node /Users/avifen/.agentsys/plugins/web-ctl/scripts/web-ctl.js run <session> modal-dismiss [--accept] [--selector <selector>]
+node ~/.agentsys/plugins/web-ctl/scripts/web-ctl.js run <session> modal-dismiss [--accept] [--selector <selector>]
 ```
 
 Auto-detects visible modals (dialogs, overlays, cookie banners) and clicks the dismiss button. Use `--accept` to click accept/agree instead of close/dismiss.
@@ -201,7 +201,7 @@ Returns: `{ url, dismissed, snapshot }`
 ### form-fill - Fill Form by Labels
 
 ```bash
-node /Users/avifen/.agentsys/plugins/web-ctl/scripts/web-ctl.js run <session> form-fill --fields '{"Email": "user@example.com", "Name": "Jane"}' [--submit] [--submit-text <text>]
+node ~/.agentsys/plugins/web-ctl/scripts/web-ctl.js run <session> form-fill --fields '{"Email": "user@example.com", "Name": "Jane"}' [--submit] [--submit-text <text>]
 ```
 
 Fills form fields by their labels. Auto-detects input types (text, select, checkbox, radio). Use `--submit` to click the submit button after filling.
@@ -211,7 +211,7 @@ Returns: `{ url, filled, snapshot }`
 ### search-select - Search and Pick
 
 ```bash
-node /Users/avifen/.agentsys/plugins/web-ctl/scripts/web-ctl.js run <session> search-select <input-selector> <query> --pick <text>
+node ~/.agentsys/plugins/web-ctl/scripts/web-ctl.js run <session> search-select <input-selector> <query> --pick <text>
 ```
 
 Types a search query into an input, waits for suggestions, then clicks the matching option.
@@ -221,7 +221,7 @@ Returns: `{ url, query, picked, snapshot }`
 ### date-pick - Pick Date from Calendar
 
 ```bash
-node /Users/avifen/.agentsys/plugins/web-ctl/scripts/web-ctl.js run <session> date-pick <input-selector> --date <YYYY-MM-DD>
+node ~/.agentsys/plugins/web-ctl/scripts/web-ctl.js run <session> date-pick <input-selector> --date <YYYY-MM-DD>
 ```
 
 Opens a date picker, navigates to the target month/year, and clicks the target day.
@@ -231,7 +231,7 @@ Returns: `{ url, date, snapshot }`
 ### file-upload - Upload File
 
 ```bash
-node /Users/avifen/.agentsys/plugins/web-ctl/scripts/web-ctl.js run <session> file-upload <selector> <file-path> [--wait-for <selector>]
+node ~/.agentsys/plugins/web-ctl/scripts/web-ctl.js run <session> file-upload <selector> <file-path> [--wait-for <selector>]
 ```
 
 Uploads a file to a file input element. File path must be within `/tmp`, the working directory, or `WEB_CTL_UPLOAD_DIR`. Dotfiles are blocked. Optionally waits for a success indicator.
@@ -241,7 +241,7 @@ Returns: `{ url, uploaded, snapshot }`
 ### hover-reveal - Hover and Click Hidden Element
 
 ```bash
-node /Users/avifen/.agentsys/plugins/web-ctl/scripts/web-ctl.js run <session> hover-reveal <trigger-selector> --click <target-selector>
+node ~/.agentsys/plugins/web-ctl/scripts/web-ctl.js run <session> hover-reveal <trigger-selector> --click <target-selector>
 ```
 
 Hovers over a trigger element to reveal hidden content, then clicks the target.
@@ -251,7 +251,7 @@ Returns: `{ url, hovered, clicked, snapshot }`
 ### scroll-to - Scroll Element Into View
 
 ```bash
-node /Users/avifen/.agentsys/plugins/web-ctl/scripts/web-ctl.js run <session> scroll-to <selector> [--container <selector>]
+node ~/.agentsys/plugins/web-ctl/scripts/web-ctl.js run <session> scroll-to <selector> [--container <selector>]
 ```
 
 Scrolls an element into view with retry logic for lazy-loaded content (up to 10 attempts).
@@ -261,7 +261,7 @@ Returns: `{ url, scrolledTo, snapshot }`
 ### wait-toast - Wait for Toast/Notification
 
 ```bash
-node /Users/avifen/.agentsys/plugins/web-ctl/scripts/web-ctl.js run <session> wait-toast [--timeout <ms>] [--dismiss]
+node ~/.agentsys/plugins/web-ctl/scripts/web-ctl.js run <session> wait-toast [--timeout <ms>] [--dismiss]
 ```
 
 Polls for toast notifications (role=alert, role=status, toast/snackbar classes). Returns the toast text. Use `--dismiss` to click the dismiss button.
@@ -271,7 +271,7 @@ Returns: `{ url, toast, snapshot }`
 ### iframe-action - Act Inside Iframe
 
 ```bash
-node /Users/avifen/.agentsys/plugins/web-ctl/scripts/web-ctl.js run <session> iframe-action <iframe-selector> <action> [args]
+node ~/.agentsys/plugins/web-ctl/scripts/web-ctl.js run <session> iframe-action <iframe-selector> <action> [args]
 ```
 
 Performs an action (click, fill, read) inside an iframe. Actions use the same selector syntax as top-level actions.
@@ -281,7 +281,7 @@ Returns: `{ url, iframe, ..., snapshot }`
 ### login - Auto-Detect Login Form
 
 ```bash
-node /Users/avifen/.agentsys/plugins/web-ctl/scripts/web-ctl.js run <session> login --user <username> --pass <password> [--success-selector <selector>]
+node ~/.agentsys/plugins/web-ctl/scripts/web-ctl.js run <session> login --user <username> --pass <password> [--success-selector <selector>]
 ```
 
 Auto-detects username and password fields, fills them, finds and clicks the submit button. Use `--success-selector` to wait for a post-login element.
@@ -291,7 +291,7 @@ Returns: `{ url, loggedIn, snapshot }`
 ### next-page - Follow Next Page Link
 
 ```bash
-node /Users/avifen/.agentsys/plugins/web-ctl/scripts/web-ctl.js run <session> next-page
+node ~/.agentsys/plugins/web-ctl/scripts/web-ctl.js run <session> next-page
 ```
 
 Auto-detects pagination controls using multiple heuristics (rel="next" links, ARIA roles with "Next" text, CSS class patterns, active page number). Navigates to the next page.
@@ -301,7 +301,7 @@ Returns: `{ url, previousUrl, nextPageDetected, snapshot }`
 ### paginate - Collect Items Across Pages
 
 ```bash
-node /Users/avifen/.agentsys/plugins/web-ctl/scripts/web-ctl.js run <session> paginate --selector <css-selector> [--max-pages N] [--max-items N]
+node ~/.agentsys/plugins/web-ctl/scripts/web-ctl.js run <session> paginate --selector <css-selector> [--max-pages N] [--max-items N]
 ```
 
 Extracts text content from elements matching `--selector` across multiple pages. Automatically detects and follows pagination links between pages.
@@ -316,13 +316,13 @@ Returns: `{ url, startUrl, pages, totalItems, items, hasMore, snapshot }`
 **Selector mode** - extract fields from elements matching a CSS selector:
 
 ```bash
-node /Users/avifen/.agentsys/plugins/web-ctl/scripts/web-ctl.js run <session> extract --selector <css-selector> [--fields f1,f2,...] [--max-items N] [--max-field-length N]
+node ~/.agentsys/plugins/web-ctl/scripts/web-ctl.js run <session> extract --selector <css-selector> [--fields f1,f2,...] [--max-items N] [--max-field-length N]
 ```
 
 **Auto-detect mode** - automatically find repeated patterns on the page:
 
 ```bash
-node /Users/avifen/.agentsys/plugins/web-ctl/scripts/web-ctl.js run <session> extract --auto [--max-items N] [--max-field-length N]
+node ~/.agentsys/plugins/web-ctl/scripts/web-ctl.js run <session> extract --auto [--max-items N] [--max-field-length N]
 ```
 
 Extracts structured data from repeated list items. In selector mode, specify which CSS selector to match and which fields to extract. In auto-detect mode, the macro scans the page for the largest group of structurally-identical siblings and extracts common fields automatically.
@@ -346,13 +346,13 @@ Extracts structured data from repeated list items. In selector mode, specify whi
 
 ```bash
 # Extract titles and URLs from blog post cards
-node /Users/avifen/.agentsys/plugins/web-ctl/scripts/web-ctl.js run mysession extract --selector ".post-card" --fields "title,url,author,date"
+node ~/.agentsys/plugins/web-ctl/scripts/web-ctl.js run mysession extract --selector ".post-card" --fields "title,url,author,date"
 
 # Auto-detect repeated items on a search results page
-node /Users/avifen/.agentsys/plugins/web-ctl/scripts/web-ctl.js run mysession extract --auto --max-items 20
+node ~/.agentsys/plugins/web-ctl/scripts/web-ctl.js run mysession extract --auto --max-items 20
 
 # Extract product listings with images
-node /Users/avifen/.agentsys/plugins/web-ctl/scripts/web-ctl.js run mysession extract --selector ".product-item" --fields "title,url,image,text"
+node ~/.agentsys/plugins/web-ctl/scripts/web-ctl.js run mysession extract --selector ".product-item" --fields "title,url,image,text"
 ```
 
 Returns: `{ url, mode, selector, fields, count, items, snapshot }`
@@ -370,53 +370,53 @@ By default, snapshots are auto-scoped to the main content area of the page. The
 ### --snapshot-depth N - Limit Tree Depth
 
 ```bash
-node /Users/avifen/.agentsys/plugins/web-ctl/scripts/web-ctl.js run <session> snapshot --snapshot-depth 2
-node /Users/avifen/.agentsys/plugins/web-ctl/scripts/web-ctl.js run <session> goto <url> --snapshot-depth 3
+node ~/.agentsys/plugins/web-ctl/scripts/web-ctl.js run <session> snapshot --snapshot-depth 2
+node ~/.agentsys/plugins/web-ctl/scripts/web-ctl.js run <session> goto <url> --snapshot-depth 3
 ```
 
 Keeps only the top N levels of the ARIA tree. Deeper nodes are replaced with `- ...` truncation markers. Useful for large pages where the full tree exceeds context limits.
 
 ### --snapshot-selector sel - Scope to Subtree
 
 ```bash
-node /Users/avifen/.agentsys/plugins/web-ctl/scripts/web-ctl.js run <session> snapshot --snapshot-selector "css=nav"
-node /Users/avifen/.agentsys/plugins/web-ctl/scripts/web-ctl.js run <session> click "#btn" --snapshot-selector "#main"
+node ~/.agentsys/plugins/web-ctl/scripts/web-ctl.js run <session> snapshot --snapshot-selector "css=nav"
+node ~/.agentsys/plugins/web-ctl/scripts/web-ctl.js run <session> click "#btn" --snapshot-selector "#main"
 ```
 
 Takes the snapshot from a specific DOM subtree instead of the full body. Accepts the same selector syntax as other actions.
 
 ### --snapshot-full - Full Page Snapshot
 
 ```bash
-node /Users/avifen/.agentsys/plugins/web-ctl/scripts/web-ctl.js run <session> goto <url> --snapshot-full
-node /Users/avifen/.agentsys/plugins/web-ctl/scripts/web-ctl.js run <session> snapshot --snapshot-full
+node ~/.agentsys/plugins/web-ctl/scripts/web-ctl.js run <session> goto <url> --snapshot-full
+node ~/.agentsys/plugins/web-ctl/scripts/web-ctl.js run <session> snapshot --snapshot-full
 ```
 
 Bypasses the default auto-scoping to `<main>` and captures the full page body instead. Use this when you need to see navigation, headers, footers, or other content outside the main content area.
 
 ### --no-snapshot - Omit Snapshot
 
 ```bash
-node /Users/avifen/.agentsys/plugins/web-ctl/scripts/web-ctl.js run <session> click "#submit" --no-snapshot
-node /Users/avifen/.agentsys/plugins/web-ctl/scripts/web-ctl.js run <session> fill "#email" user@test.com --no-snapshot
+node ~/.agentsys/plugins/web-ctl/scripts/web-ctl.js run <session> click "#submit" --no-snapshot
+node ~/.agentsys/plugins/web-ctl/scripts/web-ctl.js run <session> fill "#email" user@test.com --no-snapshot
 ```
 
 Skips the snapshot entirely. The `snapshot` field is omitted from the JSON response. Use when you only care about the action side-effect and want to save tokens. The explicit `snapshot` action ignores this flag.
 
 ### --snapshot-max-lines N - Truncate by Line Count
 
 ```bash
-node /Users/avifen/.agentsys/plugins/web-ctl/scripts/web-ctl.js run <session> snapshot --snapshot-max-lines 50
-node /Users/avifen/.agentsys/plugins/web-ctl/scripts/web-ctl.js run <session> goto <url> --snapshot-max-lines 100
+node ~/.agentsys/plugins/web-ctl/scripts/web-ctl.js run <session> snapshot --snapshot-max-lines 50
+node ~/.agentsys/plugins/web-ctl/scripts/web-ctl.js run <session> goto <url> --snapshot-max-lines 100
 ```
 
 Hard-caps the snapshot output to N lines. A marker like `... (42 more lines)` is appended when lines are omitted. Applied after all other snapshot transforms, so it acts as a final safety net. Max value: 10000.
 
 ### --snapshot-compact - Token-Efficient Compact Format
 
 ```bash
-node /Users/avifen/.agentsys/plugins/web-ctl/scripts/web-ctl.js run <session> snapshot --snapshot-compact
-node /Users/avifen/.agentsys/plugins/web-ctl/scripts/web-ctl.js run <session> goto <url> --snapshot-compact
+node ~/.agentsys/plugins/web-ctl/scripts/web-ctl.js run <session> snapshot --snapshot-compact
+node ~/.agentsys/plugins/web-ctl/scripts/web-ctl.js run <session> goto <url> --snapshot-compact
 ```
 
 Applies four token-saving transforms in sequence:
@@ -431,8 +431,8 @@ Combines well with `--snapshot-collapse` and `--snapshot-text-only` for maximum
 ### --snapshot-collapse - Collapse Repeated Siblings
 
 ```bash
-node /Users/avifen/.agentsys/plugins/web-ctl/scripts/web-ctl.js run <session> snapshot --snapshot-collapse
-node /Users/avifen/.agentsys/plugins/web-ctl/scripts/web-ctl.js run <session> goto <url> --snapshot-collapse
+node ~/.agentsys/plugins/web-ctl/scripts/web-ctl.js run <session> snapshot --snapshot-collapse
+node ~/.agentsys/plugins/web-ctl/scripts/web-ctl.js run <session> goto <url> --snapshot-collapse
 ```
 
 Detects consecutive siblings of the same ARIA type at each depth level and collapses them. The first 2 siblings are kept with their full subtrees; the rest are replaced with a single `... (K more <type>)` marker. Works recursively on nested structures.
@@ -442,8 +442,8 @@ Ideal for navigation menus, long lists, and data tables where dozens of identica
 ### --snapshot-text-only - Content Only Mode
 
 ```bash
-node /Users/avifen/.agentsys/plugins/web-ctl/scripts/web-ctl.js run <session> snapshot --snapshot-text-only
-node /Users/avifen/.agentsys/plugins/web-ctl/scripts/web-ctl.js run <session> goto <url> --snapshot-text-only --snapshot-max-lines 50
+node ~/.agentsys/plugins/web-ctl/scripts/web-ctl.js run <session> snapshot --snapshot-text-only
+node ~/.agentsys/plugins/web-ctl/scripts/web-ctl.js run <session> goto <url> --snapshot-text-only --snapshot-max-lines 50
 ```
 
 Strips structural container nodes (list, listitem, group, region, main, form, table, row, grid, generic, etc.) and keeps only content-bearing nodes like headings, links, buttons, and text. Structural nodes that carry a label (e.g., `navigation "Main"`) are preserved. Indentation is re-compressed to close gaps left by removed nodes.
@@ -481,9 +481,9 @@ When `goto` returns a Cloudflare challenge, CAPTCHA, or any bot detection page (
 ```bash
 # 1. goto returns bot detection page
 # 2. Use checkpoint to let user solve it
-node /Users/avifen/.agentsys/plugins/web-ctl/scripts/web-ctl.js run <session> checkpoint
+node ~/.agentsys/plugins/web-ctl/scripts/web-ctl.js run <session> checkpoint
 # 3. After user solves, continue normally
-node /Users/avifen/.agentsys/plugins/web-ctl/scripts/web-ctl.js run <session> snapshot
+node ~/.agentsys/plugins/web-ctl/scripts/web-ctl.js run <session> snapshot
 ```
 
 NEVER silently fall back to an alternative method (APIs, WebFetch, etc.) when the user asked to use web-ctl. The user invoked this tool for a reason.
@@ -493,24 +493,24 @@ Example recovery flow:
 ```bash
 # Action failed with element_not_found - snapshot is in the error response
 # Use it to find the correct selector, then retry
-node /Users/avifen/.agentsys/plugins/web-ctl/scripts/web-ctl.js run mysession click "role=button[name='Sign In']"
+node ~/.agentsys/plugins/web-ctl/scripts/web-ctl.js run mysession click "role=button[name='Sign In']"
 ```
 
 ## Workflow Pattern
 
 ```bash
 # Navigate
-node /Users/avifen/.agentsys/plugins/web-ctl/scripts/web-ctl.js run session goto "https://example.com"
+node ~/.agentsys/plugins/web-ctl/scripts/web-ctl.js run session goto "https://example.com"
 
 # Understand page
-node /Users/avifen/.agentsys/plugins/web-ctl/scripts/web-ctl.js run session snapshot
+node ~/.agentsys/plugins/web-ctl/scripts/web-ctl.js run session snapshot
 
 # Interact
-node /Users/avifen/.agentsys/plugins/web-ctl/scripts/web-ctl.js run session click "role=link[name='Login']"
-node /Users/avifen/.agentsys/plugins/web-ctl/scripts/web-ctl.js run session fill "#email" user@example.com
-node /Users/avifen/.agentsys/plugins/web-ctl/scripts/web-ctl.js run session fill "#password" secretpass
-node /Users/avifen/.agentsys/plugins/web-ctl/scripts/web-ctl.js run session click "role=button[name='Submit']"
+node ~/.agentsys/plugins/web-ctl/scripts/web-ctl.js run session click "role=link[name='Login']"
+node ~/.agentsys/plugins/web-ctl/scripts/web-ctl.js run session fill "#email" user@example.com
+node ~/.agentsys/plugins/web-ctl/scripts/web-ctl.js run session fill "#password" secretpass
+node ~/.agentsys/plugins/web-ctl/scripts/web-ctl.js run session click "role=button[name='Submit']"
 
 # Verify result
-node /Users/avifen/.agentsys/plugins/web-ctl/scripts/web-ctl.js run session snapshot
+node ~/.agentsys/plugins/web-ctl/scripts/web-ctl.js run session snapshot
 ```
PATCH

echo "Gold patch applied."
