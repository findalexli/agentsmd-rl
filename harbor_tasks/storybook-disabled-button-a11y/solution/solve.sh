#!/bin/bash
set -e

cd /workspace/storybook

# Apply the gold patch to fix disabled button accessibility
cat <<'PATCH' | git apply -
diff --git a/code/core/src/components/components/Button/Button.tsx b/code/core/src/components/components/Button/Button.tsx
index 63a8d4a338..b8449a407e 100644
--- a/code/core/src/components/components/Button/Button.tsx
+++ b/code/core/src/components/components/Button/Button.tsx
@@ -138,12 +138,13 @@ export const Button = forwardRef<HTMLButtonElement, ButtonProps>(
             variant={variant}
             size={size}
             padding={padding}
-            disabled={disabled || readOnly}
+            $disabled={disabled || readOnly}
+            aria-disabled={disabled || readOnly ? 'true' : undefined}
             readOnly={readOnly}
             active={active}
             animating={isAnimating}
             animation={animation}
-            onClick={handleClick}
+            onClick={disabled || readOnly ? undefined : handleClick}
             aria-label={!readOnly && ariaLabel !== false ? ariaLabel : undefined}
             aria-keyshortcuts={readOnly ? undefined : shortcutAttribute}
             {...(readOnly ? {} : ariaDescriptionAttrs)}
@@ -165,7 +166,7 @@ const StyledButton = styled('button', {
   padding?: 'small' | 'medium' | 'none';
   variant?: 'outline' | 'solid' | 'ghost';
   active?: boolean;
-  disabled?: boolean;
+  $disabled?: boolean;
   readOnly?: boolean;
   animating?: boolean;
   animation?: 'none' | 'rotate360' | 'glow' | 'jiggle';
@@ -174,15 +175,15 @@ const StyledButton = styled('button', {
     theme,
     variant,
     size,
-    disabled,
+    $disabled,
     readOnly,
     active,
     animating,
     animation = 'none',
     padding,
   }) => ({
     border: 0,
-    cursor: readOnly ? 'inherit' : disabled ? 'not-allowed' : 'pointer',
+    cursor: readOnly ? 'inherit' : $disabled ? 'not-allowed' : 'pointer',
     display: 'inline-flex',
     gap: '6px',
     alignItems: 'center',
@@ -216,7 +217,7 @@ const StyledButton = styled('button', {
     verticalAlign: 'top',
     whiteSpace: 'nowrap',
     userSelect: 'none',
-    opacity: disabled && !readOnly ? 0.5 : 1,
+    opacity: $disabled && !readOnly ? 0.5 : 1,
     margin: 0,
     fontSize: `${theme.typography.size.s1}px`,
     fontWeight: theme.typography.weight.bold,
PATCH

# Verify the distinctive line is present (idempotency check)
if ! grep -q "aria-disabled={disabled || readOnly ? 'true' : undefined}" code/core/src/components/components/Button/Button.tsx; then
    echo "ERROR: Patch was not applied successfully"
    exit 1
fi

echo "Patch applied successfully"
