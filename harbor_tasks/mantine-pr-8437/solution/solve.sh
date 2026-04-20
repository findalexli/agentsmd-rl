#!/bin/bash
set -e
cd /workspace/mantine_repo

# Apply the gold patch
git apply --verbose <<'PATCH'
diff --git a/packages/@docs/demos/src/demos/core/Menu/Menu.demo.sub.tsx b/packages/@docs/demos/src/demos/core/Menu/Menu.demo.sub.tsx
index 32d81637f23..b9c7201b9d4 100644
--- a/packages/@docs/demos/src/demos/core/Menu/Menu.demo.sub.tsx
+++ b/packages/@docs/demos/src/demos/core/Menu/Menu.demo.sub.tsx
@@ -14,7 +14,7 @@ function Demo() {
       <Menu.Dropdown>
         <Menu.Item>Dashboard</Menu.Item>

-        <Menu.Sub>
+        <Menu.Sub openDelay={120} closeDelay={150}>
           <Menu.Sub.Target>
             <Menu.Sub.Item>Products</Menu.Sub.Item>
           </Menu.Sub.Target>
@@ -67,7 +67,7 @@ function Demo() {
       <Menu.Dropdown>
         <Menu.Item>Dashboard</Menu.Item>

-        <Menu.Sub>
+        <Menu.Sub openDelay={120} closeDelay={150}>
           <Menu.Sub.Target>
             <Menu.Sub.Item>Products</Menu.Sub.Item>
           </Menu.Sub.Target>
diff --git a/packages/@mantine/core/src/components/Menu/Menu.story.tsx b/packages/@mantine/core/src/components/Menu/Menu.story.tsx
index 7627d1b9599..83659ba6b3c 100644
--- a/packages/@mantine/core/src/components/Menu/Menu.story.tsx
+++ b/packages/@mantine/core/src/components/Menu/Menu.story.tsx
@@ -219,7 +219,7 @@ export function WithSubMenu() {
         <Menu.Dropdown>
           <Menu.Item>Item 1</Menu.Item>
           <Menu.Item>Item 2</Menu.Item>
-          <Menu.Sub closeDelay={100}>
+          <Menu.Sub openDelay={1200} closeDelay={100}>
             <Menu.Sub.Target>
               <Menu.Sub.Item>Sub Menu item</Menu.Sub.Item>
             </Menu.Sub.Target>
@@ -227,7 +227,7 @@ export function WithSubMenu() {
             <Menu.Sub.Dropdown>
               <Menu.Item closeMenuOnClick={false}>Sub 1</Menu.Item>
               <Menu.Item closeMenuOnClick={false}>Sub 2</Menu.Item>
-              <Menu.Sub closeDelay={100}>
+              <Menu.Sub openDelay={120} closeDelay={100}>
                 <Menu.Sub.Target>
                   <Menu.Sub.Item>Sub Menu item</Menu.Sub.Item>
                 </Menu.Sub.Target>
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
