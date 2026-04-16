#!/bin/bash
set -e

# Apply the gold patch for Link component keyboard accessibility fix
# This ensures Link without href renders as a button element

cd /workspace/storybook

# Check if already applied (idempotency check - look for distinctive line from patch)
if grep -q "as={href ? 'a' : 'button'}" code/core/src/components/components/typography/link/link.tsx 2>/dev/null; then
    echo "Patch already applied, skipping"
    exit 0
fi

# Apply the gold patch
patch -p1 <<'PATCH'
diff --git a/code/core/src/components/components/typography/link/link.tsx b/code/core/src/components/components/typography/link/link.tsx
index b63e69e639ca..03dea0305333 100644
--- a/code/core/src/components/components/typography/link/link.tsx
+++ b/code/core/src/components/components/typography/link/link.tsx
@@ -1,6 +1,8 @@
 import type { AnchorHTMLAttributes, MouseEvent } from 'react';
 import React, { forwardRef } from 'react';

+import { deprecate } from 'storybook/internal/client-logger';
+
 import { ChevronRightIcon } from '@storybook/icons';

 import { darken } from 'polished';
@@ -165,14 +167,22 @@ const A = styled.a<LinkStylesProps>(
           },
         }
       : {},
-  ({ isButton }) =>
+  ({ isButton, theme }) =>
     isButton
       ? {
           border: 0,
-          borderRadius: 0,
+          borderRadius: theme.input.borderRadius,
           background: 'none',
           padding: 0,
           fontSize: 'inherit',
+          lineHeight: 'inherit',
+
+          '&:focus-visible': {
+            outline: `2px solid ${theme.color.secondary}`,
+            outlineOffset: 2,
+            // Should ensure focus outline gets drawn above next sibling
+            zIndex: '1',
+          },
         }
       : {}
 );
@@ -194,25 +204,34 @@ export const Link = forwardRef<HTMLAnchorElement, LinkProps>(
       withArrow = false,
       containsIcon = false,
       className = undefined,
-      style = undefined,
-      isButton = false,
+      isButton = undefined,
+      href,
       ...rest
     },
     ref
-  ) => (
-    <A
-      {...rest}
-      ref={ref}
-      isButton={isButton}
-      role={isButton ? 'button' : undefined}
-      onClick={onClick && cancel ? (e) => cancelled(e, onClick) : onClick}
-      className={className}
-    >
-      <LinkInner withArrow={withArrow} containsIcon={containsIcon}>
-        {children}
-        {withArrow && <ChevronRightIcon />}
-      </LinkInner>
-    </A>
-  )
+  ) => {
+    if (isButton !== undefined) {
+      deprecate(
+        'Link: `isButton` is deprecated and will be removed in Storybook 11. Links without a `href` are automatically rendered as buttons.'
+      );
+    }
+
+    return (
+      <A
+        as={href ? 'a' : 'button'}
+        href={href}
+        {...rest}
+        ref={ref}
+        isButton={!href || isButton === true}
+        onClick={onClick && cancel ? (e) => cancelled(e, onClick) : onClick}
+        className={className}
+      >
+        <LinkInner withArrow={withArrow} containsIcon={containsIcon}>
+          {children}
+          {withArrow && <ChevronRightIcon />}
+        </LinkInner>
+      </A>
+    );
+  }
 );
 Link.displayName = 'Link';
PATCH

# Recompile the affected package
yarn nx compile core

echo "Patch applied successfully"
