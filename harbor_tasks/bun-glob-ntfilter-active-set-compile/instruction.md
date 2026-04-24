# Build error in GlobWalker: undeclared identifier

## Problem

The glob walker in `src/glob/GlobWalker.zig` fails to compile. The Windows-specific directory iteration code references a variable that no longer exists after a recent refactor.

## Context

The `GlobWalker_` function's directory iteration logic on Windows uses a kernel-level filename filter via `setNameFilter` for optimization. This filter is computed by `computeNtFilter`, which takes a pattern component index.

A recent refactor replaced the single component index tracking variable with a BitSet called `active` (to correctly handle `**` glob patterns). The Windows iteration code still references the old variable.

## What needs to happen

Fix the compilation error.

The glob walker must correctly handle multiple active pattern components (e.g., `**` segments). The `setNameFilter` call must be preserved. `computeNtFilter` must still be called near it.