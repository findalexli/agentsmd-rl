#!/usr/bin/env bash
set -euo pipefail

cd /workspace/browser-harness

# Idempotency guard
if grep -qF "**If you learned anything non-obvious about how a site works, open a PR to `doma" "SKILL.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/SKILL.md b/SKILL.md
@@ -87,11 +87,36 @@ rg --files domain-skills
 rg -n "tiktok|upload" domain-skills
 ```
 
-## Post-task ritual (self-improving harness)
+## Always contribute back
 
-If needed, modify your own helper functions to fix tools that do not work well on a task, make repeated actions more efficient, or fix recurring browser-interaction problems.
+**If you learned anything non-obvious about how a site works, open a PR to `domain-skills/<site>/` before you finish. Default to contributing.** The harness gets better only because agents file what they learn. If figuring something out cost you a few steps, the next run should not pay the same tax.
 
-If you spend a couple of corrective steps learning things you would want to know on the next similar task for the same domain, add or update a Markdown skill under `domain-skills/<domain>/` (create the directory if needed) with all reusable learnings that would speed up the next run, such as where to wait for network requests, which interaction patterns worked, and what traps matter. `domain-skills/` is shared across users, so include only sanitized, reusable guidance and never include sensitive data, secrets, or user-specific details. Then open a PR to this public repo.
+Examples of what's worth a PR:
+
+- A **private API** the page calls (XHR/fetch endpoint, request shape, auth) — often 10× faster than DOM scraping.
+- A **stable selector** that beats the obvious one, or an obfuscated CSS-module class to avoid.
+- A **framework quirk** — "the dropdown is a React combobox that only commits on Escape", "this Vue list only renders rows inside its own scroll container, so `scrollIntoView` on the row doesn't work — you have to scroll the container".
+- A **URL pattern** — direct route, required query params (`?lang=en`, `?th=1`), a variant that skips a loader.
+- A **wait** that `wait_for_load()` misses, with the reason.
+- A **trap** — stale drafts, legacy IDs that now return null, unicode quirks, beforeunload dialogs, CAPTCHA surfaces.
+
+### What a domain skill should capture
+
+The *durable* shape of the site — the map, not the diary. Focus on what the next agent on this site needs to know before it starts:
+
+- URL patterns and query params.
+- Private APIs and their payload shape.
+- Stable selectors (`data-*`, `aria-*`, `role`, semantic classes).
+- Site structure — containers, items per page, framework, where state lives.
+- Framework/interaction quirks unique to this site.
+- Waits and the reasons they're needed.
+- Traps and the selectors that *don't* work.
+
+### Do not write
+
+- **Raw pixel coordinates.** They break on viewport, zoom, and layout changes. Describe how to *locate* the target (selector, `scrollIntoView`, `aria-label`, visible text) — never where it happened to be on your screen.
+- **Run narration** or step-by-step of the specific task you just did.
+- **Secrets, cookies, session tokens, user-specific state.** `domain-skills/` is shared and public.
 
 ## What actually works
 
PATCH

echo "Gold patch applied."
