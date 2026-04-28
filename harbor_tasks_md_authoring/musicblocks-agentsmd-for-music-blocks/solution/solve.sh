#!/usr/bin/env bash
set -euo pipefail

cd /workspace/musicblocks

# Idempotency guard
if grep -qF "Ask the user for a browser check when the change affects UI, widgets, drag/drop," "AGENTS.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/AGENTS.md b/AGENTS.md
@@ -0,0 +1,118 @@
+# AGENTS.md
+
+Use this when working on a bug fix, addition/improving a feature.
+
+## 1. Understand Before Editing
+
+**Do not guess. Read the code path that actually owns the problem.**
+
+Before changing code:
+- Check whether the reported bug is already fixed on the current branch.
+- Read the exact files involved before proposing or writing a fix.
+- Inspect 2-3 nearby examples in the same subsystem and copy existing patterns.
+- If the issue is unclear, say what is unclear instead of making up behavior.
+
+Quick repo map:
+- `js/activity.js` - app entry point, load order, runtime wiring
+- `js/block.js` - behavior of a single block in the UI
+- `js/blocks.js` - workspace block management, connections, drag/drop, stack behavior
+- `js/basicblocks.js` - registration of the main block sets
+- `js/blocks/*.js` - block definitions by palette
+- `js/turtleactions/*.js` - runtime behavior triggered by blocks
+- `js/logo.js` - project execution engine
+- `js/artwork.js` - block artwork and palette visuals
+- `js/widgets/*.js` - larger UI widgets
+- `js/utils/*.js` - shared helpers, often high impact
+
+Use the smallest path that matches the issue. Example:
+- wrong block UI or menu -> `js/block.js`, `js/artwork.js`, relevant file in `js/blocks/`
+- wrong block behavior -> relevant file in `js/blocks/` and matching file in `js/turtleactions/`
+- execution bug -> `js/logo.js`
+- drag/drop or stack behavior -> `js/blocks.js`
+- startup or load-order bug -> `js/activity.js`
+
+## 2. Fix The Real Problem
+
+**Do not be a lazy AI. Do not hide the symptom and call it fixed.**
+
+- Trace the issue through the real execution path.
+- Identify the source of truth and fix the bug there.
+- Do not stop at the first patch that makes the current reproduction steps disappear.
+- Avoid one-off guards, scattered conditionals, duplicated special cases, and UI-only masking.
+- If a temporary workaround is the only safe option, say so explicitly.
+- If the bug is not fixed after 2-3 iterations write console logs to see what going wrong.
+
+If the issue is already fixed or cannot be reproduced from the current code, tell the user that
+clearly instead of forcing a hypothetical patch.
+
+## 3. Keep Changes Surgical
+
+**Minimum code that solves the requested problem. Nothing speculative.**
+
+- Do not add features that were not requested.
+- Do not refactor unrelated code.
+- Do not "clean up" nearby files just because you are already there.
+- Match the existing style and structure of the file you are editing.
+- Every changed line should trace back to the issue being solved.
+
+## 4. Follow Music Blocks Patterns
+
+**This repo has sharp edges. Respect them.**
+
+- Main browser code in `js/` uses `sourceType: "script"`, RequireJS, and globals.
+- Do not use ES `import` or `export` in main browser source files.
+- Keep accurate `/* global */` and `/* exported */` headers in browser scripts.
+- If a file already uses guarded `module.exports` for Jest, preserve that pattern.
+- New files need the AGPL license header.
+- Never modify `lib/`.
+- Do not casually reorder load-sensitive code in `js/activity.js`.
+- Do not rename internal block names. Saved projects depend on them.
+
+Block/runtime rules:
+- `ValueBlock` implementations must return a value from `arg()`.
+- `FlowBlock` implementations must return the expected flow result, not implicit `undefined`.
+- `Singer.XxxActions` behavior belongs in static action methods.
+- New block work may require coordinated updates across definitions, registration, artwork, help
+  text, macros, and related mappings.
+
+Style:
+- 4 spaces
+- double quotes
+- semicolons
+- no trailing commas
+- LF line endings
+- comments only when they add real value
+
+## 5. Verify Intelligently
+
+**Prove the fix. Do not just hope.**
+
+- For logic bugs, add or update focused Jest coverage when possible.
+- Verify the intended fix and the nearest related behavior so the change is not correct only for one narrow case.
+- Start with the smallest relevant checks, then broaden if the change is risky.
+
+Standard validation:
+- `npm run lint`
+- `npx prettier --check .`
+- `npm test`
+
+Ask the user for a browser check when the change affects UI, widgets, drag/drop, rendering, audio, persistence, startup behavior, or another interaction that tests do not fully cover.
+
+When asking for browser testing, give exact steps:
+1. Run `npm run dev` or `npm run serve:dev`
+2. Open `http://127.0.0.1:3000`
+3. Reproduce the issue with the smallest possible project
+4. State the expected result
+5. Report any browser console errors if they appear
+
+For pure logic bugs with strong focused tests, do not block on manual browser testing.
+
+## 6. Report Clearly
+
+**Leave the contributor and reviewer with a clear picture.**
+
+- Say what changed.
+- Say how it was verified.
+- Say what remains unverified.
+- If the current branch already contains the fix, say that plainly.
+
PATCH

echo "Gold patch applied."
