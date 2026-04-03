#!/usr/bin/env bash
set -euo pipefail

cd /workspace/remix

# Idempotent: skip if already applied
if grep -q 'export type InteractionSetup = (handle: Interaction)' packages/interaction/src/lib/interaction.ts 2>/dev/null; then
    echo "Patch already applied."
    exit 0
fi

git apply --whitespace=fix - <<'PATCH'
diff --git a/packages/interaction/.changes/minor.interaction-handle-parameter.md b/packages/interaction/.changes/minor.interaction-handle-parameter.md
new file mode 100644
index 00000000000..2bb9a00724b
--- /dev/null
+++ b/packages/interaction/.changes/minor.interaction-handle-parameter.md
@@ -0,0 +1,17 @@
+BREAKING CHANGE: Interaction setup functions now receive `handle` as a parameter instead of using `this` context
+
+Interaction setup functions now receive the `Interaction` handle as a parameter:
+
+```ts
+// Before
+function MyInteraction(this: Interaction) {
+  this.on(this.target, { ... })
+}
+
+// After
+function MyInteraction(handle: Interaction) {
+  handle.on(handle.target, { ... })
+}
+```
+
+This change affects all custom interactions created with `defineInteraction()`.
diff --git a/packages/interaction/README.md b/packages/interaction/README.md
index 5dd8c0192b5..ba52796582e 100644
--- a/packages/interaction/README.md
+++ b/packages/interaction/README.md
@@ -224,13 +224,13 @@ declare global {
   }
 }

-function KeydownEnter(this: Interaction) {
-  if (!(this.target instanceof HTMLElement)) return
+function KeydownEnter(handle: Interaction) {
+  if (!(handle.target instanceof HTMLElement)) return

-  this.on(this.target, {
+  handle.on(handle.target, {
     keydown(event) {
       if (event.key === 'Enter') {
-        this.target.dispatchEvent(new KeyboardEvent(keydownEnter, { key: 'Enter' }))
+        handle.target.dispatchEvent(new KeyboardEvent(keydownEnter, { key: 'Enter' }))
       }
     },
   })
diff --git a/packages/interaction/src/lib/interaction.test.ts b/packages/interaction/src/lib/interaction.test.ts
index 559a46f9bcd..549ccd838d1 100644
--- a/packages/interaction/src/lib/interaction.test.ts
+++ b/packages/interaction/src/lib/interaction.test.ts
@@ -263,10 +263,10 @@ describe('interaction', () => {
       let hostType = 'host-event'
       let myType = defineInteraction('my:type', Test)

-      function Test(this: Interaction) {
-        this.on(this.target, {
+      function Test(handle: Interaction) {
+        handle.on(handle.target, {
           [hostType]: () => {
-            this.target.dispatchEvent(new Event(myType))
+            handle.target.dispatchEvent(new Event(myType))
           },
         })
       }
@@ -304,10 +304,10 @@ describe('interaction', () => {
     let hostType = 'host-event'
     let myType = defineInteraction('my:type', Test)

-    function Test(this: Interaction) {
-      this.on(this.target, {
+    function Test(handle: Interaction) {
+      handle.on(handle.target, {
         [hostType]: () => {
-          this.target.dispatchEvent(new Event(myType))
+          handle.target.dispatchEvent(new Event(myType))
         },
       })
     }
diff --git a/packages/interaction/src/lib/interaction.ts b/packages/interaction/src/lib/interaction.ts
index bba88f1f6f0..d5963fc3051 100644
--- a/packages/interaction/src/lib/interaction.ts
+++ b/packages/interaction/src/lib/interaction.ts
@@ -37,7 +37,7 @@ export type EventListeners<target extends EventTarget = EventTarget> = Partial<{
 }>

 /**
- * Context object provided to interaction setup functions via `this`.
+ * Context object provided to interaction setup functions as a parameter.
  */
 export interface Interaction {
   /**
@@ -62,7 +62,7 @@ export interface Interaction {
 /**
  * A function that sets up an interaction on a target.
  */
-export type InteractionSetup = (this: Interaction) => void
+export type InteractionSetup = (handle: Interaction) => void

 // interactions ------------------------------------------------------------------------------------

@@ -87,11 +87,11 @@ export type InteractionSetup = (this: Interaction) => void
  * }
  *
  * // setup the interaction
- * function KeydownEnter(this: Interaction) {
- *   this.on(this.target, {
+ * function KeydownEnter(handle: Interaction) {
+ *   handle.on(handle.target, {
  *     keydown(event) {
  *       if (event.key === 'Enter') {
- *         this.target.dispatchEvent(new KeyboardEvent(keydownEnter, { key: 'Enter' }))
+ *         handle.target.dispatchEvent(new KeyboardEvent(keydownEnter, { key: 'Enter' }))
  *       }
  *     },
  *   })
@@ -504,7 +504,7 @@ function createBinding<target extends EventTarget, k extends EventType<target>>(
       // Only create AbortController for interactions that need cleanup coordination
       interactionController = new AbortController()
       let interactionContext = new InteractionHandle(target, interactionController.signal, onError)
-      interaction.call(interactionContext)
+      interaction(interactionContext)
     }
     refCounts.set(interaction, count + 1)
   }
diff --git a/packages/interaction/src/lib/interactions/form.ts b/packages/interaction/src/lib/interactions/form.ts
index 63fcff5c18d..f88816a9818 100644
--- a/packages/interaction/src/lib/interactions/form.ts
+++ b/packages/interaction/src/lib/interactions/form.ts
@@ -22,17 +22,17 @@ declare global {
   }
 }

-function FormReset(this: Interaction) {
-  if (!(this.target instanceof HTMLElement)) return
+function FormReset(handle: Interaction) {
+  if (!(handle.target instanceof HTMLElement)) return

-  let target = this.target
+  let target = handle.target
   let form =
     'form' in target && target.form instanceof HTMLFormElement
       ? target.form
       : target.closest('form')

   if (form) {
-    this.on(form, {
+    handle.on(form, {
       reset() {
         target.dispatchEvent(new Event(formReset))
       },
diff --git a/packages/interaction/src/lib/interactions/keys.ts b/packages/interaction/src/lib/interactions/keys.ts
index b970008414d..8316ac296a5 100644
--- a/packages/interaction/src/lib/interactions/keys.ts
+++ b/packages/interaction/src/lib/interactions/keys.ts
@@ -134,21 +134,21 @@ declare global {
 }

 function makeKeyInteraction(key: string) {
-  return function (this: Interaction) {
+  return function (handle: Interaction) {
     if (
       !(
-        this.target instanceof HTMLElement ||
-        this.target instanceof Document ||
-        this.target instanceof Window
+        handle.target instanceof HTMLElement ||
+        handle.target instanceof Document ||
+        handle.target instanceof Window
       )
     )
       return

-    this.on(this.target, {
+    handle.on(handle.target, {
       keydown: (event) => {
         if (event.key === key) {
           event.preventDefault()
-          this.target.dispatchEvent(
+          handle.target.dispatchEvent(
             new KeyboardEvent(`keydown:${event.key}`, {
               key: event.key,
             }),
diff --git a/packages/interaction/src/lib/interactions/popover.ts b/packages/interaction/src/lib/interactions/popover.ts
index f0848ef0ba5..0c02f97cbf5 100644
--- a/packages/interaction/src/lib/interactions/popover.ts
+++ b/packages/interaction/src/lib/interactions/popover.ts
@@ -64,17 +64,17 @@ declare global {
   }
 }

-function Popover(this: Interaction) {
-  if (!(this.target instanceof HTMLElement)) return
+function Popover(handle: Interaction) {
+  if (!(handle.target instanceof HTMLElement)) return

-  let target = this.target
+  let target = handle.target
   let popoverId = target.getAttribute('popovertarget')
   if (!popoverId) return

   let popover = target.ownerDocument.getElementById(popoverId)
   if (!(popover instanceof HTMLElement)) return

-  this.on(popover, {
+  handle.on(popover, {
     toggle(event) {
       target.dispatchEvent(
         new ToggleEvent(popoverToggle, {
diff --git a/packages/interaction/src/lib/interactions/press.ts b/packages/interaction/src/lib/interactions/press.ts
index 450bfb74788..0e096b7c694 100644
--- a/packages/interaction/src/lib/interactions/press.ts
+++ b/packages/interaction/src/lib/interactions/press.ts
@@ -105,10 +105,10 @@ export class PressEvent extends Event {
   }
 }

-function Press(this: Interaction) {
-  if (!(this.target instanceof HTMLElement)) return
+function Press(handle: Interaction) {
+  if (!(handle.target instanceof HTMLElement)) return

-  let target = this.target
+  let target = handle.target
   let isPointerDown = false
   let isKeyboardDown = false
   let longPressTimer: number = 0
@@ -128,7 +128,7 @@ function Press(this: Interaction) {
     }, 500)
   }

-  this.on(this.target, {
+  handle.on(handle.target, {
     pointerdown(event) {
       if (event.isPrimary === false) return
       if (isPointerDown) return
@@ -206,7 +206,7 @@ function Press(this: Interaction) {
     },
   })

-  this.on(target.ownerDocument, {
+  handle.on(target.ownerDocument, {
     pointerup() {
       if (isPointerDown) {
         isPointerDown = false

PATCH

echo "Patch applied successfully."
