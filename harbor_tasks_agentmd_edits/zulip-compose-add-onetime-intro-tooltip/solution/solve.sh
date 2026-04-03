#!/usr/bin/env bash
set -euo pipefail

cd /workspace/zulip

# Idempotent: skip if already applied
if grep -q 'intro_go_to_conversation_tooltip' zerver/lib/onboarding_steps.py 2>/dev/null; then
    echo "Patch already applied."
    exit 0
fi

# Apply the full gold patch (code + config changes)
git apply --whitespace=fix - <<'PATCH'
diff --git a/.claude/skills/visual-test/SKILL.md b/.claude/skills/visual-test/SKILL.md
index be0056d7eef0a..cae6d447b15c6 100644
--- a/.claude/skills/visual-test/SKILL.md
+++ b/.claude/skills/visual-test/SKILL.md
@@ -5,21 +5,15 @@ description: "Visually verify UI changes using Puppeteer screenshots. Use when y

 # Visual Test

-User-invocable skill for visually verifying UI changes using Puppeteer
-screenshots.
-
-## When to use
-
-When you need to visually verify that a UI change looks correct —
-layout, colors, popover positioning, text content, etc. This runs a
-real browser against the Zulip test server and takes screenshots that
-you can read as images.
+Runs a real browser against the Zulip test server and takes
+screenshots you can read as images to verify layout, colors,
+positioning, text content, etc.

 ## Steps

 ### 1. Write the puppeteer test script

-Create `web/e2e-tests/_claude_feature_x_test.test.ts` using this template:
+Create `web/e2e-tests/_claude_<feature>_test.test.ts` using this template:

 ```typescript
 import type {Page} from "puppeteer";
@@ -41,14 +35,236 @@ Adapt the body to exercise whatever UI you need to verify. Take a
 screenshot at every visually significant state using descriptive names
 like `step-2-color-picker-open`, `step-3-color-selected`.

+**Important patterns:**
+
+These patterns are derived from the existing Puppeteer tests in
+`web/e2e-tests/`. Follow them to write reliable, non-flaky tests.
+
+#### Waiting: never use hardcoded timeouts
+
+The existing test suite has essentially zero `setTimeout` calls
+(the two in `common.ts` are explicitly commented workarounds for
+specific animation flakes). Always wait for the specific condition
+you expect instead. The three main waiting primitives, in order of
+preference:
+
+- **`waitForSelector`** — wait for an element to appear or disappear.
+  This is the most common pattern in the test suite (100+ uses):
+
+  ```typescript
+  // Wait for element to be visible (most common)
+  await page.waitForSelector("#left-sidebar", {visible: true});
+
+  // Wait for element to disappear (e.g., overlay closed, row deleted)
+  await page.waitForSelector("#subscription_overlay", {hidden: true});
+  ```
+
+- **`waitForFunction`** — wait for a condition that can't be
+  expressed as a single selector (text content, element count,
+  attribute value, application state):
+
+  ```typescript
+  // Wait for specific text content
+  await page.waitForFunction(
+      () => document.querySelector(".save-button")?.textContent?.trim() === "Save changes",
+  );
+
+  // Wait for element count after filtering
+  await page.waitForFunction(
+      () => document.querySelectorAll(".linkifier_row").length === 4,
+  );
+
+  // Wait for an input's value to update
+  await page.waitForFunction(
+      () => document.querySelector<HTMLInputElement>("#full_name")?.value === "New name",
+  );
+
+  // Wait for focus to land on a specific element
+  await page.waitForFunction(
+      () => document.activeElement?.classList?.contains("search") === true,
+  );
+
+  // Wait for internal app state via zulip_test
+  await page.waitForFunction(
+      (content) => {
+          const last_msg = zulip_test.current_msg_list?.last();
+          return last_msg !== undefined && last_msg.raw_content === content
+              && !last_msg.locally_echoed;
+      },
+      {},
+      content,
+  );
+  ```
+
+- **`waitForNavigation`** — only for actual full-page navigations
+  (form submits, reloads). Wrap with `Promise.all` when the
+  navigation is triggered by an action:
+  ```typescript
+  await Promise.all([
+      page.waitForNavigation(),
+      page.$eval("form#login_form", (form) => { form.submit(); }),
+  ]);
+  ```
+
+#### Interacting with elements
+
+- **`page.click(selector)`** is the standard for clicking. When it's
+  unreliable (overlapping elements, timing), fall back to clicking
+  via `evaluate` — several existing tests do this with a comment
+  explaining why:
+
+  ```typescript
+  // When page.click() is unreliable, click via the DOM directly
+  await page.evaluate(() => {
+      document.querySelector<HTMLElement>(".dialog_submit_button")?.click();
+  });
+  ```
+
+- **`page.type(selector, text)`** for typing. Use `{delay: 100}`
+  when typing triggers a typeahead or filter that needs per-keystroke
+  updates:
+
+  ```typescript
+  await page.type('[name="user_list_filter"]', "ot", {delay: 100});
+  ```
+
+- **`common.clear_and_type(page, selector, text)`** to replace
+  existing input content (triple-click + Delete + type).
+
+- **`common.fill_form(page, selector, params)`** to fill multiple
+  form fields at once — handles text inputs, checkboxes (by
+  toggling), and `<select>` elements.
+
+- **`common.select_item_via_typeahead(page, selector, str, item)`**
+  to type into a field and pick a typeahead suggestion.
+
+- **`page.keyboard.press("KeyC")`** for Zulip keyboard shortcuts.
+  After pressing, wait for the resulting UI change:
+
+  ```typescript
+  await page.keyboard.press("KeyC");
+  await page.waitForSelector("#compose-textarea", {visible: true});
+  ```
+
+- **Hover before clicking action buttons** that only appear on
+  hover (e.g., message action icons):
+  ```typescript
+  const msg = (await page.$$(".message_row")).at(-1)!;
+  await msg.hover();
+  await page.waitForSelector(".message-actions-menu-button", {visible: true});
+  await page.click(".message-actions-menu-button");
+  ```
+
+#### Navigating within the app
+
+- **Click sidebar items** for in-app navigation:
+
+  ```typescript
+  await page.click(".narrow-filter[data-stream-id='...'] .stream-name");
+  await page.waitForSelector("#message_view_header .zulip-icon-hashtag", {visible: true});
+  ```
+
+- **`page.goto(url)`** for hash-route navigation:
+
+  ```typescript
+  await page.goto(`http://zulip.zulipdev.com:9981/#channels/${stream_id}/Denmark`);
+  ```
+
+- **`common.manage_organization(page)`** to navigate to org settings,
+  **`common.open_personal_menu(page)`** to open the personal menu.
+
+#### Reading state with page.evaluate
+
+Use `page.evaluate()` to read internal application state or DOM
+properties not accessible through selectors:
+
+```typescript
+// Read internal Zulip state via the zulip_test global
+const stream_id = await page.evaluate(
+    () => zulip_test.get_sub("Verona")!.stream_id,
+);
+
+// Read DOM properties
+const page_language = await page.evaluate(
+    () => document.documentElement.lang,
+);
+```
+
+#### Changing user settings via the API
+
+Use `page.evaluate` with `fetch()` and reload, rather than clicking
+through the settings UI:
+
+```typescript
+await page.evaluate(async () => {
+    const csrfToken = document.querySelector<HTMLInputElement>(
+        'input[name="csrfmiddlewaretoken"]',
+    )?.value ?? "";
+    await fetch("/json/settings", {
+        method: "PATCH",
+        headers: {
+            "Content-Type": "application/x-www-form-urlencoded",
+            "X-CSRFToken": csrfToken,
+        },
+        body: "user_list_style=1",
+    });
+});
+await page.reload({waitUntil: "networkidle2"});
+```
+
+#### XPath selectors for text matching
+
+When you need to match elements by text content, use XPath with
+`common.has_class_x()`:
+
+```typescript
+await page.waitForSelector(
+    `xpath///*[${common.has_class_x("stream-name")} and normalize-space()="Verona"]`,
+);
+```
+
+#### Assertions for visual tests
+
+For visual test scripts, prefer a soft-assertion pattern that
+reports all failures rather than aborting on the first:
+
+```typescript
+const results: string[] = [];
+function check(name: string, ok: boolean): void {
+    results.push(`${ok ? "PASS" : "FAIL"}: ${name}`);
+    console.log(`${ok ? "PASS" : "FAIL"}: ${name}`);
+}
+// ... run checks ...
+const failures = results.filter((r) => r.startsWith("FAIL"));
+console.log(`\n${results.length - failures.length}/${results.length} tests passed`);
+```
+
+This keeps the test running through failures so you see all results,
+unlike `assert` which aborts on the first failure.
+
 ### 2. Run the test

 ```bash
-./tools/test-js-with-puppeteer _clause_feature_x_test
+./tools/test-js-with-puppeteer _claude_<feature>_test
 ```

-This starts a fresh test server on port 9981, runs the script, and
-saves screenshots to `var/puppeteer/`.
+The runner matches test file names by prefix, so you don't need the
+full filename or `.test.ts` suffix. This starts a fresh test server
+on port 9981, runs the script, and saves screenshots to
+`var/puppeteer/`. The test database is reset between test files.
+
+On **aarch64 (ARM) hosts**, you must set `PUPPETEER_EXECUTABLE_PATH`
+(see "Environment details" below):
+
+```bash
+PUPPETEER_EXECUTABLE_PATH=$(echo ~/.cache/ms-playwright/chromium-*/chrome-linux/chrome) \
+    ./tools/test-js-with-puppeteer _claude_<feature>_test
+```
+
+To run all existing Puppeteer tests, omit the test name argument.
+
+**Timeout:** Tests can take 1–3 minutes each. Use a 300000ms timeout
+for the Bash tool.

 ### 3. Read the screenshots

@@ -70,41 +286,62 @@ script), then re-run from step 2.

 ### 6. Clean up

-Once you've gotten a solid test, leave it as an untracked file, so
-that you can use it when rebasing or iterating on the pull request.
+Leave test files as untracked `_claude_*` files so you can reuse them
+when rebasing or iterating on the pull request. The `_claude_` prefix
+is a convention to distinguish these from Zulip's committed test
+files. Do not commit them.
+
+## Environment details
+
+- **Architecture:** On x86_64, Puppeteer's bundled Chrome works. On
+  **aarch64**, it does NOT (fails with rosetta/ld-linux errors). Use
+  `uname -m` to check. For aarch64, install Playwright's Chromium
+  and point `PUPPETEER_EXECUTABLE_PATH` at it (shown in step 2).
+- **If the Playwright Chromium is missing**, install it:
+  ```bash
+  npx --yes playwright install chromium
+  ```
+- **Headless mode:** Tests run headless (`headless: true` in
+  `common.ts`). There is no display server.

 ## Test infrastructure facts

 - **Server URL:** `http://zulip.zulipdev.com:9981/`
 - **Login:** `common.log_in(page)` uses credentials from
-  `var/puppeteer/test_credentials.json` (auto-generated). Default
-  user is Desdemona (realm admin).
+  `var/puppeteer/test_credentials.json` (auto-generated by the test
+  harness). Default user is Desdemona (realm owner).
 - **Known users:** `common.fullname.cordelia`, `.othello`, `.hamlet`
 - **Screenshots:** saved to `var/puppeteer/<name>.png`
 - **Window size:** 1400 x 1024
-- **Test data:** The test database includes a non-system user group
-  `hamletcharacters` (members: Cordelia, Hamlet).
+- **Test data:** The test database includes channels like "Verona",
+  "Denmark", "Scotland" with topics and messages. Non-system user
+  group `hamletcharacters` (members: Cordelia, Hamlet).
 - **`zulip_test` global:** Only a limited set of internal functions
   are exposed — see `web/src/zulip_test.ts`. Functions like
   `get_stream_id` and `get_user_id_from_name` are available, but
   `user_groups` is not. Navigate to groups via URL hash routes
   or by clicking list items instead.
+- **Database reset:** The test runner calls
+  `reset_zulip_test_database()` and `POST /flush_caches` between
+  test files, so each test file starts with a clean state.
+- **`common.run_test()`** handles browser lifecycle, console log
+  forwarding with source-map resolution, automatic failure
+  screenshots, and logout at the end.

 ## Available helpers (from `web/e2e-tests/lib/common.ts`)

-| Helper                                        | Purpose                                                                              |
-| --------------------------------------------- | ------------------------------------------------------------------------------------ |
-| `common.log_in(page)`                         | Log in as the default user (Iago)                                                    |
-| `common.screenshot(page, "name")`             | Save `var/puppeteer/name.png`                                                        |
-| `common.clear_and_type(page, selector, text)` | Clear input and type                                                                 |
-| `common.wait_for_micromodal_to_open(page)`    | Wait for modal open animation                                                        |
-| `common.wait_for_micromodal_to_close(page)`   | Wait for modal close animation                                                       |
-| `common.get_stream_id(page, name)`            | Get a stream's ID                                                                    |
-| `common.get_user_id_from_name(page, name)`    | Get a user's ID                                                                      |
-| `common.open_personal_menu(page)`             | Open the personal menu                                                               |
-| `common.manage_organization(page)`            | Navigate to org settings                                                             |
-| `page.waitForSelector(sel, {visible: true})`  | Wait for element                                                                     |
-| `page.click(selector)`                        | Click an element                                                                     |
-| `page.goto(url)`                              | Navigate (e.g., hash routes like `http://zulip.zulipdev.com:9981/#groups/1/general`) |
-| `page.evaluate(() => ...)`                    | Run JS in browser context                                                            |
-| `page.keyboard.press("Escape")`               | Dismiss popovers/modals                                                              |
+| Helper                                        | Purpose                                  |
+| --------------------------------------------- | ---------------------------------------- |
+| `common.log_in(page)`                         | Log in as the default user (Desdemona)   |
+| `common.screenshot(page, "name")`             | Save `var/puppeteer/name.png`            |
+| `common.clear_and_type(page, selector, text)` | Clear input and type                     |
+| `common.fill_form(page, selector, params)`    | Fill multiple form fields at once        |
+| `common.wait_for_micromodal_to_open(page)`    | Wait for modal open animation            |
+| `common.wait_for_micromodal_to_close(page)`   | Wait for modal close animation           |
+| `common.get_stream_id(page, name)`            | Get a stream's ID                        |
+| `common.get_user_id_from_name(page, name)`    | Get a user's ID                          |
+| `common.open_personal_menu(page)`             | Open the personal menu                   |
+| `common.manage_organization(page)`            | Navigate to org settings                 |
+| `common.send_message(page, type, params)`     | Send a stream or DM message              |
+| `common.send_multiple_messages(page, msgs)`   | Send several messages in sequence        |
+| `common.select_item_via_typeahead(page, ...)` | Type into a field and select a typeahead |
diff --git a/web/src/compose_actions.ts b/web/src/compose_actions.ts
index 1204eaa4fb921..ed8be01c5e557 100644
--- a/web/src/compose_actions.ts
+++ b/web/src/compose_actions.ts
@@ -529,6 +529,7 @@ export let cancel = (): void => {
     compose_banner.clear_message_sent_banners();
     compose_banner.clear_non_interleaved_view_messages_fading_banner();
     compose_banner.clear_interleaved_view_messages_fading_banner();
+    compose_tooltips.dismiss_intro_go_to_conversation_tooltip();
     call_hooks(compose_cancel_hooks);
     compose_state.set_message_type(undefined);
     compose_pm_pill.clear();
diff --git a/web/src/compose_recipient.ts b/web/src/compose_recipient.ts
index 6d0f3ef736129..3ea6ec3ab2c9f 100644
--- a/web/src/compose_recipient.ts
+++ b/web/src/compose_recipient.ts
@@ -11,6 +11,7 @@ import * as compose_banner from "./compose_banner.ts";
 import * as compose_fade from "./compose_fade.ts";
 import * as compose_pm_pill from "./compose_pm_pill.ts";
 import * as compose_state from "./compose_state.ts";
+import * as compose_tooltips from "./compose_tooltips.ts";
 import * as compose_ui from "./compose_ui.ts";
 import type {ComposeTriggeredOptions} from "./compose_ui.ts";
 import * as compose_validate from "./compose_validate.ts";
@@ -19,9 +20,12 @@ import * as dropdown_widget from "./dropdown_widget.ts";
 import type {DropdownWidget, Option} from "./dropdown_widget.ts";
 import {$t} from "./i18n.ts";
 import * as narrow_state from "./narrow_state.ts";
+import * as onboarding_steps from "./onboarding_steps.ts";
+import * as pm_conversations from "./pm_conversations.ts";
 import {realm} from "./state_data.ts";
 import * as stream_color from "./stream_color.ts";
 import * as stream_data from "./stream_data.ts";
+import * as stream_topic_history from "./stream_topic_history.ts";
 import type {StreamSubscription} from "./sub_store.ts";
 import * as typeahead_helper from "./typeahead_helper.ts";
 import * as ui_util from "./ui_util.ts";
@@ -108,6 +112,8 @@ export function set_high_attention_recipient_row(): void {

 export let update_narrow_to_recipient_visibility = (): void => {
     const message_type = compose_state.get_message_type();
+    const display_intro_go_to_conversation_tooltip =
+        onboarding_steps.ONE_TIME_NOTICES_TO_DISPLAY.has("intro_go_to_conversation_tooltip");
     if (message_type === "stream") {
         const stream_exists = Boolean(compose_state.stream_id());

@@ -117,6 +123,14 @@ export let update_narrow_to_recipient_visibility = (): void => {
             compose_state.has_full_recipient()
         ) {
             $(".conversation-arrow").toggleClass("narrow_to_compose_recipients", true);
+            const stream_id = compose_state.stream_id()!;
+            const topic_name = compose_state.topic();
+            if (
+                display_intro_go_to_conversation_tooltip &&
+                stream_topic_history.get_recent_topic_names(stream_id).includes(topic_name)
+            ) {
+                compose_tooltips.maybe_show_intro_go_to_conversation_tooltip();
+            }
             return;
         }
     } else if (message_type === "private") {
@@ -127,9 +141,16 @@ export let update_narrow_to_recipient_visibility = (): void => {
             compose_state.has_full_recipient()
         ) {
             $(".conversation-arrow").toggleClass("narrow_to_compose_recipients", true);
+            if (
+                display_intro_go_to_conversation_tooltip &&
+                pm_conversations.recent.has_conversation(recipients.join(","))
+            ) {
+                compose_tooltips.maybe_show_intro_go_to_conversation_tooltip();
+            }
             return;
         }
     }
+    compose_tooltips.dismiss_intro_go_to_conversation_tooltip();
     $(".conversation-arrow").toggleClass("narrow_to_compose_recipients", false);
 };

diff --git a/web/src/compose_setup.ts b/web/src/compose_setup.ts
index e7eaad35f18cd..c4dbe8d156819 100644
--- a/web/src/compose_setup.ts
+++ b/web/src/compose_setup.ts
@@ -16,6 +16,7 @@ import * as compose_notifications from "./compose_notifications.ts";
 import * as compose_recipient from "./compose_recipient.ts";
 import * as compose_send_menu_popover from "./compose_send_menu_popover.ts";
 import * as compose_state from "./compose_state.ts";
+import * as compose_tooltips from "./compose_tooltips.ts";
 import * as compose_ui from "./compose_ui.ts";
 import * as compose_validate from "./compose_validate.ts";
 import * as composebox_typeahead from "./composebox_typeahead.ts";
@@ -600,6 +601,7 @@ export function initialize(): void {

     $("#compose").on("click", ".narrow_to_compose_recipients", (e) => {
         e.preventDefault();
+        compose_tooltips.dismiss_intro_go_to_conversation_tooltip();
         message_view.to_compose_target();
     });

diff --git a/web/src/compose_tooltips.ts b/web/src/compose_tooltips.ts
index 1fb8f6b331fe1..690fb5131b0d9 100644
--- a/web/src/compose_tooltips.ts
+++ b/web/src/compose_tooltips.ts
@@ -4,6 +4,7 @@ import assert from "minimalistic-assert";
 import * as tippy from "tippy.js";

 import render_drafts_tooltip from "../templates/drafts_tooltip.hbs";
+import render_intro_go_to_conversation_tooltip from "../templates/intro_go_to_conversation_tooltip.hbs";
 import render_narrow_to_compose_recipients_tooltip from "../templates/narrow_to_compose_recipients_tooltip.hbs";

 import * as blueslip from "./blueslip.ts";
@@ -12,6 +13,7 @@ import * as compose_validate from "./compose_validate.ts";
 import {$t} from "./i18n.ts";
 import {pick_empty_narrow_banner} from "./narrow_banner.ts";
 import * as narrow_state from "./narrow_state.ts";
+import * as onboarding_steps from "./onboarding_steps.ts";
 import * as popover_menus from "./popover_menus.ts";
 import {realm} from "./state_data.ts";
 import * as stream_data from "./stream_data.ts";
@@ -94,6 +96,44 @@ export function initialize_compose_tooltips(context: SingletonContext, selector:
     });
 }

+let intro_go_to_conversation_tooltip_instance: tippy.Instance | null = null;
+
+export function maybe_show_intro_go_to_conversation_tooltip(): void {
+    const $button = $(".conversation-arrow");
+    if (!$button.hasClass("narrow_to_compose_recipients")) {
+        return;
+    }
+
+    if ($("#compose_banners .main-view-banner").length > 0) {
+        return;
+    }
+
+    if (intro_go_to_conversation_tooltip_instance !== null) {
+        return;
+    }
+
+    intro_go_to_conversation_tooltip_instance = tippy.default($button[0]!, {
+        content: parse_html(render_intro_go_to_conversation_tooltip()),
+        placement: "top",
+        trigger: "manual",
+        showOnCreate: true,
+        hideOnClick: false,
+        appendTo: () => document.body,
+        onHidden(inst) {
+            inst.destroy();
+            intro_go_to_conversation_tooltip_instance = null;
+        },
+    });
+
+    onboarding_steps.post_onboarding_step_as_read("intro_go_to_conversation_tooltip");
+}
+
+export function dismiss_intro_go_to_conversation_tooltip(): void {
+    if (intro_go_to_conversation_tooltip_instance !== null) {
+        intro_go_to_conversation_tooltip_instance.hide();
+    }
+}
+
 export function initialize(): void {
     tippy.delegate("body", {
         target: [
@@ -309,6 +349,13 @@ export function initialize(): void {
         target: ".narrow_to_compose_recipients",
         delay: LONG_HOVER_DELAY,
         appendTo: () => document.body,
+        onShow() {
+            // Suppress the hover tooltip while the intro tooltip is showing.
+            if (intro_go_to_conversation_tooltip_instance !== null) {
+                return false;
+            }
+            return undefined;
+        },
         content() {
             const narrow_filter = narrow_state.filter();
             let display_current_view;
diff --git a/web/src/hotkey.ts b/web/src/hotkey.ts
index 4fdc359fb5e7f..061d437095e6c 100644
--- a/web/src/hotkey.ts
+++ b/web/src/hotkey.ts
@@ -15,6 +15,7 @@ import * as compose_reply from "./compose_reply.ts";
 import * as compose_send_menu_popover from "./compose_send_menu_popover.ts";
 import * as compose_state from "./compose_state.ts";
 import * as compose_textarea from "./compose_textarea.ts";
+import * as compose_tooltips from "./compose_tooltips.ts";
 import * as condense from "./condense.ts";
 import {show_copied_confirmation} from "./copied_tooltip.ts";
 import * as deprecated_feature_notice from "./deprecated_feature_notice.ts";
@@ -1053,6 +1054,7 @@ function process_hotkey(e: JQuery.KeyDownEvent, hotkey: Hotkey): boolean {
     }

     if (event_name === "narrow_to_compose_target") {
+        compose_tooltips.dismiss_intro_go_to_conversation_tooltip();
         message_view.to_compose_target();
         return true;
     }
diff --git a/web/src/onboarding_steps.ts b/web/src/onboarding_steps.ts
index a0163dec086cb..19ff50d7563bc 100644
--- a/web/src/onboarding_steps.ts
+++ b/web/src/onboarding_steps.ts
@@ -6,7 +6,6 @@ import render_navigation_tour_video_modal from "../templates/navigation_tour_vid

 import * as browser_history from "./browser_history.ts";
 import * as channel from "./channel.ts";
-import * as compose_recipient from "./compose_recipient.ts";
 import * as dialog_widget from "./dialog_widget.ts";
 import {$t, $t_html} from "./i18n.ts";
 import type * as message_view from "./message_view.ts";
@@ -104,7 +103,10 @@ function narrow_to_dm_with_welcome_bot_new_user(
     }
 }

-function show_navigation_tour_video(navigation_tour_video_url: string | null): void {
+function show_navigation_tour_video(
+    navigation_tour_video_url: string | null,
+    update_recipient_row_attention_level: () => void,
+): void {
     if (ONE_TIME_NOTICES_TO_DISPLAY.has("navigation_tour_video")) {
         assert(navigation_tour_video_url !== null);
         const modal_content_html = render_navigation_tour_video_modal({
@@ -193,7 +195,7 @@ function show_navigation_tour_video(navigation_tour_video_url: string | null): v
                 //
                 // We explicitly set the focus to #compose-textarea to avoid flaky nature.
                 $("textarea#compose-textarea").trigger("focus");
-                compose_recipient.update_recipient_row_attention_level();
+                update_recipient_row_attention_level();

                 if (!watch_later_clicked) {
                     // $watch_later_button click handler already calls this function.
@@ -206,9 +208,19 @@ function show_navigation_tour_video(navigation_tour_video_url: string | null): v

 export function initialize(
     params: StateData["onboarding_steps"],
-    {show_message_view}: {show_message_view: typeof message_view.show},
+    {
+        show_message_view,
+        update_recipient_row_attention_level,
+    }: {
+        show_message_view: typeof message_view.show;
+        update_recipient_row_attention_level: () => void;
+    },
 ): void {
     update_onboarding_steps_to_display(params.onboarding_steps);
+
     narrow_to_dm_with_welcome_bot_new_user(params.onboarding_steps, show_message_view);
-    show_navigation_tour_video(params.navigation_tour_video_url);
+    show_navigation_tour_video(
+        params.navigation_tour_video_url,
+        update_recipient_row_attention_level,
+    );
 }
diff --git a/web/src/ui_init.js b/web/src/ui_init.js
index 9da0359e68350..bcf6758202650 100644
--- a/web/src/ui_init.js
+++ b/web/src/ui_init.js
@@ -764,6 +764,8 @@ export async function initialize_everything(state_data) {
     // is defined. Also, must happen after people.initialize()
     onboarding_steps.initialize(state_data.onboarding_steps, {
         show_message_view: message_view.show,
+        update_recipient_row_attention_level:
+            compose_recipient.update_recipient_row_attention_level,
     });
     typing.initialize();
     starred_messages_ui.initialize();
diff --git a/web/templates/intro_go_to_conversation_tooltip.hbs b/web/templates/intro_go_to_conversation_tooltip.hbs
new file mode 100644
index 0000000000000..52f2d50a9c346
--- /dev/null
+++ b/web/templates/intro_go_to_conversation_tooltip.hbs
@@ -0,0 +1,2 @@
+<div>{{t "Click here to go to the conversation you're composing to."}}</div>
+{{tooltip_hotkey_hints "Ctrl" "."}}
diff --git a/web/tests/compose.test.cjs b/web/tests/compose.test.cjs
index 599aecb95dd31..d216807a61c1b 100644
--- a/web/tests/compose.test.cjs
+++ b/web/tests/compose.test.cjs
@@ -49,7 +49,9 @@ const sent_messages = mock_esm("../src/sent_messages");
 const server_events_state = mock_esm("../src/server_events_state");
 const transmit = mock_esm("../src/transmit");
 const upload = mock_esm("../src/upload");
-const onboarding_steps = mock_esm("../src/onboarding_steps");
+const onboarding_steps = mock_esm("../src/onboarding_steps", {
+    ONE_TIME_NOTICES_TO_DISPLAY: new Set(),
+});
 mock_esm("../src/settings_data", {
     user_has_permission_for_group_setting: () => true,
 });
diff --git a/web/tests/compose_actions.test.cjs b/web/tests/compose_actions.test.cjs
index ec1a697a4a1e2..20c55765cec9f 100644
--- a/web/tests/compose_actions.test.cjs
+++ b/web/tests/compose_actions.test.cjs
@@ -51,7 +51,10 @@ set_global("requestAnimationFrame", (func) => func());
 const autosize = noop;
 autosize.update = noop;
 mock_esm("autosize", {default: autosize});
-mock_esm("../src/compose_tooltips", {initialize_compose_tooltips: noop});
+mock_esm("../src/compose_tooltips", {
+    initialize_compose_tooltips: noop,
+    dismiss_intro_go_to_conversation_tooltip: noop,
+});

 const channel = mock_esm("../src/channel");
 const compose_fade = mock_esm("../src/compose_fade", {
diff --git a/web/tests/dispatch.test.cjs b/web/tests/dispatch.test.cjs
index 440795ee45727..247b591f12903 100644
--- a/web/tests/dispatch.test.cjs
+++ b/web/tests/dispatch.test.cjs
@@ -424,7 +424,10 @@ run_test("default_streams", ({override}) => {
 });

 run_test("onboarding_steps", () => {
-    onboarding_steps.initialize({onboarding_steps: []}, () => {});
+    onboarding_steps.initialize(
+        {onboarding_steps: []},
+        {show_message_view() {}, update_recipient_row_attention_level() {}},
+    );
     const event = event_fixtures.onboarding_steps;
     const one_time_notices = new Set();
     for (const onboarding_step of event.onboarding_steps) {
diff --git a/zerver/lib/onboarding_steps.py b/zerver/lib/onboarding_steps.py
index c5ce00527a3ce..152053c0d205e 100644
--- a/zerver/lib/onboarding_steps.py
+++ b/zerver/lib/onboarding_steps.py
@@ -58,6 +58,9 @@ def to_dict(self) -> dict[str, str]:
     OneTimeNotice(
         name="navigation_tour_video",
     ),
+    OneTimeNotice(
+        name="intro_go_to_conversation_tooltip",
+    ),
 ]

 ONE_TIME_ACTIONS = [OneTimeAction(name="narrow_to_dm_with_welcome_bot_new_user")]
diff --git a/zerver/tests/test_onboarding_steps.py b/zerver/tests/test_onboarding_steps.py
index a86153439eec4..6b709a1975507 100644
--- a/zerver/tests/test_onboarding_steps.py
+++ b/zerver/tests/test_onboarding_steps.py
@@ -31,7 +31,7 @@ def test_some_done_some_not(self) -> None:

         do_mark_onboarding_step_as_read(self.user, "intro_inbox_view_modal")
         onboarding_steps = get_next_onboarding_steps(self.user)
-        self.assert_length(onboarding_steps, 8)
+        self.assert_length(onboarding_steps, 9)
         self.assertEqual(onboarding_steps[0]["name"], "intro_recent_view_modal")
         self.assertEqual(onboarding_steps[1]["name"], "first_stream_created_banner")
         self.assertEqual(onboarding_steps[2]["name"], "jump_to_conversation_banner")
@@ -39,7 +39,8 @@ def test_some_done_some_not(self) -> None:
         self.assertEqual(onboarding_steps[4]["name"], "interleaved_view_messages_fading")
         self.assertEqual(onboarding_steps[5]["name"], "intro_resolve_topic")
         self.assertEqual(onboarding_steps[6]["name"], "navigation_tour_video")
-        self.assertEqual(onboarding_steps[7]["name"], "narrow_to_dm_with_welcome_bot_new_user")
+        self.assertEqual(onboarding_steps[7]["name"], "intro_go_to_conversation_tooltip")
+        self.assertEqual(onboarding_steps[8]["name"], "narrow_to_dm_with_welcome_bot_new_user")

         with self.settings(TUTORIAL_ENABLED=False):
             onboarding_steps = get_next_onboarding_steps(self.user)

PATCH

echo "Patch applied successfully."
