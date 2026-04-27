#!/usr/bin/env bash
set -euo pipefail

cd /workspace/zulip

# Idempotency guard
if grep -qF "- For zoomed clips, calculate the clip region from non-fixed elements;" ".claude/CLAUDE.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/.claude/CLAUDE.md b/.claude/CLAUDE.md
@@ -114,6 +114,9 @@ Zulip has over 185,000 words of developer documentation. Before working on any a
 - Prefer writing code that is readable without explanation over heavily
   commented code using clever tricks. Comments should explain "why" when
   the reason isn't obvious, not narrate "what" the code does.
+- Use `em` units instead of `px` for computed CSS values that need to
+  scale with font size. Pixel approximations break at different zoom
+  levels and font-size settings.
 - Comments should have a line to themself except for CSS px math.
 - **Review CSS for redundant rules.** After writing CSS, review the
   full set of rules affecting the same elements. Look for rules that
@@ -146,6 +149,9 @@ coherent idea."** This is non-negotiable.
 - Add content in one commit only to remove or move it in the next;
   plan upfront what belongs where and do it right the first time.
 - Include debugging code, commented-out code, or temporary TODOs.
+- Leave commits that break if a later commit in the PR is dropped.
+  When a commit is flagged as potentially droppable, verify all
+  earlier commits work correctly without it.
 
 ### Commit Message Format
 
@@ -285,6 +291,23 @@ catches issues that automated tests miss:
 - Think about feature interactions: could banners overlap? What about
   resolved/unresolved topics? Collapsed or muted messages?
 
+### Puppeteer Visual Tests: Verifying Alignment
+
+When using Puppeteer to verify visual alignment, do not rely on
+eyeballing screenshots — especially small full-page ones. Instead:
+
+- Use `page.evaluate()` with `getBoundingClientRect()` to measure
+  actual pixel positions of the elements you need aligned, and print
+  them to the console. Compare the numbers.
+- Always take **both** a full-page screenshot and a zoomed clip of
+  the area of interest.
+- For zoomed clips, calculate the clip region from non-fixed elements;
+  fixed/sticky elements may report bounding-box positions that don't
+  match their visual location on the page.
+- Be aware that CSS nesting can scope styles to a specific parent
+  (e.g., `.parent .my-class`) — reusing the same class name in a
+  different context may not pick up the expected styles.
+
 ## Self-Review Checklist
 
 Before finalizing, verify:
@@ -358,6 +381,10 @@ faster and easier to just plan and write them well the first time.
 - Don't use `cursor.execute()` with string formatting (SQL injection risk)
 - Don't use `.extra()` in Django without careful review and commenting
 - Don't use `onclick` attributes in HTML; use event delegation
+- Don't access DOM APIs (`document.documentElement.style`, `$()`
+  selectors for specific elements) without guarding for node test
+  environments, where the DOM is mocked minimally. Check that the
+  element exists before using it.
 - Don't create N+1 query patterns:
 
   ```python
@@ -375,6 +402,10 @@ faster and easier to just plan and write them well the first time.
   fetch + rebase when starting a project so you're not using a stale branch.
   If you're continuing a project, start by rebasing, resolving merge
   conflicts carefully.
+- Don't make design or UX decisions silently. When a technical
+  constraint forces a tradeoff, present the constraint and options
+  to the user rather than picking one. Never remove features, hide
+  UI elements, or change interaction patterns without asking.
 - Don't submit code you haven't tested
 - Don't skip becoming familiar with the code you're modifying
 - Don't make claims about code behavior without verification, and
PATCH

echo "Gold patch applied."
