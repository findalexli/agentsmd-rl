#!/usr/bin/env bash
set -euo pipefail

cd /workspace/browser-harness

# Idempotency guard
if grep -qF "- Clicking: `screenshot()` \u2192 read the pixel off the image \u2192 `click(x, y)` \u2192 `scr" "SKILL.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/SKILL.md b/SKILL.md
@@ -5,7 +5,7 @@ description: Direct browser control via CDP. Use when the user wants to automate
 
 # browser-harness
 
-Easiest and most powerful way to interact with the browser. **Read this file in full before using or editing the harness** — it has to be in context.
+Easiest and most powerful way to interact with the browser. Read this file in full before using or editing the harness — it has to be in context.
 
 ## Fast start
 
@@ -15,7 +15,7 @@ Read `helpers.py` first. For first-time install or reconnect/bootstrap, read `in
 
 - `browser-harness --doctor` — diagnose install, daemon, browser, and whether an update is available.
 - `browser-harness --setup` — re-run the interactive browser-attach flow (equivalent to the bootstrap in `install.md`).
-- `browser-harness --update -y` — pull the latest version and restart the daemon without prompting. **If you see a banner like `[browser-harness] update available: X -> Y` at the top of a run, run this yourself — don't ask the user first.** The banner is rate-limited to once per day.
+- `browser-harness --update -y` — pull the latest version and restart the daemon without prompting. If you see a banner like `[browser-harness] update available: X -> Y` at the top of a run, run this yourself — don't ask the user first. The banner is rate-limited to once per day.
 
 ```bash
 browser-harness <<'PY'
@@ -48,7 +48,7 @@ PY
 
 ### Remote browsers
 
-Use remote for **parallel sub-agents** (each gets its own isolated browser via a distinct `BU_NAME`) or on a headless server. `BROWSER_USE_API_KEY` must be set. `start_remote_daemon`, `list_cloud_profiles`, `list_local_profiles`, `sync_local_profile` are pre-imported.
+Use remote for parallel sub-agents (each gets its own isolated browser via a distinct `BU_NAME`) or on a headless server. `BROWSER_USE_API_KEY` must be set. `start_remote_daemon`, `list_cloud_profiles`, `list_local_profiles`, `sync_local_profile` are pre-imported.
 
 ```bash
 browser-harness <<'PY'
@@ -100,16 +100,16 @@ rg -n "tiktok|upload" domain-skills
 
 ## Always contribute back
 
-**If you learned anything non-obvious about how a site works, open a PR to `domain-skills/<site>/` before you finish. Default to contributing.** The harness gets better only because agents file what they learn. If figuring something out cost you a few steps, the next run should not pay the same tax.
+If you learned anything non-obvious about how a site works, open a PR to `domain-skills/<site>/` before you finish. Default to contributing. The harness gets better only because agents file what they learn. If figuring something out cost you a few steps, the next run should not pay the same tax.
 
 Examples of what's worth a PR:
 
-- A **private API** the page calls (XHR/fetch endpoint, request shape, auth) — often 10× faster than DOM scraping.
-- A **stable selector** that beats the obvious one, or an obfuscated CSS-module class to avoid.
-- A **framework quirk** — "the dropdown is a React combobox that only commits on Escape", "this Vue list only renders rows inside its own scroll container, so `scrollIntoView` on the row doesn't work — you have to scroll the container".
-- A **URL pattern** — direct route, required query params (`?lang=en`, `?th=1`), a variant that skips a loader.
-- A **wait** that `wait_for_load()` misses, with the reason.
-- A **trap** — stale drafts, legacy IDs that now return null, unicode quirks, beforeunload dialogs, CAPTCHA surfaces.
+- A private API the page calls (XHR/fetch endpoint, request shape, auth) — often 10× faster than DOM scraping.
+- A stable selector that beats the obvious one, or an obfuscated CSS-module class to avoid.
+- A framework quirk — "the dropdown is a React combobox that only commits on Escape", "this Vue list only renders rows inside its own scroll container, so `scrollIntoView` on the row doesn't work — you have to scroll the container".
+- A URL pattern — direct route, required query params (`?lang=en`, `?th=1`), a variant that skips a loader.
+- A wait that `wait_for_load()` misses, with the reason.
+- A trap — stale drafts, legacy IDs that now return null, unicode quirks, beforeunload dialogs, CAPTCHA surfaces.
 
 ### What a domain skill should capture
 
@@ -125,31 +125,31 @@ The *durable* shape of the site — the map, not the diary. Focus on what the ne
 
 ### Do not write
 
-- **Raw pixel coordinates.** They break on viewport, zoom, and layout changes. Describe how to *locate* the target (selector, `scrollIntoView`, `aria-label`, visible text) — never where it happened to be on your screen.
-- **Run narration** or step-by-step of the specific task you just did.
-- **Secrets, cookies, session tokens, user-specific state.** `domain-skills/` is shared and public.
+- Raw pixel coordinates. They break on viewport, zoom, and layout changes. Describe how to *locate* the target (selector, `scrollIntoView`, `aria-label`, visible text) — never where it happened to be on your screen.
+- Run narration or step-by-step of the specific task you just did.
+- Secrets, cookies, session tokens, user-specific state. `domain-skills/` is shared and public.
 
 ## What actually works
 
-- **Screenshots first**: use `screenshot()` to understand the current page quickly, find visible targets, and decide whether you need a click, a selector, or more navigation.
-- **Clicking**: `screenshot()` → read the pixel off the image → `click(x, y)` → `screenshot()` to verify. Suppress the Playwright-habit reflex of "locate first, then click" — no `getBoundingClientRect`, no selector hunt. Drop to DOM only when the target has no visible geometry (hidden input, 0×0 node). Hit-testing happens in Chrome's browser process, so clicks go through iframes / shadow DOM / cross-origin without extra work.
-- **Bulk HTTP**: `http_get(url)` + `ThreadPoolExecutor`. No browser for static pages (249 Netflix pages in 2.8s).
-- **After goto**: `wait_for_load()`.
-- **Wrong/stale tab**: `ensure_real_tab()`. Use it when the current tab is stale or internal; the daemon also auto-recovers from stale sessions on the next call.
-- **Verification**: `print(page_info())` is the simplest "is this alive?" check, but screenshots are the default way to verify whether a visible action actually worked.
-- **DOM reads**: use `js(...)` for inspection and extraction when the screenshot shows that coordinates are the wrong tool.
-- **Iframe sites** (Azure blades, Salesforce): `click(x, y)` passes through; only drop to iframe DOM work when coordinate clicks are the wrong tool.
-- **Auth wall**: redirected to login → stop and ask the user. Don't type credentials from screenshots.
-- **Raw CDP** for anything helpers don't cover: `cdp("Domain.method", **params)`.
+- Screenshots first: use `screenshot()` to understand the current page quickly, find visible targets, and decide whether you need a click, a selector, or more navigation.
+- Clicking: `screenshot()` → read the pixel off the image → `click(x, y)` → `screenshot()` to verify. Suppress the Playwright-habit reflex of "locate first, then click" — no `getBoundingClientRect`, no selector hunt. Drop to DOM only when the target has no visible geometry (hidden input, 0×0 node). Hit-testing happens in Chrome's browser process, so clicks go through iframes / shadow DOM / cross-origin without extra work.
+- Bulk HTTP: `http_get(url)` + `ThreadPoolExecutor`. No browser for static pages (249 Netflix pages in 2.8s).
+- After goto: `wait_for_load()`.
+- Wrong/stale tab: `ensure_real_tab()`. Use it when the current tab is stale or internal; the daemon also auto-recovers from stale sessions on the next call.
+- Verification: `print(page_info())` is the simplest "is this alive?" check, but screenshots are the default way to verify whether a visible action actually worked.
+- DOM reads: use `js(...)` for inspection and extraction when the screenshot shows that coordinates are the wrong tool.
+- Iframe sites (Azure blades, Salesforce): `click(x, y)` passes through; only drop to iframe DOM work when coordinate clicks are the wrong tool.
+- Auth wall: redirected to login → stop and ask the user. Don't type credentials from screenshots.
+- Raw CDP for anything helpers don't cover: `cdp("Domain.method", params)`.
 
 ## Design constraints
 
-- **Coordinate clicks default.** `Input.dispatchMouseEvent` goes through iframes/shadow/cross-origin at the compositor level.
-- **Connect to the user's running Chrome.** Don't launch your own browser.
-- **`cdp-use` is only for `CDPClient.send_raw`.** Prefer raw CDP strings over typed wrappers.
-- **`run.py` stays tiny.** No argparse, subcommands, or extra control layer.
-- **Helpers stay short.** Browser primitives in `helpers.py`; daemon/bootstrap and remote session admin live in `admin.py`.
-- **Don't add a manager layer.** No retries framework, session manager, daemon supervisor, config system, or logging framework.
+- Coordinate clicks default. `Input.dispatchMouseEvent` goes through iframes/shadow/cross-origin at the compositor level.
+- Connect to the user's running Chrome. Don't launch your own browser.
+- `cdp-use` is only for `CDPClient.send_raw`. Prefer raw CDP strings over typed wrappers.
+- `run.py` stays tiny. No argparse, subcommands, or extra control layer.
+- Helpers stay short. Browser primitives in `helpers.py`; daemon/bootstrap and remote session admin live in `admin.py`.
+- Don't add a manager layer. No retries framework, session manager, daemon supervisor, config system, or logging framework.
 
 ## Architecture
 
@@ -166,30 +166,30 @@ Chrome / Browser Use cloud -> CDP WS -> daemon.py -> /tmp/bu-<NAME>.sock -> run.
 
 ## Gotchas (field-tested)
 
-- **Chrome 144+ `chrome://inspect/#remote-debugging` does NOT serve `/json/version`.** Read `DevToolsActivePort` instead.
-- **Try attaching before asking for setup.** If `uv run browser-harness` already works, skip the remote-debugging instructions entirely. Decide what to escalate from the harness's error message, not from whether Chrome is visibly running.
-- **The remote-debugging checkbox is per-profile sticky in Chrome.** Once ticked on a profile, every future Chrome launch auto-enables CDP — only navigate to `chrome://inspect/#remote-debugging` when `DevToolsActivePort` is genuinely missing on a fresh profile.
-- **The first connect may block on Chrome's Allow dialog.** If setup hangs, explicitly tell the user to click `Allow` in Chrome if it appears, then keep polling for up to 30 seconds instead of treating follow-on errors as a new failure.
-- **`DevToolsActivePort` can exist before the port is actually listening.** Treat connection refused as "still enabling" and keep polling for up to 30 seconds.
-- **Chrome may open the profile picker before any real tab exists.** If Chrome opens both a profile picker and the remote-debugging page, tell the user to choose their normal profile first, then tick the checkbox and click `Allow` if shown.
-- **On macOS, if Chrome is already running, prefer AppleScript `open location` over `open -a ... URL`.** It reuses the current profile and avoids creating an extra startup path through the profile picker.
-- **Omnibox popups are fake `page` targets.** Filter `chrome://omnibox-popup...` and other internals when you need a real tab.
-- **CDP target order != Chrome's visible tab-strip order.** Use UI automation when the user means "the first/second tab I can see"; `Target.activateTarget` only shows a known target.
-- **Default daemon sessions can go stale.** `ensure_real_tab()` re-attaches to a real page.
-- **`no close frame received or sent` usually means a stale daemon / websocket.** Restart the daemon once with:
+- Chrome 144+ `chrome://inspect/#remote-debugging` does NOT serve `/json/version`. Read `DevToolsActivePort` instead.
+- Try attaching before asking for setup. If `uv run browser-harness` already works, skip the remote-debugging instructions entirely. Decide what to escalate from the harness's error message, not from whether Chrome is visibly running.
+- The remote-debugging checkbox is per-profile sticky in Chrome. Once ticked on a profile, every future Chrome launch auto-enables CDP — only navigate to `chrome://inspect/#remote-debugging` when `DevToolsActivePort` is genuinely missing on a fresh profile.
+- The first connect may block on Chrome's Allow dialog. If setup hangs, explicitly tell the user to click `Allow` in Chrome if it appears, then keep polling for up to 30 seconds instead of treating follow-on errors as a new failure.
+- `DevToolsActivePort` can exist before the port is actually listening. Treat connection refused as "still enabling" and keep polling for up to 30 seconds.
+- Chrome may open the profile picker before any real tab exists. If Chrome opens both a profile picker and the remote-debugging page, tell the user to choose their normal profile first, then tick the checkbox and click `Allow` if shown.
+- On macOS, if Chrome is already running, prefer AppleScript `open location` over `open -a ... URL`. It reuses the current profile and avoids creating an extra startup path through the profile picker.
+- Omnibox popups are fake `page` targets. Filter `chrome://omnibox-popup...` and other internals when you need a real tab.
+- CDP target order != Chrome's visible tab-strip order. Use UI automation when the user means "the first/second tab I can see"; `Target.activateTarget` only shows a known target.
+- Default daemon sessions can go stale. `ensure_real_tab()` re-attaches to a real page.
+- `no close frame received or sent` usually means a stale daemon / websocket. Restart the daemon once with:
   `uv run python - <<'PY'`
   `from admin import restart_daemon`
   `restart_daemon()`
   `PY`
   before assuming setup is wrong.
-- **If `restart_daemon()` also hangs**, kill Chrome entirely (`pkill -9 -f "Google Chrome"`), clean sockets (`rm -f /tmp/bu-default.sock /tmp/bu-default.pid`), reopen Chrome (`open -a "Google Chrome"`), wait 5s, then reconnect. This resets all CDP state.
-- **Browser Use API is camelCase on the wire.** `cdpUrl`, `proxyCountryCode`, etc.
-- **Remote `cdpUrl` is HTTPS, not ws.** Resolve the websocket URL via `/json/version`.
-- **Stop cloud browsers with `PATCH /browsers/{id}` + `{\"action\":\"stop\"}`.**
-- **After every meaningful action, re-screenshot before assuming it worked.** Use the image to verify changed state, open menus, navigation, visible errors, and whether the page is in the state you expected.
-- **Use screenshots to drive exploration.** They are often the fastest way to find the next click target, notice hidden blockers, and decide if a selector is even worth writing.
-- **Prefer compositor-level actions over framework hacks.** Try screenshots, coordinate clicks, and raw key input before adding DOM-specific workarounds.
-- **If you need framework-specific DOM tricks, check `interaction-skills/` first.** That is where dropdown, dialog, iframe, shadow DOM, and form-specific guidance belongs.
+- If `restart_daemon()` also hangs, kill Chrome entirely (`pkill -9 -f "Google Chrome"`), clean sockets (`rm -f /tmp/bu-default.sock /tmp/bu-default.pid`), reopen Chrome (`open -a "Google Chrome"`), wait 5s, then reconnect. This resets all CDP state.
+- Browser Use API is camelCase on the wire. `cdpUrl`, `proxyCountryCode`, etc.
+- Remote `cdpUrl` is HTTPS, not ws. Resolve the websocket URL via `/json/version`.
+- Stop cloud browsers with `PATCH /browsers/{id}` + `{\"action\":\"stop\"}`.
+- After every meaningful action, re-screenshot before assuming it worked. Use the image to verify changed state, open menus, navigation, visible errors, and whether the page is in the state you expected.
+- Use screenshots to drive exploration. They are often the fastest way to find the next click target, notice hidden blockers, and decide if a selector is even worth writing.
+- Prefer compositor-level actions over framework hacks. Try screenshots, coordinate clicks, and raw key input before adding DOM-specific workarounds.
+- If you need framework-specific DOM tricks, check `interaction-skills/` first. That is where dropdown, dialog, iframe, shadow DOM, and form-specific guidance belongs.
 
 ## Interaction notes
 
PATCH

echo "Gold patch applied."
