# Stale log pointer in `resolveMaybeNeedsTrailingSlash` causes stack-buffer-overflow

## Bug Description

In `src/bun.js/VirtualMachine.zig`, the function `resolveMaybeNeedsTrailingSlash` creates a stack-local `logger.Log` and temporarily sets it on the resolver and linker so that resolution errors are captured locally:

```zig
var log = logger.Log.init(bun.default_allocator);
defer log.deinit();
jsc_vm.log = &log;
jsc_vm.transpiler.resolver.log = &log;
jsc_vm.transpiler.linker.log = &log;
```

The problem is that the **package manager's** log pointer is never updated. When module resolution triggers auto-install (e.g., via `mock.module()` with a specifier that doesn't map to an installed package), the package manager calls `manager.log.addErrorFmt()` using its own `log` field — which still points to wherever it was set before. If a previous call to `resolveMaybeNeedsTrailingSlash` already returned and its stack frame was destroyed, the package manager's stale pointer leads to a **stack-buffer-overflow**.

The existing `defer` block restores `jsc_vm.log`, `resolver.log`, and `linker.log` to `old_log`, but the package manager's log is left dangling.

## Reproduction

Use `mock.module()` with a non-existent specifier, which causes the resolver to trigger auto-install logic through the package manager. On a debug (ASAN) build, this produces:

```
Address:stack-buffer-overflow:bun-debug+0xc9f417a
```

## Expected Fix Location

The save/restore pattern in `resolveMaybeNeedsTrailingSlash` around lines 1832–1845 in `src/bun.js/VirtualMachine.zig` needs to also cover `package_manager.log`. A similar pattern already exists in `ModuleLoader.zig`.

## Files of Interest

- `src/bun.js/VirtualMachine.zig` — the `resolveMaybeNeedsTrailingSlash` function
- `src/bun.js/ModuleLoader.zig` — contains a reference implementation of the save/restore pattern for `pm.log`
