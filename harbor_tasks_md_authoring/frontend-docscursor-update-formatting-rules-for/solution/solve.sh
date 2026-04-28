#!/usr/bin/env bash
set -euo pipefail

cd /workspace/frontend

# Idempotency guard
if grep -qF "- When calling `task.perform()` in lifecycle hooks like `handleDidInsert`, use `" ".cursor/rules/formatting-component-files.mdc"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/.cursor/rules/formatting-component-files.mdc b/.cursor/rules/formatting-component-files.mdc
@@ -9,6 +9,7 @@ When creating components, follow these rules:
 - `class` doesn't have to be in `Args`, ember automatically forwards native args like `class`, `id` etc. to the component
 - Ensure the component is registered w/ Glint using `declare module ...`
 - Ensure service registrations using `@service` are grouped together and sorted alphabetically
+- When calling `task.perform()` in lifecycle hooks like `handleDidInsert`, use `await` so that tests will properly wait for the async operation to complete
 
 Example:
 
PATCH

echo "Gold patch applied."
