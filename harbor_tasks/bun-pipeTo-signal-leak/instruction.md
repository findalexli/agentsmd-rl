# AbortSignal Memory Leak in ReadableStream.pipeTo

## Symptom

When `ReadableStream.prototype.pipeTo` is called with an `AbortSignal` option and the pipe never completes (e.g., the readable stream never enqueues data), the `AbortSignal` is **never garbage collected**. Each such call leaks one AbortSignal, causing memory to grow unbounded.

## Root Cause

A reference cycle prevents collection. The AbortSignal holds references to abort algorithms, and when these algorithms capture JavaScript callbacks, the callbacks hold references back to the signal through closure scopes. This creates a cycle that prevents the GC from collecting the AbortSignal even when no external references remain.

## Expected Behavior

When all JavaScript references to an AbortSignal are dropped and the pipe never completes, the AbortSignal should be garbage collected. No reference cycle should prevent collection.