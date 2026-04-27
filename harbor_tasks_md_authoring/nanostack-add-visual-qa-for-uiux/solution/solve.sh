#!/usr/bin/env bash
set -euo pipefail

cd /workspace/nanostack

# Idempotency guard
if grep -qF "After functional tests pass, take screenshots of every key state and analyze the" "qa/SKILL.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/qa/SKILL.md b/qa/SKILL.md
@@ -53,6 +53,40 @@ Use Playwright directly — do not install a custom browser daemon. Use `qa/bin/
 
 **Coverage order:** critical path first → error states → empty states → loading states.
 
+### Visual QA (Browser QA only)
+
+After functional tests pass, take screenshots of every key state and analyze the UI visually. This is not optional for web apps. A feature that works but looks broken is broken.
+
+**Take screenshots of:**
+- Home/landing page
+- Main feature in empty state (no data)
+- Main feature with data (after adding items)
+- Forms (before and after filling)
+- Error states
+- Mobile viewport (375px width)
+
+**Analyze each screenshot for:**
+
+1. **Layout**: Are elements aligned? Is spacing consistent? Are cards/sections balanced or does one side look crushed?
+2. **Visual hierarchy**: Can the user tell what's most important? Are headings, buttons and actions clearly differentiated?
+3. **Component quality**: Does it look like shadcn/ui or like raw HTML with borders? Are buttons, inputs, cards using proper component styling?
+4. **Typography**: Is text readable? Are font sizes proportional? Is there enough contrast?
+5. **Empty states**: Do empty states guide the user ("Add your first expense") or just show blank space?
+6. **Responsive**: Does the layout work at mobile width or does it break/overflow?
+7. **Dark mode**: If dark mode is enabled, are there contrast issues, invisible borders, or text that blends into the background?
+
+**Cross-reference against `/nano-plan` product standards.** If the plan said "shadcn/ui + Tailwind" and the output looks like raw HTML with inline styles, that's a finding.
+
+**Report visual findings as QA findings:**
+```
+- **UX/UI:** Layout imbalance on group page — members card 30% width, expenses 70%
+  - **Severity:** should_fix
+  - **Screenshot:** qa/results/group-page.png
+  - **Fix:** Balance grid columns, make cards equal width
+```
+
+Visual findings are should_fix by default. Blocking only if the UI is unusable (overlapping elements, invisible text, broken layout at common viewport sizes).
+
 ## Debug Mode
 
 When investigating a bug:
@@ -126,6 +160,7 @@ See `reference/artifact-schema.md` for the full schema. The user can disable aut
 |--------|-------|----------|----------|
 | Test scope | Happy path only | Happy + error + empty | Happy + error + edge + load |
 | Screenshots | On failure only | Key checkpoints | Every state |
+| Visual QA | Skip | Main states + mobile | Every state + mobile + dark mode |
 | Bug fix limit | 3 | 10 | 20 |
 | Regression tests | Skip | If fixing a bug | Full regression suite |
 | WTF threshold | 20% | 20% | 20% |
PATCH

echo "Gold patch applied."
