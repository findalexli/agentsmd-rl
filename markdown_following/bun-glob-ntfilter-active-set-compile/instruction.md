# Build error in GlobWalker: undeclared identifier `component_idx`

## Problem

The glob walker in `src/glob/GlobWalker.zig` fails to compile. The Windows-specific
directory iteration code calls `computeNtFilter(component_idx)`, referencing a
variable named `component_idx` that no longer exists in scope after a recent refactor.

## Context

The `GlobWalker_` function's directory iteration logic on Windows uses a kernel-level
filename filter via `setNameFilter` for optimization. This filter is computed by
`computeNtFilter`, which takes a pattern component index.

A recent refactor replaced the single `component_idx` variable with a BitSet called
`active` (to correctly handle `**` glob patterns). The `active` BitSet tracks multiple
active pattern component indices simultaneously. The Windows iteration code near the
`setNameFilter` call still references the old `component_idx` variable.

When multiple glob components are active simultaneously (e.g., after a `**` segment),
the kernel filter must be disabled entirely — either by passing `null` to `setNameFilter`
or by using an empty slice such as `&[_]u16{}`. When exactly one component is active,
the filter index must be derived from the `active` BitSet.

## What needs to happen

Fix the compilation error by updating the Windows-specific code near the `setNameFilter`
call. The `setNameFilter` call must be preserved and `computeNtFilter` must still be
called at the fix site.

The fix should derive the pattern component index from the `active` BitSet (using the
set's built-in methods) when exactly one component is active, and disable the filter
(using `null` or an empty `&[_]u16{}` slice) when multiple components are active.

## Code Style Requirements

- No inline `@import()` inside functions — place imports at file bottom or in the
  containing struct.
- Prefer `bun.*` APIs over `std.*` when a bun equivalent exists.
- Explain WHY not WHAT in comments — comments should describe invariants and reasoning.

## Verification

The bug is inside a `comptime isWindows` block. On non-Windows platforms (including the
Linux test environment), full builds may succeed without the fix since the compiler
discards platform-specific code paths during codegen. Verify your changes through
static analysis and by running `zig ast-check` on the file.

See the original pull request for additional context:
https://github.com/oven-sh/bun/pull/28543
