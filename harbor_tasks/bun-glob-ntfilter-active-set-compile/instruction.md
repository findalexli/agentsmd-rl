# Build error in GlobWalker: undeclared identifier `component_idx`

## Problem

The glob walker in `src/glob/GlobWalker.zig` fails to compile with the following error:

```
src/glob/GlobWalker.zig:715:69: error: use of undeclared identifier 'component_idx'
                        iterator.setNameFilter(this.computeNtFilter(component_idx));
                                                                    ^~~~~~~~~~~~~
```

## Context

The `GlobWalker_` function's directory iteration logic on Windows applies an NT kernel-level filename filter via `setNameFilter` to optimize directory scans. This filter is computed by `computeNtFilter`, which operates on a single pattern component index.

A recent refactor replaced the single component index tracking variable with a `BitSet` called `active` that tracks multiple active pattern component indices simultaneously (to correctly handle `**` glob patterns that can match across multiple components at once). However, the Windows `setNameFilter` call still references the old single-index variable, which no longer exists in scope.

## What needs to happen

The `setNameFilter` call (around line 715) needs to be updated to work with the new `active` BitSet instead of the removed single-index variable.

Key considerations:
- `computeNtFilter` takes a single `u32` component index
- When multiple pattern indices are active (e.g., after a `**` segment), a single-component kernel filter could hide directory entries that other active indices need to match
- The NT filter is purely a pre-filter optimization — `matchPatternImpl` still runs on every returned entry for correctness (per the existing doc comment on `computeNtFilter`)

Look at `src/glob/GlobWalker.zig` around line 710-720 for the broken code, and the `active` BitSet usage elsewhere in the same function for how other code was updated.
