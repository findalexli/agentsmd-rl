#!/usr/bin/env bash
set -euo pipefail

cd /workspace/actionbook

# Idempotency guard
if grep -qF "description: Activate when the user needs to interact with any website \u2014 browser" "skills/actionbook/SKILL.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/skills/actionbook/SKILL.md b/skills/actionbook/SKILL.md
@@ -1,17 +1,19 @@
 ---
 name: actionbook
-description: This skill should be used when the user needs to automate multi-step website tasks. Activates for browser automation, web scraping, UI testing, or building AI agents. Provides complete action manuals with step-by-step instructions and verified selectors.
+description: Activate when the user needs to interact with any website — browser automation, web scraping, screenshots, form filling, UI testing, monitoring, or building AI agents. Provides verified action manuals with step-by-step instructions and pre-tested selectors.
 ---
 
 ## When to Use This Skill
 
-Activate this skill when the user:
+**Activate this skill when the user's request involves interacting with a website or web page**
 
-- Needs to complete a multi-step task ("Send a LinkedIn message", "Book an Airbnb")
-- Asks how to interact with a website ("How do I post a tweet?")
-- Builds browser-based AI agents or web scrapers
-- Writes E2E tests for external websites
-- Navigates to any new page during browser automation
+Activate when the user:
+- Needs to do anything on a website ("Send a LinkedIn message", "Book an Airbnb", "Search Google for...")
+- Asks how to interact with a site ("How do I post a tweet?", "How to apply on LinkedIn?")
+- Wants to fill out forms, click buttons, navigate, search, filter, or browse on a specific site
+- Wants to take a screenshot of a web page or monitor changes
+- Builds browser-based AI agents, web scrapers, or E2E tests for external websites
+- Automates repetitive web tasks (data entry, form submission, content posting)
 - Wants to control their existing Chrome browser (Extension mode)
 
 ## Browser Modes
@@ -23,33 +25,55 @@ Actionbook supports two browser control modes:
 | **CDP** (default) | (none) | Launches a dedicated browser instance via Chrome DevTools Protocol |
 | **Extension** | `--extension` | Controls the user's existing Chrome browser via a Chrome Extension + WebSocket bridge |
 
-**When to use Extension mode:**
-- The user wants to operate on their already-open Chrome (with existing logins, cookies, tabs)
-- The task requires interacting with pages that need the user's real session state
-- The user explicitly mentions their Chrome browser, extension, or existing tabs
+**Extension mode:** Use when the user wants to operate their already-open Chrome (existing logins, cookies, tabs), or when the task requires the user's real session state.
 
-**When to use CDP mode (default):**
-- Clean browser environment is preferred
-- Headless automation or CI/CD
-- Profile-based session isolation is needed
+**CDP mode (default):** Use for clean environments, headless automation, CI/CD, or profile-based session isolation.
 
-All `actionbook browser` commands work identically in both modes. The only difference is adding `--extension` flag (or setting `ACTIONBOOK_EXTENSION=1`).
+All commands work identically in both modes — the only difference is the `--extension` flag (or `ACTIONBOOK_EXTENSION=1`).
 
 ## How to Use
 
+> **CRITICAL RULE — Action Manual First (Per-Page-Type):**
+> Before executing ANY `actionbook browser` command on a page, complete Phase 1 (`actionbook search` → `actionbook get`). This includes ALL browser commands: `click`, `fill`, `text`, `eval`, `snapshot`, `screenshot`, and any other interaction.
+>
+> **This rule applies per page type.** Every time you navigate to a page with a different URL pattern, repeat Phase 1 before any interaction:
+>
+> 1. `actionbook search` — query by task description for the new page type
+> 2. `actionbook get` — if a manual exists, retrieve selectors
+> 3. **Only then** execute browser commands, using Action Manual selectors first
+> 4. If no manual exists → `actionbook browser snapshot` as fallback
+>
+> **What counts as a "different page type":**
+> - Different URL path structure (e.g., `x.com/home` → `x.com/:user/status/:id`)
+> - Different functional purpose (e.g., search results page → item detail page)
+> - Different domain or subdomain
+> - Note: Pagination, sorting, or refreshing within the same page type does NOT count
+>
+> **Common violation:** Having prior knowledge of a site's DOM does NOT exempt you from this rule. Action Manual selectors are pre-verified and maintained; selectors from memory may be outdated.
+
 ### Phase 1: Get Action Manual
 
 ```bash
-# Step 1: Search for action manuals
+# Step 1: Search for action manuals (always do this first)
 actionbook search "arxiv search papers"
 # Returns: area IDs with descriptions
 
 # Step 2: Get the full manual (use area_id from search results)
 actionbook get "arxiv.org:/search/advanced:default"
 # Returns: Page structure, UI Elements with CSS/XPath selectors
+
+# If you navigate to a NEW page type, repeat Steps 1-2 for that page.
+# Example: after landing on a paper detail page:
+#   actionbook search "arxiv paper abstract page"
+#   actionbook get "arxiv.org:/abs/1910.06709:default"
 ```
 
-### Phase 2: Execute with Browser (CDP mode — default)
+### Phase 2: Execute with Browser
+
+After opening a page, choose your path:
+- **Have Action Manual selectors?** → Use them directly. Do not run `snapshot`.
+- **Manual selector fails at runtime?** → `snapshot` → retry with snapshot selectors (see Fallback Strategy).
+- **No Action Manual at all?** → `snapshot` as primary source.
 
 ```bash
 # Step 3: Open browser
@@ -94,24 +118,22 @@ actionbook --extension browser close    # release debug connection FIRST
 actionbook extension stop               # then stop bridge server
 ```
 
+> **Extension mode tabs:** `browser close` closes the current tab. Close tabs opened via `browser open` when the task is done. Do not close pre-existing tabs.
+
 ## Action Manual Format
 
-Action manuals return:
-- **Page URL** - Target page address
-- **Page Structure** - DOM hierarchy and key sections
-- **UI Elements** - CSS/XPath selectors with element metadata
+Action manuals return page URL, page structure (DOM hierarchy), and UI elements with selectors:
 
 ```yaml
   ### button_advanced_search
-
   - ID: button_advanced_search
   - Description: Advanced search navigation button
   - Type: link
   - Allow Methods: click
   - Selectors:
-    - role: getByRole('link', { name: 'Advanced Search' }) (confidence: 0.9)
     - css: button.button.is-small.is-cul-darker (confidence: 0.65)
     - xpath: //button[contains(@class, 'button')] (confidence: 0.55)
+    - role: getByRole('link', { name: 'Advanced Search' }) (confidence: 0.9)
 ```
 
 ## Action Search Commands
@@ -156,8 +178,7 @@ actionbook extension ping      # should show "responded"
 
 ## Browser Commands
 
-> All browser commands below work in both CDP and Extension mode.
-> For Extension mode, add `--extension` flag or set `ACTIONBOOK_EXTENSION=1`.
+All browser commands work in both CDP and Extension mode. For Extension mode, add `--extension` flag or set `ACTIONBOOK_EXTENSION=1`.
 
 ### Navigation
 
@@ -174,7 +195,9 @@ actionbook browser restart                     # Restart browser
 actionbook browser connect <endpoint>          # Connect to existing browser (CDP port or URL)
 ```
 
-### Interactions (use CSS selectors from Action Manual)
+### Interactions
+
+Every selector you pass to these commands must come from an Action Manual (`actionbook get`) or a `snapshot` taken in this session. Do not use selectors from memory or training data.
 
 ```bash
 actionbook browser click "<selector>"                  # Click element
@@ -219,6 +242,8 @@ actionbook browser pdf output.pdf              # Export as PDF
 
 ### JavaScript & Inspection
 
+> **`eval` is last-resort only.** Before using `browser eval` with `querySelector`, you must have already run `snapshot` on this page. Base selectors on snapshot/inspect output, never on memorized DOM knowledge.
+
 ```bash
 actionbook browser eval "document.title"               # Execute JS
 actionbook browser inspect 100 200                     # Inspect at coordinates
@@ -228,12 +253,8 @@ actionbook browser inspect 100 200 --desc "login btn"  # With description
 ### Cookies
 
 ```bash
-actionbook browser cookies list                # List all cookies
-actionbook browser cookies get "name"          # Get cookie
-actionbook browser cookies set "name" "value"  # Set cookie
+actionbook browser cookies list/get/set/delete/clear
 actionbook browser cookies set "name" "value" --domain ".example.com"
-actionbook browser cookies delete "name"       # Delete cookie
-actionbook browser cookies clear               # Clear all
 ```
 
 ## Global Flags
@@ -250,16 +271,30 @@ actionbook --extension <command>         # Use Chrome Extension mode
 
 ## Guidelines
 
+### Selector Priority
 - Search by task description, not element name ("arxiv search papers" not "search button")
-- **Use Action Manual selectors first** - they are pre-verified and don't require snapshot
+- Prefer Action Manual selectors — they are pre-verified and don't require snapshot
 - Prefer CSS ID selectors (`#id`) over XPath when both are provided
-- **Fallback to snapshot when selectors fail** - use `actionbook browser snapshot` then CSS selectors from the output
-- Re-snapshot after navigation - DOM changes invalidate previous state
-- **Extension mode**: follow the full lifecycle — pre-flight → connect → execute → cleanup (see [Extension Mode Lifecycle](#extension-mode-lifecycle-critical))
-- **Extension mode**: verify extension is installed before starting bridge; prefer auto-pair over manual token
-- **Extension mode**: always run `browser close` before stopping the bridge to release the debug connection
-- **Extension mode**: the user's real browser is being controlled — avoid destructive actions (clearing all cookies, closing all tabs) without confirmation
-- **Extension mode**: L3 operations (some cookie/storage modifications) may require manual approval in the extension popup
+- Fall back to snapshot when selectors fail
+
+### Prohibited Patterns
+- Do not run `snapshot` when you already have Action Manual selectors — snapshot is a fallback, not a discovery step
+- Do not use `browser eval` with hardcoded/memorized selectors to bypass the workflow
+- Do not skip search because a page "looks similar" to one you already searched — different URL patterns require separate searches
+- Do not use `browser text` or `browser eval` as the first command on a new page type without completing Phase 1
+
+### Extension Mode
+- Follow the full lifecycle — pre-flight → connect → execute → cleanup (see [Extension Mode Lifecycle](#extension-mode-lifecycle-critical))
+- Verify extension is installed before starting bridge; prefer auto-pair over manual token
+- Always run `browser close` before stopping the bridge to release the debug connection
+- The user's real browser is being controlled — avoid destructive actions (clearing all cookies, closing all tabs) without confirmation
+- L3 operations (some cookie/storage modifications) may require manual approval in the extension popup
+
+### Browser Lifecycle
+Always clean up when the task is complete:
+- **CDP mode:** Run `actionbook browser close` as the final step
+- **Extension mode:** `browser close` to release debug connection → `extension stop` to stop bridge
+- **Exception:** Only skip cleanup if the user explicitly asks to keep the tab open
 
 ## Fallback Strategy
 
@@ -271,14 +306,18 @@ Actionbook stores pre-computed page data captured at indexing time. This data ma
 - **Element mismatch** - The selector matches an element with unexpected type or behavior
 - **Multiple selector failures** - Several selectors from the same action fail consecutively
 
-### Fallback Approaches
+### Fallback Chain
 
-When Action Manual selectors don't work:
+When Action Manual selectors don't work, follow this ordered fallback chain:
 
-1. **Snapshot the page** - `actionbook browser snapshot` to get the current accessibility tree
-2. **Inspect visually** - `actionbook browser screenshot` to see the current state
-3. **Inspect by coordinates** - `actionbook browser inspect <x> <y>` to find elements
-4. **Execute JS** - `actionbook browser eval "document.querySelector(...)"` for dynamic queries
+1. **Snapshot the page** — `actionbook browser snapshot` to get the current accessibility tree; use selectors from the snapshot output
+2. **Inspect visually** — `actionbook browser screenshot` to see the current state
+3. **Inspect by coordinates** — `actionbook browser inspect <x> <y>` to find elements at specific positions
+4. **Execute JS (last resort)** — Before using `eval`, verify:
+   1. Have I run `snapshot` on this page? (If no → snapshot first)
+   2. Is my selector from snapshot/inspect output in this session? (If no → stop, you're using memorized selectors)
+   3. Did snapshot selectors already fail? (If no → use snapshot selectors instead)
+   Only proceed with `eval` if all checks pass.
 
 ### When to Exit
 
@@ -315,6 +354,7 @@ actionbook --extension browser open "https://github.com/notifications"
 actionbook --extension browser wait-nav
 actionbook --extension browser text ".notifications-list"
 actionbook --extension browser screenshot notifications.png
+actionbook --extension browser close
 ```
 
 ### Extension Mode Lifecycle (CRITICAL)
@@ -411,6 +451,33 @@ actionbook extension ping               # Check connectivity
 actionbook extension serve              # Prints new token
 ```
 
+### Multi-page-type workflow (re-search on navigation)
+
+```bash
+# === Page Type 1: x.com/home (timeline) ===
+actionbook search "twitter timeline" --domain x.com
+actionbook get "x.com:/:default"
+actionbook --extension browser open "https://x.com/home"
+# Action Manual returned selectors → use them directly (no snapshot)
+actionbook --extension browser text "<selector-from-manual>"
+
+# === Navigate to Page Type 2: x.com/:user/status/:id ===
+# Different page type → re-search before any interaction
+actionbook search "twitter tweet detail" --domain x.com
+# No results? Use snapshot fallback:
+actionbook --extension browser snapshot
+actionbook --extension browser text "<selector-from-snapshot>"
+
+# === Back to Page Type 1 ===
+actionbook --extension browser back
+# Same page type as before — Action Manual selectors are still valid (page structure is stable).
+# No need to re-search or re-snapshot. However, dynamic content (e.g., new tweets loaded)
+# may differ — if you need fresh content, use `browser text` with the same Manual selectors.
+
+# === Done — close the tab we opened ===
+actionbook --extension browser close
+```
+
 ### Deep-Dive Documentation
 
 For detailed patterns and best practices:
PATCH

echo "Gold patch applied."
