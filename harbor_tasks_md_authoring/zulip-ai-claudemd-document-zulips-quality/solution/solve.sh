#!/usr/bin/env bash
set -euo pipefail

cd /workspace/zulip

# Idempotency guard
if grep -qF "built to last for many years. It is developed by a vibrant open-source" ".claude/CLAUDE.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/.claude/CLAUDE.md b/.claude/CLAUDE.md
@@ -7,10 +7,64 @@ contributors.
 
 ## Philosophy
 
-Zulip's coding philosophy is to **focus relentlessly on making the codebase
-easy to understand and difficult to make dangerous mistakes**. This applies
-equally to AI-generated contributions. Every change should make the codebase
-more maintainable and easier to read.
+Zulip is a team chat application used by thousands of organizations,
+built to last for many years. It is developed by a vibrant open-source
+community, with maintainers who have consistently emphasized **high
+standards for codebase readability, code review, commit discipline,
+debuggability, automated testing, tooling, documentation, and all the
+other subtle details that together determine whether software is easy
+to understand, operate, and modify**.
+
+Zulip's engineering strategy is to **"move quickly without breaking
+things"**. This is possible because the project has invested years in
+testing, tooling, code structure, documentation, and development
+practices that catch bugs systematically rather than relying on
+individual vigilance. Maintainers spend most of their review time on
+product decisions and code structure/readability, not on chasing
+correctness issues — because the process is designed to prevent them.
+
+This means Zulip's coding philosophy is to **focus relentlessly on
+making the codebase easy to understand and difficult to make dangerous
+mistakes**. This applies equally to AI-generated contributions. Every
+change should make the codebase more maintainable and easier to read.
+
+### No detail is too small
+
+Zulip holds itself to a high bar for polish because users depend on
+this software daily, and because the project is built to last for
+decades. There is no category of "minor issue" that is acceptable
+to ship — if something is broken in any context where a user would
+encounter it, it must be fixed before merging. The project's
+extensive investment in testing, tooling, and review processes exists
+precisely so that these issues get caught and fixed, not so that they
+can be classified as low-priority and deferred.
+
+This philosophy extends to every aspect of the product:
+
+- **Visual precision matters.** Alignment, spacing, colors, and font
+  sizes must be consistent with similar existing UI. When making CSS
+  changes, you must demonstrate with pixel-precise before/after
+  comparisons that there are no unintended side effects.
+- **Every state matters.** UI must look correct in all its states:
+  hover, active, disabled, focused, selected, empty, overflowing.
+  It must work in both light and dark themes.
+- **Every window size matters.** UI must look good from wide desktop
+  (1920px) down to narrow phone screens (480px).
+- **Every language matters.** Translated strings can be 1.5x longer
+  than English or half as short. UI must handle both extremes without
+  breaking layout. Think about right-to-left languages too.
+- **Every interaction path matters.** Keyboard navigation, screen
+  readers, permission levels, feature interactions (banners
+  overlapping, resolved topics, muted messages), and edge cases in
+  data (empty lists, very long names, single items vs. many) must all
+  be considered.
+
+The right attitude is: "What could go wrong, and how do I verify that
+it doesn't?" not "It looks fine to me." **What isn't tested probably
+doesn't work** — this applies to visual changes just as much as to
+backend logic.
+
+### Understand before coding
 
 Before writing any code, you must understand:
 
@@ -267,22 +321,31 @@ tests.
 ### Manual Testing for UI Changes
 
 If a PR makes frontend changes, manually verify the affected UI. This
-catches issues that automated tests miss:
+catches issues that automated tests miss. **Treat this checklist as
+blocking, not advisory** — every applicable item must be verified
+before the change is ready.
 
 **Visual appearance:**
 
 - Is the new UI consistent with similar elements (fonts, colors, sizes)?
-- Is alignment correct, both vertically and horizontally?
+  Find the closest existing analogues and compare carefully.
+- Is alignment correct, both vertically and horizontally? Measure
+  programmatically with `getBoundingClientRect()` when in doubt —
+  don't eyeball it.
 - Do clickable elements have hover behavior consistent with similar UI?
 - If elements can be disabled, does the disabled state look right?
 - Did the change accidentally affect other parts of the UI? Use
-  `git grep` to check if modified CSS is used elsewhere.
+  `git grep` to check if modified CSS is used elsewhere. CSS changes
+  are notorious for unintended consequences — check every page and
+  component that shares the selectors you modified.
 - Check all of the above in both light and dark themes.
 
 **Responsiveness and internationalization:**
 
-- Does the UI look good at different window sizes, including mobile?
-- Would the UI break if translated strings were 1.5x longer than English?
+- Does the UI look good at different window sizes? Check wide desktop
+  (1920px), typical laptop (1280px), tablet, and narrow phone (480px).
+- Would the UI break if translated strings were 1.5x longer than
+  English? What if they were half as long? Both directions matter.
 
 **Functionality:**
 
@@ -296,6 +359,8 @@ catches issues that automated tests miss:
   has permissions and one who does not.
 - Think about feature interactions: could banners overlap? What about
   resolved/unresolved topics? Collapsed or muted messages?
+- Think about edge cases in data: empty lists, very long names, single
+  items vs. hundreds, special characters in strings.
 
 ### Puppeteer Visual Tests: Verifying Alignment
 
@@ -340,6 +405,18 @@ commits.
 
 ## Common Pitfalls
 
+### Treating Known Issues as Acceptable
+
+A common failure mode is discovering a problem during verification
+and then noting it as a known limitation rather than fixing it. At
+Zulip, there is no category of "known minor issue" that is acceptable
+to ship. If it's broken in any state, size, theme, or language, it
+needs to be fixed.
+
+**Mitigation:** When you find any issue during verification, fix it
+before presenting the work. If a fix would require a design decision,
+raise it as a question rather than shipping the broken state.
+
 ### Overconfident Code Generation
 
 You may generate code that looks correct but doesn't match Zulip patterns.
PATCH

echo "Gold patch applied."
