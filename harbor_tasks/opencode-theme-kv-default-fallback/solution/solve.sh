#!/usr/bin/env bash
set -euo pipefail

FILE="packages/opencode/src/cli/cmd/tui/context/theme.tsx"

# Idempotency: skip if kv.get("theme") fallback already present in the memo
if grep -q 'kv\.get("theme")' "$FILE"; then
  echo "Patch already applied."
  exit 0
fi

git apply - <<'PATCH'
diff --git a/packages/opencode/src/cli/cmd/tui/context/theme.tsx b/packages/opencode/src/cli/cmd/tui/context/theme.tsx
index 008f1bf806c..dcef2cb466f 100644
--- a/packages/opencode/src/cli/cmd/tui/context/theme.tsx
+++ b/packages/opencode/src/cli/cmd/tui/context/theme.tsx
@@ -399,7 +399,16 @@ export const { use: useTheme, provider: ThemeProvider } = createSimpleContext({
     })

     const values = createMemo(() => {
-      return resolveTheme(store.themes[store.active] ?? store.themes.opencode, store.mode)
+      const active = store.themes[store.active]
+      if (active) return resolveTheme(active, store.mode)
+
+      const saved = kv.get("theme")
+      if (typeof saved === "string") {
+        const theme = store.themes[saved]
+        if (theme) return resolveTheme(theme, store.mode)
+      }
+
+      return resolveTheme(store.themes.opencode, store.mode)
     })

     createEffect(() => {

PATCH

echo "Patch applied successfully."
