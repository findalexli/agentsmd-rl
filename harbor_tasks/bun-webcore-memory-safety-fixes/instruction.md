# WebCore Memory Safety Bugs

Bun's WebCore code (forked from WebKit) has four memory safety issues in `src/bun.js/bindings/webcore/`. Each one is a confirmed upstream WebKit bug that was fixed in WebKit but not yet backported to Bun's fork.

## 1. MessagePortChannel: memory leak on closed ports

When a message is posted to a remote port that has already been closed, the message is unconditionally appended to the pending messages collection. These messages will never be delivered, so they accumulate indefinitely. Sending 5000 x 64KB messages to a closed MessagePort causes ~330MB of RSS growth.

The fix should check whether the target port is closed before appending any message. The guard must use a computed (non-hardcoded) index into the port's closed-state array. The resulting diff should contain `m_isClosed` and `return false` around the same area as `m_pendingMessages`.

**File:** `src/bun.js/bindings/webcore/MessagePortChannel.cpp`

## 2. JSAbortController: signal.reason lost after GC

When only the AbortController (not the AbortSignal) is retained by JavaScript, and GC runs, the reason object can be collected. After that, `controller.signal.reason` returns `undefined` instead of the original abort reason. The `visitChildrenImpl` method marks the opaque root but does not visit the signal's reason value.

The fix should ensure the signal's reason is visited during GC traversal. The resulting diff should include `reason` in a `visitChildrenImpl` context, with `signal()` and `reason()` chained in the same expression and the result passed to the visitor.

**File:** `src/bun.js/bindings/webcore/JSAbortController.cpp`

## 3. BroadcastChannel: use-after-free in global channel map

The global channel map stores raw `BroadcastChannel*` pointers. When a worker-owned channel is being destroyed while the main thread dispatches a message, the main thread can dereference a dangling pointer. The race window is between the channel's destructor running on the worker thread and the pointer assignment on the main thread.

The fix should use a thread-safe weak pointer template in the global map so that lookups atomically check liveness. The map declaration should use `ThreadSafeWeakPtr<BroadcastChannel>` as its value type (not a raw pointer). The resulting diff should contain `ThreadSafeWeakPtr`.

**File:** `src/bun.js/bindings/webcore/BroadcastChannel.cpp`

## 4. EventListenerMap: missing thread affinity checks

Mutation operations (add, remove, clear, replace, removeFirstEventListenerCreatedFromMarkup) lack per-instance thread ownership validation. Unlike a global main-thread check, the correct approach records the owning thread per-instance on first mutation, then asserts subsequent mutations come from the same thread (exempting GC sweeper threads).

The fix should add a thread affinity check at the top of each mutation method, before the Locker. It requires a helper function (e.g., `releaseAssertOrSetThreadUID`) and a thread UID member (e.g., `uint32_t m_threadUID`). The helper must call `mayBeGCThread()` or `isGCThread()` for the GC exemption. At least 4 of the 5 mutators must have this check. The resulting diff should contain `thread` or `Thread` in both `.cpp` and `.h` files.

**Files:**
- `src/bun.js/bindings/webcore/EventListenerMap.h`
- `src/bun.js/bindings/webcore/EventListenerMap.cpp`
