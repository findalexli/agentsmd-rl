# Make the SIM102 collapsible-if fix safe in preview mode

## Problem

The `collapsible-if` rule (`SIM102`) detects nested `if` statements that can be collapsed into a single `if` with `and`. The auto-fix for this rule is currently always marked as `Unsafe`, even when running in `--preview` mode. However, the fix is actually safe — it preserves comments (the fix is not offered when comments exist between the two `if` headers), and the rule is careful to avoid false positives.

When users run `ruff check --fix --preview`, SIM102 fixes are not applied automatically because they're marked as unsafe. Users have to explicitly use `--unsafe-fixes` to get these applied, which is unnecessary friction for a fix that's demonstrably safe.

## Expected Behavior

- When `--preview` is enabled, the SIM102 fix should have `Safe` applicability (so it gets applied with `--fix`).
- When `--preview` is not enabled, the fix should remain `Unsafe` (preserving backward compatibility).
- The fix safety should be gated by a function named `is_collapsible_if_fix_safe_enabled` in `preview.rs` that returns `true` when preview mode is enabled.

## Files to Look At

- `crates/ruff_linter/src/rules/flake8_simplify/rules/collapsible_if.rs` — contains the `nested_if_statements` function that generates the SIM102 diagnostic and fix
- `crates/ruff_linter/src/preview.rs` — add a function `is_collapsible_if_fix_safe_enabled` to gate the fix safety
