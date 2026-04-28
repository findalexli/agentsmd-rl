#!/usr/bin/env bash
set -euo pipefail

cd /workspace/calcite-design-system

# Idempotency guard
if grep -qF "- Prefer `*.browser.e2e.tsx` for new component tests that use **Vitest locators*" ".github/copilot-instructions.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/.github/copilot-instructions.md b/.github/copilot-instructions.md
@@ -11,6 +11,7 @@
 - `packages/components`: source for Calcite web components.
 - `packages/components-react`: React wrappers generated around component APIs. Avoid manual edits here unless the task is explicitly React-wrapper specific.
 - `packages/design-tokens`, `packages/ui-icons`, `packages/eslint-plugin-components`, and `packages/tailwind-preset`: shared package-level concerns. Only change them when the task clearly requires it.
+- Some workspace packages are internal or private tooling packages. Only change them when the task explicitly targets those package-level concerns.
 
 ## Priorities
 
@@ -36,6 +37,7 @@ In descending order when rules conflict:
 - Do NOT introduce new libraries, frameworks, or dependencies unless approved.
 - Do NOT modify unrelated files.
 - If you notice a potential improvement, suggest it but wait for approval.
+- When browser baseline updates or modern web development resources suggest a new pattern, propose it with supporting references (e.g., MDN, web.dev, Baseline status) and wait for approval before applying it.
 - Avoid browser-specific fixes. Prefer feature detection instead.
 
 ## Code Quality
@@ -47,7 +49,7 @@ In descending order when rules conflict:
 - Do not add comments for obvious code. Improve naming or structure instead.
 - Reduce branching and duplication when it improves readability, but do not compress code into dense expressions just to be shorter.
 - Sort properties alphabetically where the existing repo patterns expect it, but do not create unrelated churn just to reorder code.
-- Use strict TypeScript typings, prefer the `nil` type where a value may be `null` or `undefined`, and avoid unnecessary type widening.
+- Use strict TypeScript typings and avoid unnecessary type widening.
 
 ## Component Conventions
 
@@ -91,17 +93,16 @@ In descending order when rules conflict:
 ## Testing
 
 - Every bug fix or feature change should include automated test coverage.
-- Prefer `*.browser.e2e.tsx` for new component tests that use **Vite locators** (use the project’s established locator patterns first). Legacy `*.e2e.ts` tests still exist and continue to run, so update them when required by the changed behavior.
+- Prefer `*.browser.e2e.tsx` for new component tests that use **Vitest locators** (use the project’s established locator patterns first). Legacy `*.e2e.ts` tests still exist and continue to run, so update them when required by the changed behavior.
 - Use shared helpers from `packages/components/src/tests/commonTests` and `packages/components/src/tests/utils` instead of duplicating test utilities.
-- For new UI functionality, add applicable **Storybook stories** and update existing stories when behavior changes.
-- Always use CSS classes when adding/updating stories instead of repeating styles.
 - If a change impacts user interaction, include assertions that validate the intended UX behavior and avoid flaky selectors.
 - If changes are visual, prefer updating stories in addition to tests when behavior also changes.
 - If a change is purely visual, prefer updating stories over adding end-to-end tests unless new interaction coverage is needed.
 - If you’re unsure whether a story or test is warranted, propose the smallest useful one and explain why.
 - Follow `packages/components/conventions/Testing.md` for story and test expectations.
 - Prefer focused behavioral tests over implementation detail tests.
 - Do not add unrelated test coverage in the same change.
+- Always use CSS classes when adding/updating stories instead of repeating styles.
 - Targeted commands for component work:
   - `npm --workspace=packages/components run test:stable -- <path>`
   - `npm --workspace=packages/components run test:experimental -- <path>`
@@ -130,6 +131,7 @@ In descending order when rules conflict:
 - When drafting review comments or PR text, be direct, collaborative, and specific.
 - Avoid sounding absolute, dismissive, or overly corrective.
 - Prefer wording that explains what changed and why in concrete terms.
+- When helpful, label the type of review comment up front (for example, `fixme` or `suggestion`) so the intent is clear.
 
 ## Reference Docs
 
PATCH

echo "Gold patch applied."
