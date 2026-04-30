#!/usr/bin/env bash
set -euo pipefail

cd /workspace/goose

# Idempotency guard
if grep -qF "If the project has a stronger pre-push or CI gate than this helper set, run that" ".agents/skills/code-review/SKILL.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/.agents/skills/code-review/SKILL.md b/.agents/skills/code-review/SKILL.md
@@ -92,6 +92,16 @@ You are a senior engineer conducting a thorough code review. Review **only the l
 - **AnimatePresence**: Is it used properly with unique keys for dialog/modal transitions?
 - **Reduced Motion**: Is `useReducedMotion()` respected for accessibility?
 
+### Async State, Defaults & Persistence
+- **Async Source of Truth**: During async provider/model/session mutations, does UI/session/localStorage state update only after the backend accepts the change? If the UI updates optimistically, is there an explicit rollback path?
+- **UI/Backend Drift**: Could the UI show provider/model/project/persona X while the backend is still on Y after a failed mutation, delayed prepare, or pending-to-real session handoff?
+- **Requested vs Fallback Authority**: Do explicit user or caller selections stay authoritative over sticky defaults, saved preferences, aliases, or fallback resolution?
+- **Dependent State Invalidation**: When a parent selection changes (provider/project/persona/workspace/etc.), are dependent values like `modelId`, `modelName`, defaults, or cached labels cleared or recomputed so stale state does not linger?
+- **Persisted Preference Validation**: Are stored selections validated against current inventory/capabilities before reuse, and do stale values fail soft instead of breaking creation flows?
+- **Compatibility of Fallbacks**: Are default or sticky selections guaranteed to remain compatible with the active concrete provider/backend, instead of leaking across providers?
+- **Best-Effort Lookups**: Do inventory/config/default-resolution lookups degrade gracefully on transient failure, or can they incorrectly block a primary flow that should still work with a safe fallback?
+- **Draft/Home/Handoff Paths**: If the product has draft, Home, pending, or pre-created sessions, did you review those handoff paths separately from the already-active session path?
+
 ### General Code Quality
 - **Error Handling**: Are errors handled gracefully with user-friendly messages?
 - **Loading States**: Are loading states shown during async operations?
@@ -104,13 +114,18 @@ You are a senior engineer conducting a thorough code review. Review **only the l
 
 ### Step 0: Run Quality Checks
 
-Before reading any code, run the project's CI gate to establish a baseline:
+Before reading any code, run the project's CI gate to establish a baseline. Use **check-only** commands so the baseline never mutates the working tree — otherwise auto-formatters can introduce unstaged diffs and you'll end up reviewing formatter output instead of the author's actual changes.
+
+Avoid `just check-everything` as the baseline in this repo: that recipe runs `cargo fmt --all` in write mode and will modify the working tree. Run the non-mutating equivalents instead:
 
 ```bash
-just ci
+cargo fmt --all -- --check
+cargo clippy --all-targets -- -D warnings
+(cd ui/desktop && pnpm run lint:check)
+./scripts/check-openapi-schema.sh
 ```
 
-This runs: `pnpm check` (Biome lint/format + file sizes), `pnpm typecheck`, `just clippy` (Rust linting), `pnpm test`, `pnpm build`, and `just tauri-check` (Rust type checking).
+If the project has a stronger pre-push or CI gate than this helper set, run that fuller gate when the review is meant to be PR-ready, but only after confirming it is also non-mutating (or run it from a clean stash). In this repo, targeted tests for the changed area plus the pre-push checks are often the practical follow-up.
 
 Report the results as pass/fail. Any failures are automatically **P0** issues and should appear at the top of the findings list. Do not skip this step even if the user only wants a quick review.
 
@@ -120,7 +135,8 @@ For each file in the list:
 
 1. Run `git diff main...HEAD -- <file>` to get the exact lines that changed
 2. Review **only those changed lines** against the Review Checklist — do not flag issues in unchanged code
-3. Note the file path and line numbers from the diff output for each issue found
+3. For stateful UI or async flow changes, trace the full path end to end: user selection -> local/session state update -> persistence -> backend prepare/set/update call -> failure/rollback path
+4. Note the file path and line numbers from the diff output for each issue found
 
 ### Step 2: Categorize Issues
 
@@ -152,16 +168,17 @@ After reviewing all files, provide:
 
 ### Step 3b: Self-Check
 
-Before presenting findings to the user, silently review the issue list two more times:
+Before presenting findings to the user, silently review the issue list three times:
 
 1. **Pass 1**: For each issue, ask — is this genuinely a problem, or could it be intentional/acceptable? Remove false positives.
 2. **Pass 2**: For each remaining issue, ask — does the recommended fix actually improve the code, or is it a matter of preference?
+3. **Pass 3**: For async state/default-resolution issues, ask — can the UI, persisted state, and backend ever disagree after a failure, fallback, or session handoff?
 
-After both passes, tag each surviving issue as one of:
+After these passes, tag each surviving issue as one of:
 - **[Must Fix]** — clear violation, will likely get flagged in PR review
 - **[Your Call]** — valid concern but may be intentional or a reasonable tradeoff (e.g. stepping outside the design system for a specific reason). Present it but let the user decide.
 
-Only present issues that survived both passes.
+Only present issues that survived these passes.
 
 ### Step 4: Fix Issues
 
@@ -189,7 +206,7 @@ Once all issues are fixed, display:
 
 **✅ Code review complete! All issues have been addressed.**
 
-Your code is ready to commit and push. Lefthook will run the full CI gate (`just ci`) automatically when you push.
+Your code is ready to commit and push. Lefthook and CI will run the repo's configured gates when you push.
 
 Next steps: generate a PR summary that explains the intent of this change, what files were modified and why, and how to verify the changes work.
 
PATCH

echo "Gold patch applied."
