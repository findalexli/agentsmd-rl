# Add a Cancel hook to the Pulumi Python Provider

You are working in the Pulumi monorepo, checked out at the parent of merge
commit `3809a4c60c9a423b1cd8edab4f2a7bdafcf71adf`. The repo lives at
`/workspace/pulumi`. Only the Python SDK (`sdk/python/lib/pulumi/provider/`)
is in scope for the tests in this task.

## Background

The Pulumi engine talks to provider plugins over gRPC. The
`ResourceProvider` service defined in `proto/pulumi/provider.proto` includes
a `Cancel` RPC: the engine calls it to ask a provider to abort any in-flight
work and shut down gracefully.

The Python SDK ships **two** Provider base classes that authors subclass
when writing a custom provider:

1. **`pulumi.provider.provider.Provider`** — the long-standing,
   synchronous base class. Its gRPC adapter is
   `pulumi.provider.server.ProviderServicer`.
2. **`pulumi.provider.experimental.provider.Provider`** — the newer
   `async`-native experimental base class (an `abc.ABC`). Its gRPC adapter
   is `pulumi.provider.experimental.server.ProviderServicer`.

Today **neither** class exposes a `cancel` hook, and **neither** servicer's
gRPC `Cancel` RPC does anything useful — calling it on either servicer
produces the inherited `NotImplementedError("Method not implemented!")`
from `grpc`. Provider authors who want to react to a cancel signal have no
way to do so.

## What to do

Give Python provider authors a way to handle the engine's `Cancel` RPC by
exposing a no-op-by-default hook on each base class and wiring each gRPC
servicer to invoke it.

### Synchronous Provider (`pulumi.provider.provider.Provider`)

- Add a `cancel(self) -> None` method to the `Provider` class. The default
  implementation must be a no-op (it must not raise) and must return
  `None`. Subclasses must be able to override it with their own teardown
  logic.
- In `pulumi.provider.server.ProviderServicer`, implement the gRPC `Cancel`
  RPC as an async method `Cancel(self, request, context)` that:
  - calls `self.provider.cancel()` (synchronously — the base hook is sync),
  - returns a `google.protobuf.Empty` message,
  - propagates any exception the provider's `cancel` raises to the caller.

### Experimental Provider (`pulumi.provider.experimental.provider.Provider`)

- Add an `async def cancel(self) -> None` coroutine method to the
  experimental `Provider` ABC. Default implementation is a no-op coroutine
  that returns `None`. Subclasses must be able to override it with their
  own async teardown logic.
- In `pulumi.provider.experimental.server.ProviderServicer`, implement the
  gRPC `Cancel` RPC as an async method `Cancel(self, request, context)`
  that:
  - **awaits** `self._provider.cancel()` (it is a coroutine — do not
    schedule it as a task and return early),
  - returns a `google.protobuf.Empty` message,
  - propagates any exception the provider's `cancel` raises to the caller.

The two RPC handlers must be named exactly `Cancel` (capitalised) on the
servicer classes — this is the gRPC method name dispatched by the
`ResourceProvider` service.

## Constraints

- Do not change unrelated files. The fix is local to
  `sdk/python/lib/pulumi/provider/provider.py`,
  `sdk/python/lib/pulumi/provider/server.py`,
  `sdk/python/lib/pulumi/provider/experimental/provider.py`, and
  `sdk/python/lib/pulumi/provider/experimental/server.py`.
- Do not edit any generated protobuf files (`*_pb2.py`, `*_pb2_grpc.py`,
  `*_pb2.pyi`).
- Do not introduce new external runtime dependencies. The protobuf
  `google.protobuf.empty_pb2.Empty` message and `pulumi.provider`
  package are already available; everything you need is already imported
  in the relevant modules or trivially importable from `google.protobuf`.
- Do not modify the existing test suite under
  `sdk/python/lib/test/provider/`.
- Existing tests under `sdk/python/lib/test/provider/test_server.py` and
  `sdk/python/lib/test/provider/experimental/test_provider.py` must
  continue to pass.

## Where to verify yourself

You can exercise your work directly:

```python
import asyncio
from pulumi.provider.provider import Provider as SyncProvider
from pulumi.provider.server import ProviderServicer as SyncServicer

class P(SyncProvider):
    def __init__(self):
        super().__init__(version="0.0.1")
        self.cancelled = False
    def cancel(self):
        self.cancelled = True

p = P()
servicer = SyncServicer(provider=p, args=[], engine_address="127.0.0.1:0")
asyncio.run(servicer.Cancel(None, None))   # should return google.protobuf.Empty
assert p.cancelled
```

and the equivalent for the experimental variant (with
`pulumi.provider.experimental.{provider,server}` and an `async def cancel`).
