#!/usr/bin/env bash
set -euo pipefail

cd /workspace/gradio

# Idempotency guard
if grep -qF "- **Never use `container.querySelector`**. It is unconditionally banned. Use `ge" ".agents/skills/frontend-unit-testing/SKILL.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/.agents/skills/frontend-unit-testing/SKILL.md b/.agents/skills/frontend-unit-testing/SKILL.md
@@ -275,20 +275,12 @@ Always use the query utilities returned by `render()`. **Never use `container.qu
    getByPlaceholderText("Enter text...")
    ```
 
-3. **Test ID queries** (acceptable — when no semantic/text query works):
+3. **Test ID queries** (required fallback — when no semantic/text query works):
    ```ts
    getByTestId("source-select")
    getByTestId("password")
    ```
-   If the component lacks a useful `data-testid`, recommend adding one rather than falling back to `querySelector`.
-
-4. **`container.querySelector`** (absolute last resort — only when the DOM structure makes all of the above impossible):
-   ```ts
-   // Only when there is genuinely no role, label, text, or testid available.
-   // Document WHY in a comment when you use this.
-   // e.g., querying an <img> tag that has no alt text and no testid
-   const img = container.querySelector("img"); // no role/label available for bare img
-   ```
+   If the element lacks a `data-testid`, **add one to the component source**. This is always the right move. `container.querySelector` is never acceptable — adding a `data-testid` is cheap, explicit, and keeps test intent clear.
 
 Use `queryBy*` variants (which return `null` instead of throwing) when asserting something is **not** in the DOM:
 ```ts
@@ -351,7 +343,7 @@ await waitFor(() => {
 
 ## What NOT to Do
 
-- **Don't use `container.querySelector`** as a default. Use `getByRole`, `getByText`, `getByLabelText`, `getByDisplayValue`, `getByPlaceholderText`, or `getByTestId` first. If none of those work, recommend adding a `data-testid` to the component. `querySelector` is an absolute last resort and must include a comment explaining why no query utility works.
+- **Never use `container.querySelector`**. It is unconditionally banned. Use `getByRole`, `getByText`, `getByLabelText`, `getByDisplayValue`, `getByPlaceholderText`, or `getByTestId`. If none of those work, add a `data-testid` attribute to the component source — this is always the correct solution.
 - **Don't mock Svelte internals**, the DOM, or browser APIs that work natively.
 - **Don't unit-test purely visual styling** (colours, spacing, fonts, shadows). Instead, add `test.todo` placeholders recommending Playwright visual regression tests. Do test behavioural *effects* of styling (visibility, disabled state).
 - **Don't assert on internal class names** unless they are the mechanism by which a behaviour is expressed and there's no semantic alternative (e.g., `.sr-only` for screen-reader-only labels).
PATCH

echo "Gold patch applied."
