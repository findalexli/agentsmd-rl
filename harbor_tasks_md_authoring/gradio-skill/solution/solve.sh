#!/usr/bin/env bash
set -euo pipefail

cd /workspace/gradio

# Idempotency guard
if grep -qF "- **Don't use `toBeTruthy()` or `toBeFalsy()`.** These are too vague and hide in" ".agents/skills/frontend-unit-testing/SKILL.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/.agents/skills/frontend-unit-testing/SKILL.md b/.agents/skills/frontend-unit-testing/SKILL.md
@@ -290,8 +290,8 @@ Always use the query utilities returned by `render()`. **Never use `container.qu
 
 Use `queryBy*` variants (which return `null` instead of throwing) when asserting something is **not** in the DOM:
 ```ts
-expect(queryByRole("button")).toBeNull();
-expect(queryByLabelText("Upload file")).toBeNull();
+expect(queryByRole("button")).not.toBeInTheDocument();
+expect(queryByLabelText("Upload file")).not.toBeInTheDocument();
 ```
 
 ### Common assertion patterns
@@ -302,8 +302,8 @@ expect(el).toBeVisible();
 expect(el).not.toBeVisible();
 
 // Presence
-expect(queryByRole("button")).toBeNull();        // not in DOM
-expect(getByRole("button")).toBeTruthy();         // in DOM
+expect(queryByRole("button")).not.toBeInTheDocument();  // not in DOM
+expect(getByRole("button")).toBeInTheDocument();        // in DOM
 
 // Values
 expect(el).toHaveValue("hello");
@@ -354,6 +354,15 @@ await waitFor(() => {
 - **Don't unit-test purely visual styling** (colours, spacing, fonts, shadows). Instead, add `test.todo` placeholders recommending Playwright visual regression tests. Do test behavioural *effects* of styling (visibility, disabled state).
 - **Don't assert on internal class names** unless they are the mechanism by which a behaviour is expressed and there's no semantic alternative (e.g., `.sr-only` for screen-reader-only labels).
 - **Don't manually rewrite shared prop tests.** `run_shared_prop_tests` handles `elem_id`, `elem_classes`, `visible`, `label`, `show_label`, `validation_error`. Always call it. If a specific test doesn't apply, use the config flags (`has_label: false`, `has_validation_error: false`) — never skip the utility and hand-roll the tests instead.
+- **Don't use `toBeTruthy()` or `toBeFalsy()`.** These are too vague and hide intent. Use the most specific matcher for the value being checked:
+  - Element in DOM → `toBeInTheDocument()` / `.not.toBeInTheDocument()`
+  - Element visible → `toBeVisible()` / `.not.toBeVisible()`
+  - Element has value → `toHaveValue("x")`
+  - Element checked → `toBeChecked()`
+  - Element disabled → `toBeDisabled()` / `toBeEnabled()`
+  - Boolean variable → `toBe(true)` / `toBe(false)`
+  - Array non-empty → `toHaveLength(n)` or `expect(arr.length).toBeGreaterThan(0)`
+  - Non-DOM null/undefined → `toBeNull()` / `toBeDefined()` / `toBeUndefined()`
 - **Don't add `setTimeout` or artificial delays.** Use `await tick()`, `await fireEvent.x()`, or `await waitFor()`.
 - **Don't write snapshot tests.** They test implementation, not behaviour.
 - **Don't import from `@testing-library/svelte`** — always use `@self/tootils/render`.
PATCH

echo "Gold patch applied."
