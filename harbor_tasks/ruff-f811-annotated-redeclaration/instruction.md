# F811 does not flag annotated variable redeclarations in preview mode

Ruff's `F811` rule (`RedefinedWhileUnused`) currently catches redefinitions of unused imports and some other bindings, but it does **not** detect cases where an annotated variable assignment shadows a previous annotated assignment of the same name in the same scope, even in preview mode.

For example, this code silently passes without any F811 diagnostic:

```python
bar: int = 1
bar: int = 2  # No warning — but the first assignment is clearly dead
```

Meanwhile, if these were imports, F811 would correctly flag the redefinition. The issue is specific to annotated assignments (`x: T = value`) — both the original and the shadowing binding must be annotated assignments with values for this to be a true "redefinition while unused" scenario.

Important nuances that should be preserved:
- Plain reassignments like `y = 1; y = 2` should **not** be flagged — this is normal Python
- Mixed cases (one annotated, one plain) should **not** be flagged
- If the first binding is actually used between the two assignments, it should **not** be flagged

## Affected code

The core logic lives in `crates/ruff_linter/src/rules/pyflakes/rules/redefined_while_unused.rs`, specifically in the `redefined_while_unused` function. The function iterates over bindings in a scope and decides which ones count as redefinitions — but annotated assignments are currently not recognized as redefinitions of each other, so they slip through.

This behavior should only be enabled in preview mode, following ruff's convention for gating new lint behaviors behind the preview flag. See `crates/ruff_linter/src/preview.rs` for how other preview-gated behaviors are defined.

## What needs to happen

1. Teach the F811 rule to recognize annotated assignment redeclarations, gated behind preview mode
2. Ensure only the case where **both** bindings are annotated assignments with values is flagged
3. Add a test fixture and snapshot test covering all the edge cases described above
4. Update the rule's documentation to describe the preview behavior
