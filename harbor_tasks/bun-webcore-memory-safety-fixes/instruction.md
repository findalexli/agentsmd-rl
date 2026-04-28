# WebCore Memory Safety Bugs

Bun's WebCore code (forked from WebKit) has several memory safety issues in the C++ WebCore bindings layer. Each one is a confirmed upstream WebKit bug that was fixed upstream but not yet applied to Bun's fork.

## Issue 1: Message Port Channel Memory Leak

When a message is sent via `postMessage` to a port that has already been closed, the message is still appended to the `m_pendingMessages` queue even though it will never be delivered. This causes unbounded memory growth. Sending 5000 messages of 64KB each to a closed port results in approximately 330MB of memory that is never freed.

The `postMessageToRemote` method must check whether the destination port is closed before appending to `m_pendingMessages`. The port closed state is tracked in the `m_isClosed` array, which is indexed by the same computed port index used to access `m_pendingMessages`. When the port at that index has been closed, the method must return `false` without appending the message. The closed-port guard must appear before any reference to `m_pendingMessages` in the function body.

## Issue 2: AbortController Signal Reason Lost After GC

When only the `AbortController` (not the `AbortSignal`) is retained by JavaScript, and garbage collection runs, the abort reason object can be collected prematurely. After GC, accessing `controller.signal.reason` returns `undefined` instead of the original abort reason value.

The `visitChildrenImpl` method currently calls `Base::visitChildren` and `addWebCoreOpaqueRoot` to mark GC roots, but it does not visit `signal().reason()`. The method must also traverse the reason object so the GC knows it is still reachable.

## Issue 3: BroadcastChannel Use-After-Free

BroadcastChannel instances are registered in a global map that maps channel identifiers to channel pointers. When a worker thread destroys a channel while the main thread is dispatching a message, the main thread can dereference a dangling pointer.

The map value type must use a thread-safe weak pointer wrapper instead of a raw pointer, so that dereferencing a retrieved pointer is always safe. The channel must still be registered in the map via `.add()` or `.set()`. The existing locking pattern with `Locker` on `allBroadcastChannelsLock` must be retained.

## Issue 4: Event Listener Map Missing Thread Affinity Validation

Mutation operations on the event listener map (`clear`, `replace`, `add`, `remove`, `removeFirstEventListenerCreatedFromMarkup`) do not verify that they are called from a consistent thread. This can lead to data races if different threads mutate the map concurrently.

Each mutator method needs a thread affinity check that runs before acquiring the `Locker`. The check must record the owning thread on first mutation and validate that subsequent mutations come from the same thread. GC sweeper threads must be exempt from this verification. At least 4 of the 5 mutator methods require this check. A member variable is needed to track the thread identity.

## CLAUDE.md

After applying all fixes, add a note to CLAUDE.md summarizing the WebCore memory safety fixes that were applied.
