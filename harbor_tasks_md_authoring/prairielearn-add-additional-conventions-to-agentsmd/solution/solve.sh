#!/usr/bin/env bash
set -euo pipefail

cd /workspace/prairielearn

# Idempotency guard
if grep -qF "- Don't add extra defensive checks or try/catch blocks that are abnormal for tha" "AGENTS.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/AGENTS.md b/AGENTS.md
@@ -41,6 +41,24 @@ Run `make format-js-cached` / `make lint-js-cached` from the root directory to f
 
 Run `make format-python` / `make lint-python` from the root directory to format/lint all Python code.
 
+## Conventions
+
+### Stylistic conventions
+
+- NEVER use `as any` casts in TypeScript code to avoid type errors.
+- Don't add extra defensive checks or try/catch blocks that are abnormal for that area of the codebase (especially if called by trusted / validated codepaths).
+- Don't add extra comments that a human wouldn't add or that are inconsistent with the rest of the file.
+
+### Library usage conventions
+
+- Use `@tanstack/react-query` for API calls.
+- Use `react-hook-form` for form handling.
+
+### User interface conventions
+
+- Use `react-bootstrap` components for UI elements.
+- Titles and buttons should use sentence case ("Save course", "Discard these changes").
+
 ## Testing
 
 TypeScript tests are written with Vitest. Unit tests are located next to the code they test in files with a `.test.ts` suffix. Integration tests are located in dedicated `tests` directories, e.g. `apps/prairielearn/src/tests`.
@@ -74,5 +92,4 @@ The PrairieLearn web application renders HTML in one of two ways:
 - Use `clsx` and `class="..."` in Preact components.
 - Pass `res.locals` to `getPageContext` to get information about the course instance / authentication state.
 - If you hydrate a component with `Hydrate`, you must register the component with `registerHydratedComponent` in a file in `apps/prairielearn/assets/scripts/esm-bundles/hydrated-components`.
-- NEVER use `as any` in TypeScript code to avoid type errors.
 - If you get a build error relating to the type of an error being unknown, you can use `yarn tsc -p assets/scripts/tsconfig.json --traceResolution` to debug the issue.
PATCH

echo "Gold patch applied."
