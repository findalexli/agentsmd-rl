#!/usr/bin/env bash
set -euo pipefail

cd /workspace/actionbook

# Idempotency guard
if grep -qF "- Search by task description, not element name (\"arxiv search papers\" not \"searc" "skills/actionbook/SKILL.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/skills/actionbook/SKILL.md b/skills/actionbook/SKILL.md
@@ -13,229 +13,93 @@ Activate this skill when the user:
 - Asks how to interact with a website ("How do I post a tweet?")
 - Builds browser-based AI agents or web scrapers
 - Writes E2E tests for external websites
+- Navigate to any new page during browser automation
 
-## What Actionbook Provides
-
-Action manuals include:
-
-1. **Step-by-step instructions** - The exact sequence to complete a task
-2. **Verified selectors** - CSS/XPath selectors for each element
-3. **Element metadata** - Type (button, input, etc.) and allowed methods (click, type, fill)
 
 ## How to Use
 
-Actionbook can be used in two ways: via CLI (Recommended) or via MCP.
-
-### Method A: Using CLI (Recommended)
+### Method 1: CLI (Recommended)
 
-**Step 1: Search for Action Manuals**
-
-Use the `actionbook search` command:
+**Phase 1: Get Action Manual**
 
 ```bash
-actionbook search "linkedin send message"
-actionbook search "airbnb book listing"
-actionbook search "twitter post tweet"
-```
+# Step 1: Search for action manuals
+actionbook search "arxiv search papers"
+# Returns: action IDs with scores
 
-**Step 2: Get the Full Manual**
-
-Use the `actionbook get` command with the action ID:
-
-```bash
-actionbook get "site/linkedin.com/page/profile/element/message-button"
+# Step 2: Get the full manual
+actionbook get "https://arxiv.org/search/advanced"
+# Returns: Page structure, UI Elements with CSS/XPath selectors
 ```
 
-### Method B: Using MCP (Alternative)
-
-If you have the Actionbook MCP server configured, you can also use MCP tools.
-
-**Step 1: Search for Action Manuals**
-
-Call the MCP tool `search_actions` with a task description:
-
-```typescript
-// MCP tool call
-search_actions({
-  query: "linkedin send message"
-})
-```
-
-**Step 2: Get the Full Manual**
-
-Call the MCP tool `get_action_by_id` with the action ID from search results:
-
-```typescript
-// MCP tool call
-get_action_by_id({
-  actionId: "site/linkedin.com/page/profile/element/message-button"
-})
-```
-
-## Execute the Steps
-
-Follow the manual steps in order, using the provided selectors.
-
-### Option A: Using actionbook browser
-
-The `actionbook browser` command wraps agent-browser to provide powerful browser automation capabilities.
-
-#### Quick Start
+**Phase 2: Execute with Browser**
 
 ```bash
-actionbook browser open <url>        # Navigate to page
-actionbook browser snapshot -i       # Get interactive elements with refs
-actionbook browser click @e1         # Click element by ref
-actionbook browser close             # Close browser
-```
+# Step 3: Open browser
+actionbook browser open "https://arxiv.org/search/advanced"
+actionbook browser wait --load networkidle
 
-#### Core Workflow
+# Step 4: Use CSS selectors from Action Manual directly
+actionbook browser fill "#terms-0-term" "Neural Network"
+actionbook browser select "#terms-0-field" "title"
+actionbook browser click "#date-filter_by-2"
+actionbook browser fill "#date-year" "2025"
+actionbook browser click "form[action='/search/advanced'] button.is-link"
 
-1. **Navigate**: `actionbook browser open <url>`
-2. **Snapshot**: `actionbook browser snapshot -i` (returns elements with refs like `@e1`, `@e2`)
-3. **Interact** using refs from the snapshot
-4. **Re-snapshot** after navigation or significant DOM changes
+# Step 5: Wait for results
+actionbook browser wait --load networkidle
 
-**Element References (@refs)**: Instead of using CSS selectors directly, take a snapshot to get numbered references (@e1, @e2, etc.) that point to interactive elements. This dramatically reduces complexity when automating tasks.
+# Step 6: Extract data (snapshot only when needed for data extraction)
+actionbook browser snapshot
 
-#### Essential Commands
-
-**Navigation**:
-```bash
-actionbook browser open <url>      # Navigate to URL
-actionbook browser back            # Go back
-actionbook browser forward         # Go forward
-actionbook browser reload          # Reload page
-actionbook browser close           # Close browser
-```
-
-**Snapshot (Page Analysis)**:
-```bash
-actionbook browser snapshot            # Full accessibility tree
-actionbook browser snapshot -i         # Interactive elements only (recommended)
-actionbook browser snapshot -c         # Compact output
-actionbook browser snapshot -d 3       # Limit depth to 3
-```
-
-**Interactions (using @refs from snapshot)**:
-```bash
-actionbook browser click @e1           # Click
-actionbook browser fill @e2 "text"     # Clear and type
-actionbook browser type @e2 "text"     # Type without clearing
-actionbook browser press Enter         # Press key
-actionbook browser hover @e1           # Hover
-actionbook browser check @e1           # Check checkbox
-actionbook browser select @e1 "value"  # Select dropdown option
-```
-
-**Get Information**:
-```bash
-actionbook browser get text @e1        # Get element text
-actionbook browser get html @e1        # Get innerHTML
-actionbook browser get value @e1       # Get input value
-actionbook browser get url             # Get current URL
-```
-
-**Wait Conditions**:
-```bash
-actionbook browser wait @e1                     # Wait for element
-actionbook browser wait 2000                    # Wait milliseconds
-actionbook browser wait --text "Success"        # Wait for text
-actionbook browser wait --url "**/dashboard"    # Wait for URL pattern
-actionbook browser wait --load networkidle      # Wait for network idle
-```
-
-**Screenshots & Recording**:
-```bash
-actionbook browser screenshot          # Save to temp directory
-actionbook browser screenshot path.png # Save to specific path
-actionbook browser screenshot --full   # Full page screenshot
-actionbook browser pdf output.pdf      # Save as PDF
-```
-
-**Common Options**:
-```bash
---session <name>    # Isolated browser session
---json              # JSON output for parsing
---headed            # Show browser window (not headless)
-```
-
-#### Complete Workflow Example
-
-Combining Actionbook manual retrieval with browser execution:
-
-```bash
-# Step 1: Search for action manual
-actionbook search "linkedin send message"
-
-# Step 2: Get the manual
-actionbook get "site/linkedin.com/page/profile/element/message-button"
-
-# Step 3: Execute with browser
-actionbook browser open linkedin.com/in/username
-actionbook browser snapshot -i
-# Output shows: button "Message" [ref=@e5], textbox [ref=@e12], button "Send" [ref=@e13]
-
-actionbook browser click @e5       # Click Message button
-actionbook browser fill @e12 "Hello! I'd like to connect."
-actionbook browser click @e13      # Click Send button
-actionbook browser wait --text "Message sent"
+# Step 7: Close browser
 actionbook browser close
 ```
 
-For more advanced features and detailed documentation, see the [actionbook browser Command Reference](#actionbook-browser-command-reference) below.
+### Method 2: MCP Server
 
-### Option B: Using Playwright/Puppeteer
+```typescript
+// Step 1: Search
+search_actions({ query: "arxiv search papers" })
 
-```javascript
-// LinkedIn send message example
-await page.click('[data-testid="profile-avatar"]')
-await page.click('button[aria-label="Message"]')
-await page.type('div[role="textbox"]', 'Hello!')
-await page.click('button[type="submit"]')
+// Step 2: Get manual
+get_action_by_id({ actionId: "https://arxiv.org/search/advanced" })
 ```
 
-## Advanced Features
-
-For complete command reference and advanced features, see:
-
-📘 **[Command Reference](references/command-reference.md)** - Comprehensive documentation for all commands including:
-- Navigation, snapshot, and interaction commands
-- Information retrieval and state verification
-- Wait conditions and media capture
-- Mouse control and semantic locators
-- Browser settings, cookies & storage
-- Network control, tabs & windows
-- Debugging tools and practical examples
-
-### Deep-Dive Documentation
+## Action Manual Format
 
-For detailed patterns and best practices:
+Action manuals return:
+- **Page URL** - Target page address
+- **Page Structure** - DOM hierarchy and key sections
+- **UI Elements** - CSS/XPath selectors with element metadata
 
-| Reference | Description |
-|-----------|-------------|
-| [references/command-reference.md](references/command-reference.md) | Complete command reference with all features |
-| [references/snapshot-refs.md](references/snapshot-refs.md) | Ref lifecycle, invalidation rules, troubleshooting |
-| [references/session-management.md](references/session-management.md) | Parallel sessions, state persistence, concurrent scraping |
-| [references/authentication.md](references/authentication.md) | Login flows, OAuth, 2FA handling, state reuse |
-| [references/video-recording.md](references/video-recording.md) | Recording workflows for debugging and documentation |
-| [references/proxy-support.md](references/proxy-support.md) | Proxy configuration, geo-testing, rotating proxies |
-
-### Ready-to-Use Templates
+```yaml
+UI Elements:
+  input_terms_0_term:
+    CSS: #terms-0-term
+    XPath: //input[@id='terms-0-term']
+    Type: input
+    Methods: click, type, clear
+```
 
-Executable workflow scripts for common patterns:
+## Essential Commands
 
-| Template | Description |
-|----------|-------------|
-| [templates/form-automation.sh](templates/form-automation.sh) | Form filling with validation |
-| [templates/authenticated-session.sh](templates/authenticated-session.sh) | Login once, reuse state |
-| [templates/capture-workflow.sh](templates/capture-workflow.sh) | Content extraction with screenshots |
+| Category | Commands |
+|----------|----------|
+| Navigation | `open <url>`, `back`, `forward`, `reload`, `close` |
+| Snapshot | `snapshot`, `snapshot -i` (interactive only) |
+| Interaction | `click`, `fill`, `type`, `select`, `check`, `press` |
+| Wait | `wait <ms>`, `wait --load networkidle`, `wait --text "..."` |
+| Info | `get text @ref`, `get url`, `get value @ref` |
+| Capture | `screenshot`, `screenshot --full`, `pdf` |
 
 ## Guidelines
 
-- **Search by task**: Describe what you want to accomplish, not just the element (e.g., "linkedin send message" not "linkedin message button")
-- **Follow the order**: Execute steps in sequence as provided in the manual
-- **Trust the selectors**: Actionbook selectors are verified and maintained
+- Search by task description, not element name ("arxiv search papers" not "search button")
+- **Use Action Manual selectors first** - they are pre-verified and don't require snapshot
+- Prefer CSS ID selectors (`#id`) over XPath when both are provided
+- **Fallback to snapshot only when selectors fail** - use `snapshot -i` then @refs
+- Re-snapshot after navigation - DOM changes invalidate @refs
 
 ## Fallback Strategy
 
@@ -254,3 +118,13 @@ These conditions are not signaled in Actionbook API responses. They can only be
 ### Fallback Approaches
 
 When Actionbook data does not work as expected, direct browser access to the target website allows for real-time retrieval of current page structure, element information, and interaction capabilities.
+
+## Advanced Features
+
+For complete command reference and advanced features, see:
+- [references/command-reference.md](references/command-reference.md) - All commands
+- [references/authentication.md](references/authentication.md) - Login flows, OAuth, 2FA
+- [references/session-management.md](references/session-management.md) - Parallel sessions
+- [references/snapshot-refs.md](references/snapshot-refs.md) - Ref lifecycle
+- [references/video-recording.md](references/video-recording.md) - Recording workflows
+- [references/proxy-support.md](references/proxy-support.md) - Proxy configuration
PATCH

echo "Gold patch applied."
