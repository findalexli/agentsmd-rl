#!/usr/bin/env bash
set -euo pipefail

cd /workspace/prefect

# Idempotency guard
if grep -qF "- **CSS custom properties**: JSDOM does not load external stylesheets, so `getCo" "ui-v2/src/components/AGENTS.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/ui-v2/src/components/AGENTS.md b/ui-v2/src/components/AGENTS.md
@@ -62,6 +62,13 @@ This directory contains React components for the Prefect UI migration from Vue t
 - API mocks are in @prefect/ui-v2/src/api/mocks
 - All API calls should be mocked using `msw`
 - NEVER skip tests
+- **CSS custom properties**: JSDOM does not load external stylesheets, so `getComputedStyle` returns `""` for CSS custom properties (e.g., Tailwind breakpoint tokens like `--breakpoint-lg`). Mock them by spying on `CSSStyleDeclaration.prototype.getPropertyValue`:
+  ```ts
+  vi.spyOn(CSSStyleDeclaration.prototype, "getPropertyValue")
+    .mockImplementation((name) => name === "--breakpoint-lg" ? "64rem" : "");
+  ```
+  Always call `vi.restoreAllMocks()` in `afterEach` to clean up.
+- **`matchMedia` mocking**: JSDOM does not implement `window.matchMedia`. Stub it via `Object.defineProperty(window, "matchMedia", ...)` and restore the original in `afterEach`.
 
 ## Storybook Best Practices
 
PATCH

echo "Gold patch applied."
