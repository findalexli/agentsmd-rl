# Stale log pointer causes stack-buffer-overflow in `resolveMaybeNeedsTrailingSlash`

## Bug Description

In `src/bun.js/VirtualMachine.zig`, the function `resolveMaybeNeedsTrailingSlash` creates a stack-local `logger.Log` and temporarily sets it on several subsystems so that resolution errors are captured locally:

```zig
var log = logger.Log.init(bun.default_allocator);
defer log.deinit();
jsc_vm.log = &log;
jsc_vm.transpiler.resolver.log = &log;
jsc_vm.transpiler.linker.log = &log;
```

A `defer` block restores those three log pointers to their previous values after the function returns.

However, when module resolution triggers auto-install (e.g., via `mock.module()` with a specifier that doesn't map to an installed package), the program crashes with a **stack-buffer-overflow** — the crash address shows it's coming from a destroyed stack frame.

## Reproduction

Use `mock.module()` with a non-existent specifier, which causes the resolver to trigger auto-install logic. On a debug (ASAN) build, this produces:

```
Address:stack-buffer-overflow:bun-debug+0xc9f417a
```

## Files of Interest

- `src/bun.js/VirtualMachine.zig` — the `resolveMaybeNeedsTrailingSlash` function