#!/usr/bin/env bash
set -euo pipefail

FILE="js/atoms/src/Block.svelte"

# Idempotency: check if already fixed (--block-border-width: 0 replaced by border-width: 0)
# The base has --block-border-width: 0 in hide-container. After fix, it's border-width: 0.
if ! grep -q '\-\-block-border-width: 0' "$FILE"; then
    echo "Patch already applied."
    exit 0
fi

git apply - <<'PATCH'
diff --git a/js/atoms/src/Block.svelte b/js/atoms/src/Block.svelte
index 12e46f3c42..dcd60cef10 100644
--- a/js/atoms/src/Block.svelte
+++ b/js/atoms/src/Block.svelte
@@ -127,7 +127,6 @@
 		style:overflow={allow_overflow ? overflow_behavior : "hidden"}
 		style:flex-grow={scale}
 		style:min-width={`calc(min(${min_width}px, 100%))`}
-		style:border-width="var(--block-border-width)"
 		class:auto-margin={scale === null}
 		dir={rtl ? "rtl" : "ltr"}
 		aria-label={label}
@@ -166,6 +165,7 @@
 		background: var(--block-background-fill);
 		width: 100%;
 		line-height: var(--line-sm);
+		border-width: var(--block-border-width);
 	}
 	.block.fullscreen {
 		border-radius: 0;
@@ -200,7 +200,7 @@
 	.hide-container:not(.fullscreen) {
 		margin: 0;
 		box-shadow: none;
-		--block-border-width: 0;
+		border-width: 0;
 		background: transparent;
 		padding: 0;
 		overflow: visible;

PATCH

echo "Patch applied successfully."
