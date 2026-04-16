# Make the SIM102 collapsible-if fix safe in preview mode

## Problem

The `collapsible-if` rule (`SIM102`) detects nested `if` statements that can be collapsed into a single `if` with `and`. The auto-fix for this rule is currently always marked as `Unsafe`, even when running in `--preview` mode. However, the fix is actually safe — it preserves comments (the fix is not offered when comments exist between the two `if` headers), and the rule is careful to avoid false positives.

When users run `ruff check --fix --preview`, SIM102 fixes are not applied automatically because they're marked as unsafe. Users have to explicitly use `--unsafe-fixes` to get these applied, which is unnecessary friction for a fix that's demonstrably safe.

## Expected Behavior

- When `--preview` is enabled, the SIM102 fix should have `Safe` applicability (so it gets applied with `--fix`).
- When `--preview` is not enabled, the fix should remain `Unsafe` (preserving backward compatibility).
- The fix safety should be gated by a preview-aware mechanism that determines whether the safe applicability can be used based on the current settings.

## Constraints

When implementing the fix, adhere to these coding standards (from AGENTS.md):

- **Line 76**: Rust imports must be placed at the top of the file, not locally inside function bodies.
- **Line 79**: Do not use `.unwrap()`, `panic!()`, or `unreachable!()` in new code. Use proper error handling instead.

## Files to Look At

- The SIM102 rule implementation is in the flake8_simplify rules module
- Preview mode gating functions are typically defined in the preview module
