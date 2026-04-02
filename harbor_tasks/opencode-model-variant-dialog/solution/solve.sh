#!/usr/bin/env bash
set -euo pipefail

REPO_ROOT="/workspace/opencode"

# Idempotency: check if DialogVariant is already imported in app.tsx
if grep -q 'import.*DialogVariant' "$REPO_ROOT/packages/opencode/src/cli/cmd/tui/app.tsx" 2>/dev/null; then
  echo "Patch already applied."
  exit 0
fi

cd "$REPO_ROOT"

git apply - <<'PATCH'
diff --git a/packages/opencode/src/cli/cmd/tui/app.tsx b/packages/opencode/src/cli/cmd/tui/app.tsx
index 5a2e1b15588..3cb383be48d 100644
--- a/packages/opencode/src/cli/cmd/tui/app.tsx
+++ b/packages/opencode/src/cli/cmd/tui/app.tsx
@@ -121,6 +121,7 @@ async function getTerminalBackgroundColor(): Promise<"dark" | "light"> {
 }

 import type { EventSource } from "./context/sdk"
+import { DialogVariant } from "./component/dialog-variant"

 function rendererConfig(_config: TuiConfig.Info): CliRendererConfig {
   return {
@@ -580,12 +581,12 @@ function App(props: { onSnapshot?: () => Promise<string[]> }) {
       },
     },
     {
-      title: "Variant cycle",
+      title: "Switch model variant",
       value: "variant.cycle",
       keybind: "variant_cycle",
       category: "Agent",
       onSelect: () => {
-        local.model.variant.cycle()
+        dialog.replace(() => <DialogVariant />)
       },
     },
     {

PATCH

echo "Patch applied successfully."
