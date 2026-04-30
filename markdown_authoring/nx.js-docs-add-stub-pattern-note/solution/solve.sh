#!/usr/bin/env bash
set -euo pipefail

cd /workspace/nx.js

# Idempotency guard
if grep -qF "- **`stub()` does NOT mean unimplemented.** Methods marked with `stub()` in Type" "AGENTS.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/AGENTS.md b/AGENTS.md
@@ -202,3 +202,4 @@ The `screen` global is the main display (1280×720). Use `screen.getContext('2d'
 - `romfs:/` paths use forward slashes, colon after scheme
 - **Globals like `setTimeout`, `setInterval`, `clearTimeout`, `clearInterval` are NOT available inside `packages/runtime/src/`** — they're only registered as globals in `index.ts` for user code. Within the runtime package itself, import them: `import { setInterval, clearInterval } from './timers';`
 - **Gamepad button mapping** is NOT standard Web Gamepad API order. Use `@nx.js/constants` `Button` enum (e.g. `Button.A`, `Button.B`). The order is: B=0, A=1, Y=2, X=3, L=4, R=5, ZL=6, ZR=7, Minus=8, Plus=9, StickL=10, StickR=11, Up=12, Down=13, Left=14, Right=15
+- **`stub()` does NOT mean unimplemented.** Methods marked with `stub()` in TypeScript (from `./utils`) are placeholders for type generation only. At runtime, the C side overwrites them on the prototype via `NX_DEF_FUNC()` or `NX_DEF_GET()`/`NX_DEF_GETSET()`. If you see `stub()`, check the corresponding C file's `nx_init_*` or `*_init_class` function — the real implementation is there. Only `throw new Error('Method not implemented.')` means actually not implemented.
PATCH

echo "Gold patch applied."
