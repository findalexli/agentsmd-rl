# WebCore Memory Safety Bugs

Bun's WebCore code (forked from WebKit) has four memory safety issues in `src/bun.js/bindings/webcore/`. Each one is a confirmed upstream WebKit bug that was fixed in WebKit but not yet backported to Bun's fork.

## 1. MessagePortChannel: memory leak on closed ports

When a message is posted to a remote port that has already been closed, the message is unconditionally appended to the pending messages collection. These messages will never be delivered, so they accumulate indefinitely. Sending 5000 x 64KB messages to a closed MessagePort causes ~330MB of RSS growth.

The bug is in `MessagePortChannel::postMessageToRemote` in `src/bun.js/bindings/webcore/MessagePortChannel.cpp`. A closed port must reject new messages — the fix adds a guard that checks the closed-state array using the same computed index used to append the message, and returns `false` when the port is closed. The guard appears before any message is appended.

**File:** `src/bun.js/bindings/webcore/MessagePortChannel.cpp`

## 2. JSAbortController: signal.reason lost after GC

When only the AbortController (not the AbortSignal) is retained by JavaScript, and GC runs, the reason object can be collected. After that, `controller.signal.reason` returns `undefined` instead of the original abort reason.

The `visitChildrenImpl` method in `src/bun.js/bindings/webcore/JSAbortController.cpp` marks the opaque root but does not visit the signal's reason field, so the GC can collect it. The fix adds a visit call for the reason object so the GC knows to preserve it.

**File:** `src/bun.js/bindings/webcore/JSAbortController.cpp`

## 3. BroadcastChannel: use-after-free in global channel map

The global channel map stores raw `BroadcastChannel*` pointers. When a worker-owned channel is being destroyed while the main thread dispatches a message, the main thread can dereference a dangling pointer. The race window is between the channel's destructor running on the worker thread and the pointer assignment on the main thread.

The map is declared as `UncheckedKeyHashMap<BroadcastChannelIdentifier, BroadcastChannel*>` in `src/bun.js/bindings/webcore/BroadcastChannel.cpp`. The value type must be changed to use a thread-safe weak pointer so that dereferencing the retrieved pointer is safe. The channel must still be registered in the map (via `.add()` or `.set()`), and the existing `Locker` pattern for the map must be retained.

**File:** `src/bun.js/bindings/webcore/BroadcastChannel.cpp`

## 4. EventListenerMap: missing thread affinity checks

Mutation operations (add, remove, clear, replace, removeFirstEventListenerCreatedFromMarkup) lack per-instance thread ownership validation. Unlike a global main-thread check, the correct approach records the owning thread on first mutation, then asserts subsequent mutations come from the same thread. GC sweeper threads must be exempt from this check.

In `src/bun.js/bindings/webcore/EventListenerMap.cpp`, each mutator must have a thread affinity check that runs before the `Locker`. In `src/bun.js/bindings/webcore/EventListenerMap.h`, a helper function and a member variable are needed to record and validate the owning thread. At least 4 of the 5 mutators need this check.

**Files:**
- `src/bun.js/bindings/webcore/EventListenerMap.h`
- `src/bun.js/bindings/webcore/EventListenerMap.cpp`