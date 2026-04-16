#!/bin/bash
set -e

cd /workspace/mantine

# Check if already patched (idempotency check)
if grep -q "openDelay?: number;" packages/@mantine/core/src/components/Menu/MenuSub/MenuSub.tsx; then
    echo "Patch already applied, skipping..."
    exit 0
fi

# Apply the gold patch
cat <<'PATCH' | git apply -
diff --git a/packages/@mantine/core/src/components/Menu/MenuSub/MenuSub.tsx b/packages/@mantine/core/src/components/Menu/MenuSub/MenuSub.tsx
index d31c67f3e22..c3ef0a4ae82 100644
--- a/packages/@mantine/core/src/components/Menu/MenuSub/MenuSub.tsx
+++ b/packages/@mantine/core/src/components/Menu/MenuSub/MenuSub.tsx
@@ -18,6 +18,9 @@ export interface MenuSubProps extends __PopoverProps {
   /** Called with current state when dropdown opens or closes */
   onChange?: (opened: boolean) => void;

+  /** Open delay in ms */
+  openDelay?: number;
+
   /** Close delay in ms */
   closeDelay?: number;

@@ -35,6 +38,7 @@ const defaultProps = {
   offset: 0,
   position: 'right-start',
   transitionProps: { duration: 0 },
+  openDelay: 0,
   middlewares: {
     shift: {
       // Enable crossAxis shift to keep submenu dropdown within viewport bounds when positioned horizontally
@@ -44,7 +48,7 @@ const defaultProps = {
 } satisfies Partial<MenuSubProps>;

 export function MenuSub(_props: MenuSubProps) {
-  const { children, closeDelay, ...others } = useProps('MenuSub', defaultProps, _props);
+  const { children, closeDelay, openDelay, ...others } = useProps('MenuSub', defaultProps, _props);
   const id = useId();
   const [opened, { open, close }] = useDisclosure(false);
   const ctx = useSubMenuContext();
@@ -53,7 +57,7 @@ export function MenuSub(_props: MenuSubProps) {
     open,
     close,
     closeDelay,
-    openDelay: 0,
+    openDelay,
   });

   const focusFirstItem = () =>
PATCH

echo "Patch applied successfully!"
