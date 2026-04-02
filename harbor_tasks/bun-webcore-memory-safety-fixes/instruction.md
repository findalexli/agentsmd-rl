# WebCore Memory Safety Bugs

Bun's WebCore code (forked from WebKit) has four memory safety issues in `src/bun.js/bindings/webcore/`. Each one is a confirmed upstream WebKit bug that was fixed in WebKit but not yet backported to Bun's fork.

## 1. MessagePortChannel: memory leak on closed ports

In `MessagePortChannel.cpp`, when a message is posted to a remote port that has already been closed, the message is unconditionally appended to `m_pendingMessages`. These messages will never be delivered, so they accumulate indefinitely. Sending 5000 x 64KB messages to a closed `MessagePort` causes ~330MB of RSS growth.

The fix should prevent messages from being queued when the target port is closed.

**File:** `src/bun.js/bindings/webcore/MessagePortChannel.cpp`, function `postMessageToRemote`

## 2. JSAbortController: signal.reason lost after GC

In `JSAbortController.cpp`, the `visitChildrenImpl` method marks the opaque root but does not visit the `signal().reason()` value. When only the controller (not the signal) is retained by JavaScript, and GC runs, the reason object can be collected. After that, `controller.signal.reason` returns `undefined` instead of the original abort reason.

The fix should ensure `signal().reason()` is visited during GC traversal.

**File:** `src/bun.js/bindings/webcore/JSAbortController.cpp`, function `visitChildrenImpl`

## 3. BroadcastChannel: use-after-free in global channel map

In `BroadcastChannel.cpp`, the global channel map (`allBroadcastChannels()`) stores raw `BroadcastChannel*` pointers. When a worker-owned channel is being destroyed while the main thread dispatches a message through `dispatchMessageTo`, the main thread can dereference a dangling pointer. The race window is between the channel's destructor running on the worker thread and the `RefPtr` assignment on the main thread.

The fix should use weak pointers in the global map so that lookups atomically check liveness.

**File:** `src/bun.js/bindings/webcore/BroadcastChannel.cpp`

## 4. EventListenerMap: missing thread affinity checks

In `EventListenerMap.cpp` / `EventListenerMap.h`, mutation operations (`add`, `remove`, `clear`, `replace`, `removeFirstEventListenerCreatedFromMarkup`) lack per-instance thread ownership validation. Unlike a global `isMainThread()` check, the correct approach records the owning thread per-instance on first mutation, then asserts subsequent mutations come from the same thread (exempting GC sweeper threads).

The fix should add a thread affinity check at the top of each mutation method.

**Files:**
- `src/bun.js/bindings/webcore/EventListenerMap.h` (new member + helper)
- `src/bun.js/bindings/webcore/EventListenerMap.cpp` (call helper in each mutator)
