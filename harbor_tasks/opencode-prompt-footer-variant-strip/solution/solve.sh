#!/usr/bin/env bash
set -euo pipefail

FILE="packages/opencode/src/cli/cmd/tui/component/prompt/index.tsx"

# Idempotency: check if variant_cycle block is already removed
if ! grep -q 'variant_cycle' "$FILE"; then
  echo "Already applied."
  exit 0
fi

git apply - <<'PATCH'
diff --git a/packages/opencode/src/cli/cmd/tui/component/prompt/index.tsx b/packages/opencode/src/cli/cmd/tui/component/prompt/index.tsx
index f6ac9660d30..29e09f64c74 100644
--- a/packages/opencode/src/cli/cmd/tui/component/prompt/index.tsx
+++ b/packages/opencode/src/cli/cmd/tui/component/prompt/index.tsx
@@ -1189,11 +1189,6 @@ export function Prompt(props: PromptProps) {
                       )}
                     </Match>
                     <Match when={true}>
-                      <Show when={local.model.variant.list().length > 0}>
-                        <text fg={theme.text}>
-                          {keybind.print("variant_cycle")} <span style={{ fg: theme.textMuted }}>variants</span>
-                        </text>
-                      </Show>
                       <text fg={theme.text}>
                         {keybind.print("agent_cycle")} <span style={{ fg: theme.textMuted }}>agents</span>
                       </text>

PATCH

echo "Applied: removed variant cycle display from prompt footer."
