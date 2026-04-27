#!/usr/bin/env bash
set -euo pipefail

cd /workspace/angular

TARGET="skills/dev-skills/angular-developer/references/testing-fundamentals.md"

# Idempotency: if the distinctive removed phrase is already gone, the patch
# was already applied — do nothing.
if ! grep -q "## Custom Utilities" "${TARGET}"; then
    echo "solve.sh: gold patch already applied (no '## Custom Utilities' heading present)" >&2
    exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/skills/dev-skills/angular-developer/references/testing-fundamentals.md b/skills/dev-skills/angular-developer/references/testing-fundamentals.md
index 0e0953064640..d58ada3a5000 100644
--- a/skills/dev-skills/angular-developer/references/testing-fundamentals.md
+++ b/skills/dev-skills/angular-developer/references/testing-fundamentals.md
@@ -64,12 +64,3 @@ describe('MyComponent', () => {
   - `fixture.componentInstance`: Access the component's class instance.
   - `fixture.nativeElement`: Access the component's root DOM element.
   - `fixture.debugElement`: An Angular-specific wrapper around the `nativeElement` that provides safer, platform-agnostic ways to query the DOM (e.g., `debugElement.query(By.css('p'))`).
-
-## Custom Utilities
-
-To keep tests fast and avoid long waits, this project provides custom utilities:
-
-- **`useAutoTick()`**: (from `packages/private/testing/src/utils.ts`) Fast-forwards time via a mock clock to avoid real waits.
-- **`await timeout(ms)`**: (from `packages/private/testing/src/utils.ts`) Use for cases where a specific real-time delay is unavoidable.
-
-Always prefer `useAutoTick()` to keep tests efficient.
PATCH

echo "solve.sh: gold patch applied" >&2
