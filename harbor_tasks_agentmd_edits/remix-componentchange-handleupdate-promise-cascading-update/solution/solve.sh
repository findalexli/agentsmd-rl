#!/usr/bin/env bash
set -euo pipefail

cd /workspace/remix

# Idempotent: skip if already applied
if grep -q 'Promise<AbortSignal>' packages/component/src/lib/component.ts 2>/dev/null; then
    echo "Patch already applied."
    exit 0
fi

git apply --whitespace=fix - <<'PATCH'
diff --git a/demos/frames/app/assets/state-search-page.tsx b/demos/frames/app/assets/state-search-page.tsx
index 1a9c1e9ff08..d7c6783a1f6 100644
--- a/demos/frames/app/assets/state-search-page.tsx
+++ b/demos/frames/app/assets/state-search-page.tsx
@@ -13,9 +13,8 @@ export let StateSearchPage = clientEntry(moduleUrl, (handle: Handle, setup?: str
           async submit(event) {
             event.preventDefault()
             query = input.value.trim()
-            handle.update(() => {
-              input.select()
-            })
+            await handle.update()
+            input.select()
           },
         }}
         css={{ display: 'flex', gap: 8, flexWrap: 'wrap', alignItems: 'center' }}
diff --git a/packages/component/.changes/minor.handle-update-promise.md b/packages/component/.changes/minor.handle-update-promise.md
new file mode 100644
index 00000000000..7ef73ebf2c2
--- /dev/null
+++ b/packages/component/.changes/minor.handle-update-promise.md
@@ -0,0 +1,24 @@
+BREAKING CHANGE: `handle.update()` now returns `Promise<AbortSignal>` instead of accepting an optional task callback.
+
+- The promise is resolved when the update is complete (DOM is updated, tasks have run)
+- The signal is aborted when the component updates again or is removed.
+
+```tsx
+let signal = await handle.update()
+// dom is updated
+// focus/scroll elements
+// do fetches, etc.
+```
+
+Note that `await handle.update()` resumes on a microtask after the flush completes, so the browser may paint before your code runs. For work that must happen synchronously during the flush (e.g. measuring elements and triggering another update without flicker), continue to use `handle.queueTask()` instead.
+
+```tsx
+handle.update()
+handle.queueTask(() => {
+  let rect = widthReferenceNode.getBoundingClientRect()
+  if (rect.width !== width) {
+    width = rect.width
+    handle.update()
+  }
+})
+```
diff --git a/packages/component/AGENTS.md b/packages/component/AGENTS.md
index c0003ce5014..004a019ddfd 100644
--- a/packages/component/AGENTS.md
+++ b/packages/component/AGENTS.md
@@ -151,9 +151,10 @@ let element = <Counter setup={10} label="Count" />
 
 The `Handle` object provides the component's interface to the framework:
 
-### `handle.update(task?)`
+### `handle.update()`
 
-Schedules a component update. Optionally accepts a task to run after the update completes.
+Schedules a component update and returns a promise that resolves with an `AbortSignal` after
+the update completes.
 
 ```tsx
 function Counter(handle: Handle) {
@@ -174,7 +175,7 @@ function Counter(handle: Handle) {
 }
 ```
 
-With a task:
+Waiting for the update:
 
 ```tsx
 function Player(handle: Handle) {
@@ -185,12 +186,10 @@ function Player(handle: Handle) {
     <button
       disabled={isPlaying}
       on={{
-        click() {
+        async click() {
           isPlaying = true
-          handle.update(() => {
-            // Task runs after update completes
-            stopButton.focus()
-          })
+          await handle.update()
+          stopButton.focus()
         },
       }}
     >
@@ -292,57 +291,31 @@ function GoodExample(handle: Handle) {
 }
 ```
 
-**Pattern: Use `handle.update(task)` when you need to show loading state before async work:**
+**Pattern: await `handle.update()` when showing loading state before async work:**
 
-The task's signal is aborted when the component re-renders. If you call `handle.update()` before your async work completes, the re-render will abort the signal you're using for the async operation. When you need to update state (like showing a loading indicator) before starting async work, move the async work into a new task via `handle.update(task)`:
+When you need to show loading UI before async work starts, set loading state, call
+`await handle.update()`, and use the returned signal for async APIs.
 
 ```tsx
-// ❌ Avoid: Calling handle.update() before async work in the same task
-function BadAsyncExample(handle: Handle) {
+function GoodAsyncExample(handle: Handle) {
   let data: string[] = []
   let loading = false
 
-  handle.queueTask(async (signal) => {
+  async function load() {
     loading = true
-    handle.update() // This triggers a re-render, which aborts signal!
-
-    let response = await fetch('/api/data', { signal }) // AbortError: signal is aborted
+    let signal = await handle.update()
+    let response = await fetch('/api/data', { signal })
+    if (signal.aborted) return
 
     data = await response.json()
     loading = false
     handle.update()
-  })
-
-  return () => <div>{loading ? 'Loading...' : data.join(', ')}</div>
-}
-
-// ✅ Prefer: Move async work into a new task via handle.update(task)
-function GoodAsyncExample(handle: Handle) {
-  let data: string[] = []
-  let loading = false
-
-  handle.queueTask(() => {
-    loading = true
-    handle.update(async (signal) => {
-      // This task gets a fresh signal that won't be aborted by the update above
-      let response = await fetch('/api/data', { signal })
-
-      data = await response.json()
-      loading = false
-      handle.update()
-    })
-  })
+  }
 
-  return () => <div>{loading ? 'Loading...' : data.join(', ')}</div>
+  return () => <button on={{ click: load }}>{loading ? 'Loading...' : 'Load data'}</button>
 }
 ```
 
-The key insight is that `handle.update(task)` queues a new task that runs after the update completes, with its own fresh signal. This allows you to:
-
-1. Update state to show loading UI
-2. Trigger a re-render with `handle.update(task)`
-3. Perform async work in the task with a signal that won't be aborted by that re-render
-
 **Signals in events and tasks are how you manage interruptions and disconnects:**
 
 Both event handlers and `queueTask` receive `AbortSignal` parameters that are automatically aborted when:
diff --git a/packages/component/README.md b/packages/component/README.md
index 6e21ba6a58d..a79d7f05b8c 100644
--- a/packages/component/README.md
+++ b/packages/component/README.md
@@ -423,7 +423,7 @@ function Component(handle: Handle) {
 
 Components receive a `Handle` as their first argument with the following API:
 
-- **`handle.update(task?)`** - Schedule an update. Optionally provide a task to run after the update.
+- **`handle.update()`** - Schedule an update and await completion to get an `AbortSignal`.
 - **`handle.queueTask(task)`** - Schedule a task to run after the next update. Useful for DOM operations that need to happen after rendering (e.g., moving focus, scrolling, measuring elements, etc.).
 - **`handle.on(target, listeners)`** - Listen to an event target with automatic cleanup when the component disconnects.
 - **`handle.signal`** - An `AbortSignal` that's aborted when the component is disconnected. Useful for cleanup.
@@ -432,9 +432,9 @@ Components receive a `Handle` as their first argument with the following API:
 - **`handle.frame`** - The component's closest frame. Call `handle.frame.reload()` to refresh the frame's server content.
 - **`handle.frames.get(name)`** - Look up named frames in the current runtime tree for adjacent frame reloads.
 
-### `handle.update(task?)`
+### `handle.update()`
 
-Schedule an update. Optionally provide a task to run after the update completes.
+Schedule an update and optionally await completion to coordinate post-update work.
 
 ```tsx
 function Counter(handle: Handle) {
@@ -455,7 +455,7 @@ function Counter(handle: Handle) {
 }
 ```
 
-You can pass a task to run after the update:
+You can await the update before doing DOM work:
 
 ```tsx
 function Player(handle: Handle) {
@@ -469,12 +469,11 @@ function Player(handle: Handle) {
         disabled={isPlaying}
         connect={(node) => (playButton = node)}
         on={{
-          click: () => {
+          async click() {
             isPlaying = true
-            handle.update(() => {
-              // Focus the enabled button after update completes
-              stopButton.focus()
-            })
+            await handle.update()
+            // Focus the enabled button after update completes
+            stopButton.focus()
           },
         }}
       >
@@ -484,12 +483,11 @@ function Player(handle: Handle) {
         disabled={!isPlaying}
         connect={(node) => (stopButton = node)}
         on={{
-          click: () => {
+          async click() {
             isPlaying = false
-            handle.update(() => {
-              // Focus the enabled button after update completes
-              playButton.focus()
-            })
+            await handle.update()
+            // Focus the enabled button after update completes
+            playButton.focus()
           },
         }}
       >
diff --git a/packages/component/demos/readme/entry.tsx b/packages/component/demos/readme/entry.tsx
index 147459a945f..dcc7c70098f 100644
--- a/packages/component/demos/readme/entry.tsx
+++ b/packages/component/demos/readme/entry.tsx
@@ -344,7 +344,7 @@ function ResizeComponent(handle: Handle) {
 }
 
 // ============================================================================
-// handle.update(task) - Player
+// handle.update() - Player
 // ============================================================================
 function Player(handle: Handle) {
   let isPlaying = false
@@ -357,12 +357,11 @@ function Player(handle: Handle) {
         disabled={isPlaying}
         connect={(node) => (playButton = node)}
         on={{
-          click: () => {
+          async click() {
             isPlaying = true
-            handle.update(() => {
-              // Focus the enabled button after update completes
-              stopButton.focus()
-            })
+            await handle.update()
+            // Focus the enabled button after update completes
+            stopButton.focus()
           },
         }}
         css={{
@@ -376,12 +375,11 @@ function Player(handle: Handle) {
         disabled={!isPlaying}
         connect={(node) => (stopButton = node)}
         on={{
-          click: () => {
+          async click() {
             isPlaying = false
-            handle.update(() => {
-              // Focus the enabled button after update completes
-              playButton.focus()
-            })
+            await handle.update()
+            // Focus the enabled button after update completes
+            playButton.focus()
           },
         }}
         css={{
@@ -641,7 +639,7 @@ function DemoApp(handle: Handle) {
         <ResizeComponent />
       </Example>
 
-      <Example title="handle.update(task) - Player">
+      <Example title="handle.update() - Player">
         <Player />
       </Example>
 
diff --git a/packages/component/docs/handle.md b/packages/component/docs/handle.md
index 2b9783ae925..a6b7ee966d2 100644
--- a/packages/component/docs/handle.md
+++ b/packages/component/docs/handle.md
@@ -2,9 +2,10 @@
 
 The `Handle` object provides the component's interface to the framework.
 
-## `handle.update(task?)`
+## `handle.update()`
 
-Schedules a component update. Optionally accepts a task to run after the update completes.
+Schedules a component update and returns a promise that resolves with an `AbortSignal` after
+the update completes.
 
 ```tsx
 function Counter(handle: Handle) {
@@ -25,7 +26,7 @@ function Counter(handle: Handle) {
 }
 ```
 
-With a task:
+Waiting for the update:
 
 ```tsx
 function Player(handle: Handle) {
@@ -36,12 +37,10 @@ function Player(handle: Handle) {
     <button
       disabled={isPlaying}
       on={{
-        click() {
+        async click() {
           isPlaying = true
-          handle.update(() => {
-            // Task runs after update completes
-            stopButton.focus()
-          })
+          await handle.update()
+          stopButton.focus()
         },
       }}
     >
@@ -145,46 +144,26 @@ function GoodExample(handle: Handle) {
 }
 ```
 
-**Don't call `handle.update()` before async work in a task:**
-
-The task's signal is aborted when the component re-renders. If you call `handle.update()` before your async work completes, the re-render will abort the signal you're using for the async operation:
+**When showing loading state before async work, await `handle.update()` and use the returned signal:**
 
 ```tsx
-// ❌ Avoid: Calling handle.update() before async work
-function BadAsyncExample(handle: Handle) {
+function AsyncExample(handle: Handle) {
   let data: string[] = []
   let loading = false
 
-  handle.queueTask(async (signal) => {
+  async function load() {
     loading = true
-    handle.update() // This triggers a re-render, which aborts signal!
-
-    let response = await fetch('/api/data', { signal }) // AbortError: signal is aborted
-    if (signal.aborted) return
-
-    data = await response.json()
-    loading = false
-    handle.update()
-  })
-
-  return () => <div>{loading ? 'Loading...' : data.join(', ')}</div>
-}
+    let signal = await handle.update()
 
-// ✅ Prefer: Set initial state in setup, only call handle.update() after async work
-function GoodAsyncExample(handle: Handle) {
-  let data: string[] = []
-  let loading = true // Start in loading state
-
-  handle.queueTask(async (signal) => {
     let response = await fetch('/api/data', { signal })
     if (signal.aborted) return
 
     data = await response.json()
     loading = false
-    handle.update() // Safe - async work is complete
-  })
+    handle.update()
+  }
 
-  return () => <div>{loading ? 'Loading...' : data.join(', ')}</div>
+  return () => <button on={{ click: load }}>{loading ? 'Loading...' : 'Load data'}</button>
 }
 ```
 
diff --git a/packages/component/src/lib/component.ts b/packages/component/src/lib/component.ts
index 9a4b56a84ab..41a4d7f1a0b 100644
--- a/packages/component/src/lib/component.ts
+++ b/packages/component/src/lib/component.ts
@@ -18,11 +18,13 @@ export interface Handle<C = Record<string, never>> {
   context: Context<C>
 
   /**
-   * Schedules an update for the component to render again.
+   * Schedules an update for the component to render again. Returns a promise
+   * that resolves with an AbortSignal after the update completes. The signal
+   * is aborted when the component re-renders or is removed.
    *
-   * @param task A render task to run after the update completes
+   * @returns A promise that resolves with an AbortSignal after the update
    */
-  update(task?: Task): void
+  update(): Promise<AbortSignal>
 
   /**
    * Schedules a task to run after the next update.
@@ -193,7 +195,7 @@ export function createComponent<C = NoContext>(config: ComponentConfig) {
   }
 
   let getContent: null | ((props: ElementProps) => RemixNode) = null
-  let scheduleUpdate: (task?: Task) => void = () => {
+  let scheduleUpdate: () => void = () => {
     throw new Error('scheduleUpdate not implemented')
   }
 
@@ -206,10 +208,11 @@ export function createComponent<C = NoContext>(config: ComponentConfig) {
 
   let handle: Handle<C> = {
     id: config.id,
-    update: (task?: Task) => {
-      if (task) taskQueue.push(task)
-      scheduleUpdate()
-    },
+    update: () =>
+      new Promise((resolve) => {
+        taskQueue.push((signal) => resolve(signal))
+        scheduleUpdate()
+      }),
     queueTask: (task: Task) => {
       taskQueue.push(task)
     },
@@ -275,11 +278,12 @@ export function createComponent<C = NoContext>(config: ComponentConfig) {
   }
 
   function remove(): (() => void)[] {
-    if (connectedCtrl) connectedCtrl.abort()
+    connectedCtrl?.abort()
+    renderCtrl?.abort()
     return dequeueTasks()
   }
 
-  function setScheduleUpdate(_scheduleUpdate: (task?: Task) => void) {
+  function setScheduleUpdate(_scheduleUpdate: () => void) {
     scheduleUpdate = _scheduleUpdate
   }
 
diff --git a/packages/component/src/lib/scheduler.ts b/packages/component/src/lib/scheduler.ts
index 2e14334f420..90b1661204c 100644
--- a/packages/component/src/lib/scheduler.ts
+++ b/packages/component/src/lib/scheduler.ts
@@ -14,6 +14,9 @@ type EmptyFn = () => void
 
 export type Scheduler = ReturnType<typeof createScheduler>
 
+// Protect against infinite cascading updates (e.g. handle.update() during render)
+const MAX_CASCADING_UPDATES = 50
+
 export function createScheduler(
   doc: Document,
   rootTarget: EventTarget,
@@ -23,6 +26,8 @@ export function createScheduler(
   let scheduled = new Map<CommittedComponentNode, ParentNode>()
   let tasks: EmptyFn[] = []
   let flushScheduled = false
+  let cascadingUpdateCount = 0
+  let resetScheduled = false
   let scheduler: {
     enqueue(vnode: CommittedComponentNode, domParent: ParentNode): void
     enqueueTasks(newTasks: EmptyFn[]): void
@@ -34,6 +39,17 @@ export function createScheduler(
     rootTarget.dispatchEvent(new ErrorEvent('error', { error }))
   }
 
+  function scheduleCounterReset() {
+    if (resetScheduled) return
+    resetScheduled = true
+    // Reset when control returns to the event loop while still allowing
+    // microtask-driven flushes in the same turn to count as cascading.
+    setTimeout(() => {
+      cascadingUpdateCount = 0
+      resetScheduled = false
+    }, 0)
+  }
+
   function flush() {
     flushScheduled = false
 
@@ -43,6 +59,15 @@ export function createScheduler(
     let hasWork = batch.size > 0 || tasks.length > 0
     if (!hasWork) return
 
+    cascadingUpdateCount++
+    scheduleCounterReset()
+
+    if (cascadingUpdateCount > MAX_CASCADING_UPDATES) {
+      let error = new Error('handle.update() infinite loop detected')
+      dispatchError(error)
+      return
+    }
+
     // Mark layout elements within updating components as pending BEFORE capture
     // This ensures we only capture/apply for elements whose components are updating
     if (batch.size > 0) {
diff --git a/packages/component/src/test/vdom.errors.test.tsx b/packages/component/src/test/vdom.errors.test.tsx
index 14df0802357..829c2be5b39 100644
--- a/packages/component/src/test/vdom.errors.test.tsx
+++ b/packages/component/src/test/vdom.errors.test.tsx
@@ -323,4 +323,75 @@ describe('vdom error handling', () => {
       expect(container.innerHTML).toBe('<button>Click</button>')
     })
   })
+
+  describe('cascading updates protection', () => {
+    it('dispatches error when handle.update() is called during render', async () => {
+      let container = document.createElement('div')
+      let root = createRoot(container)
+      let errorHandler = vi.fn()
+      root.addEventListener('error', errorHandler)
+
+      let renderCount = 0
+      let triggerUpdate: () => void
+
+      function InfiniteLoop(handle: Handle) {
+        triggerUpdate = () => {
+          handle.update()
+        }
+        return () => {
+          renderCount++
+          if (renderCount > 1) {
+            handle.update()
+          }
+          return <div>count: {renderCount}</div>
+        }
+      }
+
+      root.render(<InfiniteLoop />)
+      root.flush()
+      expect(container.innerHTML).toBe('<div>count: 1</div>')
+      expect(renderCount).toBe(1)
+
+      triggerUpdate!()
+      await new Promise((resolve) => setTimeout(resolve, 10))
+
+      expect(errorHandler).toHaveBeenCalled()
+      let error = (errorHandler.mock.calls[0][0] as ErrorEvent).error as Error
+      expect(error.message).toContain('infinite loop detected')
+      expect(renderCount).toBeLessThan(100)
+    })
+
+    it('allows legitimate multiple updates within same event loop turn', () => {
+      let container = document.createElement('div')
+      let root = createRoot(container)
+      let errorHandler = vi.fn()
+      root.addEventListener('error', errorHandler)
+
+      let count = 0
+      let update: () => void
+
+      function Counter(handle: Handle) {
+        update = () => handle.update()
+        return () => <div>count: {count}</div>
+      }
+
+      root.render(<Counter />)
+      root.flush()
+
+      count++
+      update!()
+      root.flush()
+
+      count++
+      update!()
+      root.flush()
+
+      count++
+      update!()
+      root.flush()
+
+      expect(container.innerHTML).toBe('<div>count: 3</div>')
+      expect(errorHandler).not.toHaveBeenCalled()
+    })
+  })
 })
diff --git a/packages/component/src/test/vdom.scheduler.test.tsx b/packages/component/src/test/vdom.scheduler.test.tsx
index 7a02e242d63..7e573eb7c64 100644
--- a/packages/component/src/test/vdom.scheduler.test.tsx
+++ b/packages/component/src/test/vdom.scheduler.test.tsx
@@ -69,9 +69,10 @@ describe('vnode rendering', () => {
         })
 
         capturedUpdate = () => {
-          handle.update(() => {
+          handle.queueTask(() => {
             taskCount++
           })
+          handle.update()
         }
         return () => null
       }
diff --git a/packages/component/src/test/vdom.signals.test.tsx b/packages/component/src/test/vdom.signals.test.tsx
index dfefd8f799b..9b24a3d3edb 100644
--- a/packages/component/src/test/vdom.signals.test.tsx
+++ b/packages/component/src/test/vdom.signals.test.tsx
@@ -51,5 +51,86 @@ describe('vnode rendering', () => {
       invariant(signals[0])
       expect(signals[0].aborted).toBe(true)
     })
+
+    it('aborts handle.update() signal on next update', async () => {
+      let container = document.createElement('div')
+      let root = createRoot(container)
+
+      let capturedSignal: AbortSignal | undefined
+      let capturedUpdate = () => {}
+      function App(handle: Handle) {
+        capturedUpdate = () => {
+          handle.update().then((signal) => {
+            capturedSignal = signal
+          })
+        }
+        return () => null
+      }
+
+      root.render(<App />)
+      root.flush()
+
+      capturedUpdate()
+      root.flush()
+      await Promise.resolve()
+      invariant(capturedSignal)
+      let firstSignal = capturedSignal
+      expect(firstSignal.aborted).toBe(false)
+
+      capturedUpdate()
+      root.flush()
+      expect(firstSignal.aborted).toBe(true)
+    })
+
+    it('aborts queueTask signal when component is removed', () => {
+      let container = document.createElement('div')
+      let root = createRoot(container)
+
+      let capturedSignal: AbortSignal | undefined
+      function App(handle: Handle) {
+        handle.queueTask((signal) => {
+          capturedSignal = signal
+        })
+        return () => null
+      }
+
+      root.render(<App />)
+      root.flush()
+      invariant(capturedSignal)
+      expect(capturedSignal.aborted).toBe(false)
+
+      root.render(null)
+      root.flush()
+      expect(capturedSignal.aborted).toBe(true)
+    })
+
+    it('aborts handle.update() signal when component is removed', async () => {
+      let container = document.createElement('div')
+      let root = createRoot(container)
+
+      let capturedSignal: AbortSignal | undefined
+      let capturedUpdate = () => {}
+      function App(handle: Handle) {
+        capturedUpdate = () => {
+          handle.update().then((signal) => {
+            capturedSignal = signal
+          })
+        }
+        return () => null
+      }
+
+      root.render(<App />)
+      root.flush()
+
+      capturedUpdate()
+      root.flush()
+      await Promise.resolve()
+      invariant(capturedSignal)
+      expect(capturedSignal.aborted).toBe(false)
+
+      root.render(null)
+      root.flush()
+      expect(capturedSignal.aborted).toBe(true)
+    })
   })
 })
diff --git a/packages/component/src/test/vdom.tasks.test.tsx b/packages/component/src/test/vdom.tasks.test.tsx
index 7ccea38ca61..aad6d4acb47 100644
--- a/packages/component/src/test/vdom.tasks.test.tsx
+++ b/packages/component/src/test/vdom.tasks.test.tsx
@@ -30,16 +30,16 @@ describe('vnode rendering', () => {
     expect(taskRan).toBe(true)
   })
 
-  it('runs task provided to render', () => {
+  it('handle.update() returns a promise that resolves with a signal', async () => {
     let container = document.createElement('div')
     let root = createRoot(container)
 
-    let taskRan = false
+    let capturedSignal: AbortSignal | undefined
     let capturedUpdate = () => {}
     function App(handle: Handle) {
       capturedUpdate = () => {
-        handle.update(() => {
-          taskRan = true
+        handle.update().then((signal) => {
+          capturedSignal = signal
         })
       }
 
@@ -48,11 +48,13 @@ describe('vnode rendering', () => {
 
     root.render(<App />)
     root.flush()
-    expect(taskRan).toBe(false)
+    expect(capturedSignal).toBe(undefined)
 
     capturedUpdate()
-    expect(taskRan).toBe(false)
+    expect(capturedSignal).toBe(undefined)
     root.flush()
-    expect(taskRan).toBe(true)
+    await Promise.resolve()
+    expect(capturedSignal).toBeInstanceOf(AbortSignal)
+    expect(capturedSignal?.aborted).toBe(false)
   })
 })

PATCH

echo "Patch applied successfully."
