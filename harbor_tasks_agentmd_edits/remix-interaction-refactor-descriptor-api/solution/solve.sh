#!/usr/bin/env bash
set -euo pipefail

cd /workspace/remix

# Idempotent: skip if already applied
if grep -q 'class InteractionHandle implements Interaction' packages/interaction/src/lib/interaction.ts 2>/dev/null; then
    echo "Patch already applied."
    exit 0
fi

git apply --whitespace=fix - <<'PATCH'
diff --git a/packages/interaction/CHANGELOG.md b/packages/interaction/CHANGELOG.md
index b5b128e8d89..4467d8b31ab 100644
--- a/packages/interaction/CHANGELOG.md
+++ b/packages/interaction/CHANGELOG.md
@@ -2,6 +2,77 @@
 
 This is the changelog for [`interaction`](https://github.com/remix-run/remix/tree/main/packages/interaction). It follows [semantic versioning](https://semver.org/).
 
+## Unreleased
+
+- BREAKING CHANGE: Interaction API refactor - interactions now use `this` context with `this.on()`, `this.target`, `this.signal`, and `this.raise`
+
+  Interactions are now functions that receive an `Interaction` context via `this`:
+
+  ```ts
+  // Before
+  function MyInteraction(target: EventTarget, signal: AbortSignal) {
+    createContainer(target, { signal }).set({ ... })
+  }
+
+  // After
+  function MyInteraction(this: Interaction) {
+    this.on(this.target, { ... })
+    // or for different targets
+    this.on(this.target.ownerDocument, { ... })
+  }
+  ```
+
+  The `Interaction` context provides:
+
+  - `this.target` - The target element
+  - `this.signal` - Abort signal for cleanup
+  - `this.raise` - Error handler (renamed from `onError`)
+  - `this.on(target, listeners)` - Create a container with automatic signal/error propagation
+
+- BREAKING CHANGE: Simplify descriptor API - descriptors now extend `AddEventListenerOptions` directly
+
+  Removed `capture()` and `listenWith()` helper functions. Consumers now provide options inline using descriptor objects:
+
+  ```tsx
+  // removed
+  capture((event) => {})
+  listenWith({ once: true }, (event) => {})
+
+  // new API
+  {
+    capture: true,
+    listener(event) {}
+  }
+  {
+    once: true,
+    listener(event) {}
+  }
+  ```
+
+- BREAKING CHANGE: Remove `on` signal overload, just use containers directly
+
+  ```tsx
+  // removed
+  on(target, signal, listeners)
+
+  // on is just a shortcut now
+  let dispose = on(target, listeners)
+  dispose()
+
+  // use containers for signal cleanup
+  let container = createContainer(target, { signal })
+  ```
+
+- Added `onError` handler so containers can handle listener errors in one place (avoids Remix Component needing to wrap EventListener interfaces to raise to `<Catch>`)
+
+  ```tsx
+  createContainer(target, {
+    onError(error) {
+      // handle error
+    },
+  })
+  ```
+
 ## v0.1.0 (2025-11-03)
 
 This is the initial release of the `@remix-run/interaction` package.
diff --git a/packages/interaction/README.md b/packages/interaction/README.md
index 099c956393e..81b4f50176b 100644
--- a/packages/interaction/README.md
+++ b/packages/interaction/README.md
@@ -36,19 +36,25 @@ on(inputElement, {
 Listeners can be arrays. They run in order and preserve normal DOM semantics (including `stopImmediatePropagation`).
 
 ```ts
-import { on, capture, listenWith } from '@remix-run/interaction'
+import { on } from '@remix-run/interaction'
 
 on(inputElement, {
   input: [
     (event) => {
       console.log('first')
     },
-    capture((event) => {
-      // capture phase
-    }),
-    listenWith({ once: true }, (event) => {
-      console.log('only once')
-    }),
+    {
+      capture: true,
+      listener(event) {
+        // capture phase
+      },
+    },
+    {
+      once: true,
+      listener(event) {
+        console.log('only once')
+      },
+    },
   ],
 })
 ```
@@ -112,21 +118,27 @@ on(inputElement, {
 All DOM [`AddEventListenerOptions`](https://developer.mozilla.org/en-US/docs/Web/API/EventTarget/addEventListener#options) are supported via descriptors:
 
 ```ts
-import { on, listenWith, capture } from '@remix-run/interaction'
+import { on } from '@remix-run/interaction'
 
 on(button, {
-  click: capture((event) => {
-    console.log('capture phase')
-  }),
-  focus: listenWith({ once: true }, (event) => {
-    console.log('focused once')
-  }),
+  click: {
+    capture: true,
+    listener(event) {
+      console.log('capture phase')
+    },
+  },
+  focus: {
+    once: true,
+    listener(event) {
+      console.log('focused once')
+    },
+  },
 })
 ```
 
 ### Updating listeners efficiently
 
-Use `createContainer(target, signal?)` when you need to update listeners in place (e.g., in a component system). The container diffs and updates existing bindings without unnecessary `removeEventListener`/`addEventListener` churn.
+Use `createContainer` when you need to update listeners in place (e.g., in a component system). The container diffs and updates existing bindings without unnecessary `removeEventListener`/`addEventListener` churn.
 
 ```ts
 import { createContainer } from '@remix-run/interaction'
@@ -167,15 +179,18 @@ import { on, createContainer } from '@remix-run/interaction'
 let dispose = on(button, { click: () => {} })
 dispose()
 
-// Using an external AbortSignal
-let controller = new AbortController()
-on(button, controller.signal, { click: () => {} })
-controller.abort() // removes all listeners added via that call
-
 // Containers
 let container = createContainer(window)
 container.set({ resize: () => {} })
 container.dispose()
+
+// Use a signal
+let eventsController = new AbortController()
+let container = createContainer(window, {
+  signal: eventsController.signal,
+})
+container.set({ resize: () => {} })
+eventsController.abort()
 ```
 
 ### Stop propagation semantics
@@ -200,7 +215,7 @@ on(button, {
 Define semantic interactions that can dispatch custom events and be reused declaratively.
 
 ```ts
-import { defineInteraction, on } from '@remix-run/interaction'
+import { defineInteraction, on, type Interaction } from '@remix-run/interaction'
 
 // Provide type safety for consumers
 declare global {
@@ -209,13 +224,13 @@ declare global {
   }
 }
 
-function KeydownEnter(target: EventTarget, signal: AbortSignal) {
-  if (!(target instanceof HTMLElement)) return
+function KeydownEnter(this: Interaction) {
+  if (!(this.target instanceof HTMLElement)) return
 
-  on(target, signal, {
+  this.on(this.target, {
     keydown(event) {
       if (event.key === 'Enter') {
-        target.dispatchEvent(new KeyboardEvent(keydownEnter, { key: 'Enter' }))
+        this.target.dispatchEvent(new KeyboardEvent(keydownEnter, { key: 'Enter' }))
       }
     },
   })
diff --git a/packages/interaction/src/index.ts b/packages/interaction/src/index.ts
index 08a6ef68848..e890cf35792 100644
--- a/packages/interaction/src/index.ts
+++ b/packages/interaction/src/index.ts
@@ -1,12 +1,12 @@
 export {
+  type ContainerOptions,
   type Dispatched,
   type EventListeners,
   type EventsContainer,
+  type Interaction,
   type InteractionSetup,
   type TypedEventTarget,
-  capture,
   createContainer,
   defineInteraction,
-  listenWith,
   on,
 } from './lib/interaction.ts'
diff --git a/packages/interaction/src/lib/interaction.test.ts b/packages/interaction/src/lib/interaction.test.ts
index 40d4db18860..ec08a324c23 100644
--- a/packages/interaction/src/lib/interaction.test.ts
+++ b/packages/interaction/src/lib/interaction.test.ts
@@ -1,14 +1,13 @@
 import { describe, it, expect, vi } from 'vitest'
 
 import {
-  capture,
   createContainer,
   defineInteraction,
-  listenWith,
   on,
   TypedEventTarget,
   type Dispatched,
   type EventListeners,
+  type Interaction,
 } from './interaction.ts'
 import type { Assert, Equal } from './test/utils.ts'
 
@@ -55,7 +54,7 @@ describe('interaction', () => {
       expect(listener1).toHaveBeenCalledTimes(1)
       expect(spy).toHaveBeenCalledTimes(0)
 
-      container.set({ test: listenWith({ capture: true }, listener2) })
+      container.set({ test: { capture: true, listener: listener2 } })
       target.dispatchEvent(new Event('test'))
       expect(listener1).toHaveBeenCalledTimes(1)
       expect(listener2).toHaveBeenCalledTimes(1)
@@ -103,13 +102,13 @@ describe('interaction', () => {
       expect(() => container.set({ test: () => {} })).toThrow('Container has been disposed')
     })
 
-    describe('listenWith', () => {
-      it('provides options with listenWith', () => {
+    describe('descriptors', () => {
+      it('provides options with descriptors', () => {
         let target = new EventTarget()
         let listener = vi.fn()
 
         createContainer(target).set({
-          test: listenWith({ once: true }, listener),
+          test: { once: true, listener },
         })
 
         target.dispatchEvent(new Event('test'))
@@ -117,9 +116,7 @@ describe('interaction', () => {
         target.dispatchEvent(new Event('test'))
         expect(listener).toHaveBeenCalledTimes(1)
       })
-    })
 
-    describe('capture', () => {
       it('captures events', () => {
         let button = document.createElement('button')
         document.body.appendChild(button)
@@ -128,10 +125,13 @@ describe('interaction', () => {
         let bubbled = false
 
         createContainer(document.body).set({
-          click: capture((event) => {
-            event.stopPropagation()
-            captured = true
-          }),
+          click: {
+            capture: true,
+            listener(event) {
+              event.stopPropagation()
+              captured = true
+            },
+          },
         })
 
         // add event to the target to test that it's not captured and prove its
@@ -147,6 +147,41 @@ describe('interaction', () => {
       })
     })
 
+    describe('error handling', () => {
+      it('calls onError when a listener throws synchronously', () => {
+        let target = new EventTarget()
+        let mock = vi.fn()
+        let error = new Error('test')
+        let container = createContainer(target, { onError: mock })
+        container.set({
+          test: () => {
+            throw error
+          },
+        })
+        target.dispatchEvent(new Event('test'))
+        expect(mock).toHaveBeenCalledWith(error)
+      })
+    })
+
+    it('calls onError when a listener throws asynchronously', async () => {
+      let target = new EventTarget()
+      let mock = vi.fn()
+      let error = new Error('test')
+      createContainer(target, { onError: mock }).set({
+        async test() {
+          // ensure the error is thrown asynchronously (next microtask)
+          await Promise.resolve()
+          throw error
+        },
+      })
+      target.dispatchEvent(new Event('test'))
+      // let the listener's awaited microtask run and reject
+      await Promise.resolve()
+      // run the container's result.catch(onError) handler
+      await Promise.resolve()
+      expect(mock).toHaveBeenCalledWith(error)
+    })
+
     describe('types', () => {
       it('provides literal event and target types to listeners', () => {
         let button = document.createElement('button')
@@ -201,18 +236,6 @@ describe('interaction', () => {
           test: () => {},
         })
       })
-
-      it('accepts optional abort signal', () => {
-        let button = document.createElement('button')
-        let controller = new AbortController()
-        on(button, controller.signal, {
-          pointerdown: (event) => {
-            type T = Assert<Equal<typeof event, Dispatched<PointerEvent, HTMLButtonElement>>>
-          },
-          // @ts-expect-error - unknown event type
-          test: () => {},
-        })
-      })
     })
   })
 
@@ -221,10 +244,10 @@ describe('interaction', () => {
       let hostType = 'host-event'
       let myType = defineInteraction('my:type', Test)
 
-      function Test(target: EventTarget, signal: AbortSignal) {
-        on(target, signal, {
+      function Test(this: Interaction) {
+        this.on(this.target, {
           [hostType]: () => {
-            target.dispatchEvent(new Event(myType))
+            this.target.dispatchEvent(new Event(myType))
           },
         })
       }
@@ -262,10 +285,10 @@ describe('interaction', () => {
     let hostType = 'host-event'
     let myType = defineInteraction('my:type', Test)
 
-    function Test(target: EventTarget, signal: AbortSignal) {
-      on(target, signal, {
+    function Test(this: Interaction) {
+      this.on(this.target, {
         [hostType]: () => {
-          target.dispatchEvent(new Event(myType))
+          this.target.dispatchEvent(new Event(myType))
         },
       })
     }
diff --git a/packages/interaction/src/lib/interaction.ts b/packages/interaction/src/lib/interaction.ts
index 85bf5084064..8b0aac55b2f 100644
--- a/packages/interaction/src/lib/interaction.ts
+++ b/packages/interaction/src/lib/interaction.ts
@@ -25,7 +25,7 @@ export type EventsContainer<target extends EventTarget> = {
  *   },
  *   keydown: [
  *     (event) => {},
- *     capture((event) => {}),
+ *     { capture: true, listener(event) {} },
  *   ],
  * }
  * ```
@@ -36,10 +36,33 @@ export type EventListeners<target extends EventTarget = EventTarget> = Partial<{
     | Array<ListenerOrDescriptor<ListenerFor<target, k>>>
 }>
 
+/**
+ * Context object provided to interaction setup functions via `this`.
+ */
+export interface Interaction {
+  /**
+   * The target element this interaction is being set up on.
+   */
+  readonly target: EventTarget
+  /**
+   * The abort signal that will dispose this interaction when aborted.
+   */
+  readonly signal: AbortSignal
+  /**
+   * Error handler from the parent container.
+   */
+  readonly raise: (error: unknown) => void
+  /**
+   * Create a container on a target with listeners. Automatically passes
+   * through signal and onError from the parent container.
+   */
+  on<target extends EventTarget>(target: target, listeners: EventListeners<target>): void
+}
+
 /**
  * A function that sets up an interaction on a target.
  */
-export type InteractionSetup = (target: EventTarget, signal: AbortSignal) => void
+export type InteractionSetup = (this: Interaction) => void
 
 // interactions ------------------------------------------------------------------------------------
 
@@ -64,11 +87,11 @@ export type InteractionSetup = (target: EventTarget, signal: AbortSignal) => voi
  * }
  *
  * // setup the interaction
- * function KeydownEnter(target, signal) {
- *   on(target, signal, {
+ * function KeydownEnter(this: Interaction) {
+ *   this.on(this.target, {
  *     keydown(event) {
  *       if (event.key === 'Enter') {
- *         target.dispatchEvent(new KeyboardEvent(keydownEnter, { key: 'Enter' }))
+ *         this.target.dispatchEvent(new KeyboardEvent(keydownEnter, { key: 'Enter' }))
  *       }
  *     },
  *   })
@@ -89,6 +112,20 @@ export function defineInteraction<type extends string>(type: type, interaction:
 
 // container ---------------------------------------------------------------------------------------
 
+/**
+ * Options for creating an event container.
+ */
+export type ContainerOptions = {
+  /**
+   * An optional abort signal to dispose the container when the signal is aborted
+   */
+  signal?: AbortSignal
+  /**
+   * An optional error handler called when a listener throws an error
+   */
+  onError?: (error: unknown) => void
+}
+
 /**
  * ### Description
  *
@@ -107,6 +144,16 @@ export function defineInteraction<type extends string>(type: type, interaction:
  *   },
  * })
  * ```
+ *
+ * ### With error handling:
+ *
+ * ```ts
+ * let container = createContainer(button, {
+ *   onError(error) {
+ *     console.error('Listener error:', error)
+ *   },
+ * })
+ * ```
  */
 export function createContainer<target extends EventTarget>(
   /**
@@ -116,19 +163,25 @@ export function createContainer<target extends EventTarget>(
   target: target,
 
   /**
-   * An optional abort signal to dispose the container when the signal is aborted
+   * Optional configuration for the container
    *
    * @example
    * ```ts
    * let controller = new AbortController()
-   * let container = createContainer(target, controller.signal)
+   * let container = createContainer(target, {
+   *   signal: controller.signal,
+   *   onError(error) {
+   *     console.error(error)
+   *   },
+   * })
    * // will remove all listeners and dispose the container
    * controller.abort()
    * ```
    */
-  signal?: AbortSignal,
+  options?: ContainerOptions,
 ): EventsContainer<target> {
   let controller = new AbortController()
+  let { signal, onError = defaultOnError } = options ?? {}
 
   if (signal) {
     signal.addEventListener('abort', () => controller.abort(), { once: true })
@@ -159,9 +212,10 @@ export function createContainer<target extends EventTarget>(
 
           let existing = bindings[type]
           if (!existing) {
-            bindings[type] = descriptors.map((d) =>
-              createBinding(target, type, d.listener, d.options, controller.signal),
-            )
+            bindings[type] = descriptors.map((d) => {
+              let { listener, ...options } = d
+              return createBinding(target, type, listener, options, controller.signal, onError)
+            })
             return
           }
 
@@ -170,10 +224,11 @@ export function createContainer<target extends EventTarget>(
           for (let i = 0; i < min; i++) {
             let d = descriptors[i]
             let b = existing[i]
-            if (optionsChanged(d.options, b.options)) {
-              b.rebind(d.listener, d.options)
+            let { listener, ...options } = d
+            if (optionsChanged(options, b.options)) {
+              b.rebind(listener, options)
             } else {
-              b.setListener(d.listener)
+              b.setListener(listener)
             }
           }
 
@@ -181,7 +236,10 @@ export function createContainer<target extends EventTarget>(
           if (descriptors.length > existing.length) {
             for (let i = existing.length; i < descriptors.length; i++) {
               let d = descriptors[i]
-              existing.push(createBinding(target, type, d.listener, d.options, controller.signal))
+              let { listener, ...options } = d
+              existing.push(
+                createBinding(target, type, listener, options, controller.signal, onError),
+              )
             }
           }
 
@@ -205,16 +263,14 @@ export function createContainer<target extends EventTarget>(
 /**
  * ### Description
  *
- * Add event listeners with async reentry protection and semantic Interactions.
- *
- * ### Basic usage:
+ * Add event listeners with async reentry protection and semantic Interactions. Shorthand for `createContainer` without options.
  *
  * ```ts
  * import { on } from "@remix-run/interaction"
  * import { longPress } from "@remix-run/interaction/press"
  *
  * let button = document.createElement('button')
- * on(button, {
+ * let dispose = on(button, {
  *   click(event, signal) {
  *     console.log('clicked')
  *   },
@@ -222,75 +278,22 @@ export function createContainer<target extends EventTarget>(
  *     console.log('long pressed')
  *   },
  * })
- * ```
- *
- * ### With abort signal to dispose the container:
- *
- * ```ts
- * let controller = new AbortController()
- * on(button, controller.signal, {
- *   click(event, signal) {
- *     console.log('clicked')
- *   },
- * })
- * // will remove all listeners and dispose the container
- * controller.abort()
- * ```
- *
- * ### With array of listeners on a type:
  *
- * ```ts
- * on(button, {
- *   click: [
- *     (event, signal) => {
- *       if (someCondition) {
- *         event.stopImmediatePropagation()
- *       }
- *       console.log('called')
- *     },
- *     (event, signal) => {
- *       console.log('not called')
- *     },
- *   ],
- * })
+ * // later
+ * dispose()
  * ```
  */
 export function on<target extends EventTarget>(
   target: target,
-  signal: AbortSignal,
   listeners: EventListeners<target>,
-): () => void
-export function on<target extends EventTarget>(
-  target: target,
-  listeners: EventListeners<target>,
-): () => void
-export function on(
-  target: EventTarget,
-  signalOrListeners: AbortSignal | EventListeners,
-  listeners?: EventListeners,
 ): () => void {
-  if (!(signalOrListeners instanceof AbortSignal)) {
-    let container = createContainer(target)
-    container.set(signalOrListeners)
-    return container.dispose
-  } else if (listeners) {
-    let container = createContainer(target, signalOrListeners)
-    container.set(listeners)
-    return container.dispose
-  }
-  throw new Error('Invalid arguments')
+  let container = createContainer(target)
+  container.set(listeners)
+  return container.dispose
 }
 
 // descriptors -------------------------------------------------------------------------------------
 
-export function listenWith<L>(options: AddEventListenerOptions, listener: L): Descriptor<L> {
-  return { options, listener }
-}
-
-export function capture<L>(listener: L): Descriptor<L> {
-  return listenWith({ capture: true }, listener)
-}
-
 // TypedEventTarget --------------------------------------------------------------------------------
 
 export class TypedEventTarget<eventMap> extends EventTarget {
@@ -327,10 +330,33 @@ type TypedEventListener<eventMap> = {
 let interactions = new Map<string, InteractionSetup>()
 let initializedTargets = new WeakMap<EventTarget, Map<Function, number>>()
 
+function defaultOnError(error: unknown) {
+  throw error
+}
+
+class InteractionHandle implements Interaction {
+  readonly target: EventTarget
+  readonly signal: AbortSignal
+  readonly raise: (error: unknown) => void
+
+  constructor(target: EventTarget, signal: AbortSignal, onError: (error: unknown) => void) {
+    this.target = target
+    this.signal = signal
+    this.raise = onError
+  }
+
+  on<target extends EventTarget>(target: target, listeners: EventListeners<target>): void {
+    let container = createContainer(target, {
+      signal: this.signal,
+      onError: this.raise,
+    })
+    container.set(listeners)
+  }
+}
+
 type ListenerOrDescriptor<Listener> = Listener | Descriptor<Listener>
 
-interface Descriptor<L> {
-  options: AddEventListenerOptions
+interface Descriptor<L> extends AddEventListenerOptions {
   listener: L
 }
 
@@ -338,15 +364,13 @@ function normalizeDescriptors<Listener>(
   raw: ListenerOrDescriptor<Listener> | ListenerOrDescriptor<Listener>[],
 ): Descriptor<Listener>[] {
   if (Array.isArray(raw)) {
-    return raw.map((item) =>
-      isDescriptor<Listener>(item) ? item : { listener: item, options: {} },
-    )
+    return raw.map((item) => (isDescriptor<Listener>(item) ? item : { listener: item }))
   }
-  return [isDescriptor<Listener>(raw) ? raw : { listener: raw, options: {} }]
+  return [isDescriptor<Listener>(raw) ? raw : { listener: raw }]
 }
 
 function isDescriptor<L>(value: any): value is Descriptor<L> {
-  return typeof value === 'object' && value !== null && 'options' in value && 'listener' in value
+  return typeof value === 'object' && value !== null && 'listener' in value
 }
 
 type Binding<L> = {
@@ -375,6 +399,7 @@ function createBinding<target extends EventTarget, k extends EventType<target>>(
   listener: ListenerFor<target, k>,
   options: AddEventListenerOptions,
   containerSignal: AbortSignal,
+  onError: (error: unknown) => void,
 ): Binding<ListenerFor<target, k>> {
   let reentry = new AbortController()
   let disposed = false
@@ -386,8 +411,15 @@ function createBinding<target extends EventTarget, k extends EventType<target>>(
 
   let wrappedListener = (event: Event) => {
     abort()
-    // TODO: figure out if we can remove this cast
-    listener(event as any, reentry.signal)
+    try {
+      // TODO: figure out if we can remove this cast
+      let result = listener(event as any, reentry.signal)
+      if (result instanceof Promise) {
+        result.catch(onError)
+      }
+    } catch (error) {
+      onError(error)
+    }
   }
 
   function bind() {
@@ -437,7 +469,8 @@ function createBinding<target extends EventTarget, k extends EventType<target>>(
     }
     let count = refCounts.get(interaction) ?? 0
     if (count === 0) {
-      interaction(target, containerSignal)
+      let interactionContext = new InteractionHandle(target, containerSignal, onError)
+      interaction.call(interactionContext)
     }
     refCounts.set(interaction, count + 1)
   }
diff --git a/packages/interaction/src/lib/interactions/form.ts b/packages/interaction/src/lib/interactions/form.ts
index 4ec42d28215..63fcff5c18d 100644
--- a/packages/interaction/src/lib/interactions/form.ts
+++ b/packages/interaction/src/lib/interactions/form.ts
@@ -1,4 +1,4 @@
-import { defineInteraction } from '../interaction.ts'
+import { defineInteraction, type Interaction } from '../interaction.ts'
 
 /**
  * Called when the target's form is reset. Useful for resetting custom component
@@ -22,15 +22,20 @@ declare global {
   }
 }
 
-function FormReset(target: EventTarget, signal: AbortSignal) {
-  if (!(target instanceof HTMLElement)) return
+function FormReset(this: Interaction) {
+  if (!(this.target instanceof HTMLElement)) return
 
+  let target = this.target
   let form =
     'form' in target && target.form instanceof HTMLFormElement
       ? target.form
       : target.closest('form')
 
   if (form) {
-    form.addEventListener('reset', () => target.dispatchEvent(new Event(formReset)), { signal })
+    this.on(form, {
+      reset() {
+        target.dispatchEvent(new Event(formReset))
+      },
+    })
   }
 }
diff --git a/packages/interaction/src/lib/interactions/keys.ts b/packages/interaction/src/lib/interactions/keys.ts
index 8e294507e1d..21d7e34ed34 100644
--- a/packages/interaction/src/lib/interactions/keys.ts
+++ b/packages/interaction/src/lib/interactions/keys.ts
@@ -1,4 +1,4 @@
-import { defineInteraction, on } from '../interaction.ts'
+import { defineInteraction, type Interaction } from '../interaction.ts'
 
 /**
  * Binds the escape key to an element and automatically prevents the default
@@ -116,6 +116,40 @@ declare global {
     [pageDown]: KeyboardEvent
     [tab]: KeyboardEvent
   }
+
+  interface WindowEventMap {
+    [escape]: KeyboardEvent
+    [enter]: KeyboardEvent
+    [space]: KeyboardEvent
+    [backspace]: KeyboardEvent
+    [del]: KeyboardEvent
+    [arrowLeft]: KeyboardEvent
+    [arrowRight]: KeyboardEvent
+    [arrowUp]: KeyboardEvent
+    [arrowDown]: KeyboardEvent
+    [home]: KeyboardEvent
+    [end]: KeyboardEvent
+    [pageUp]: KeyboardEvent
+    [pageDown]: KeyboardEvent
+    [tab]: KeyboardEvent
+  }
+
+  interface DocumentEventMap {
+    [escape]: KeyboardEvent
+    [enter]: KeyboardEvent
+    [space]: KeyboardEvent
+    [backspace]: KeyboardEvent
+    [del]: KeyboardEvent
+    [arrowLeft]: KeyboardEvent
+    [arrowRight]: KeyboardEvent
+    [arrowUp]: KeyboardEvent
+    [arrowDown]: KeyboardEvent
+    [home]: KeyboardEvent
+    [end]: KeyboardEvent
+    [pageUp]: KeyboardEvent
+    [pageDown]: KeyboardEvent
+    [tab]: KeyboardEvent
+  }
 }
 
 const keys = [
@@ -135,11 +169,18 @@ const keys = [
   'Tab',
 ]
 
-function Keys(target: EventTarget, signal: AbortSignal) {
-  if (!(target instanceof HTMLElement || target instanceof Document || target instanceof Window))
+function Keys(this: Interaction) {
+  if (
+    !(
+      this.target instanceof HTMLElement ||
+      this.target instanceof Document ||
+      this.target instanceof Window
+    )
+  )
     return
 
-  on(target, signal, {
+  let target = this.target
+  this.on(this.target, {
     keydown(event) {
       if (!keys.includes(event.key)) return
       event.preventDefault()
diff --git a/packages/interaction/src/lib/interactions/popover.ts b/packages/interaction/src/lib/interactions/popover.ts
index 5818aa9cb30..82b509b38b8 100644
--- a/packages/interaction/src/lib/interactions/popover.ts
+++ b/packages/interaction/src/lib/interactions/popover.ts
@@ -1,4 +1,4 @@
-import { defineInteraction, on } from '../interaction'
+import { defineInteraction, type Interaction } from '../interaction'
 
 /**
  * ### Description
@@ -64,16 +64,17 @@ declare global {
   }
 }
 
-function Popover(target: EventTarget, signal: AbortSignal) {
-  if (!(target instanceof HTMLElement)) return
+function Popover(this: Interaction) {
+  if (!(this.target instanceof HTMLElement)) return
 
+  let target = this.target
   let popoverId = target.getAttribute('popovertarget')
   if (!popoverId) return
 
   let popover = target.ownerDocument.getElementById(popoverId)
   if (!(popover instanceof HTMLElement)) return
 
-  on(popover, signal, {
+  this.on(popover, {
     toggle(event) {
       target.dispatchEvent(
         new ToggleEvent(popoverToggle, {
diff --git a/packages/interaction/src/lib/interactions/press.ts b/packages/interaction/src/lib/interactions/press.ts
index 72fff3e6d8b..450bfb74788 100644
--- a/packages/interaction/src/lib/interactions/press.ts
+++ b/packages/interaction/src/lib/interactions/press.ts
@@ -1,4 +1,4 @@
-import { defineInteraction, on } from '../interaction.ts'
+import { defineInteraction, type Interaction } from '../interaction.ts'
 
 /**
  * Normalized press events for pointer and keyboard input. A press is dispatched
@@ -105,9 +105,10 @@ export class PressEvent extends Event {
   }
 }
 
-function Press(target: EventTarget, signal: AbortSignal) {
-  if (!(target instanceof HTMLElement)) return
+function Press(this: Interaction) {
+  if (!(this.target instanceof HTMLElement)) return
 
+  let target = this.target
   let isPointerDown = false
   let isKeyboardDown = false
   let longPressTimer: number = 0
@@ -127,7 +128,7 @@ function Press(target: EventTarget, signal: AbortSignal) {
     }, 500)
   }
 
-  on(target, signal, {
+  this.on(this.target, {
     pointerdown(event) {
       if (event.isPrimary === false) return
       if (isPointerDown) return
@@ -205,7 +206,7 @@ function Press(target: EventTarget, signal: AbortSignal) {
     },
   })
 
-  on(target.ownerDocument, signal, {
+  this.on(target.ownerDocument, {
     pointerup() {
       if (isPointerDown) {
         isPointerDown = false
diff --git a/packages/interaction/tsconfig.json b/packages/interaction/tsconfig.json
index b26ac4889ed..860c46dcf6f 100644
--- a/packages/interaction/tsconfig.json
+++ b/packages/interaction/tsconfig.json
@@ -1,7 +1,7 @@
 {
   "compilerOptions": {
     "strict": true,
-    "lib": ["ES2020", "DOM", "DOM.Iterable"],
+    "lib": ["ES2024", "DOM", "DOM.Iterable"],
     "module": "ES2022",
     "moduleResolution": "Bundler",
     "target": "ESNext",
PATCH

echo "Patch applied successfully."
