# chore: document rule-group severity relation and update rules_check

## Summary

Update the `biome_analyze` CONTRIBUTING guide and the `rules_check` xtask to emit diagnostics when a rule has a severity level that doesn't match its group.

## Problem

Currently, Biome doesn't enforce consistency between rule groups and their severity levels. This leads to:
- Rules in `correctness`, `security`, or `a11y` groups that don't use `error` severity
- Rules in `style` or `complexity` groups incorrectly using `error` severity
- Inconsistent severity for `performance` and `suspicious` groups

Additionally, the `Errors` struct in `rules_check` uses a tuple struct pattern (`Errors(String)`) with specific methods for each error type, which is not extensible.

## Expected Changes

### 1. Update CONTRIBUTING.md

Add a new section "Rule group and severity" in `crates/biome_analyze/CONTRIBUTING.md` (after "Rule severity") that documents:

- `correctness`, `security`, and `a11y` rules **must** have severity set to `error`
- `style` rules **must** have severity set to `info` or `warn` (not `error`)
- `complexity` rules **must** have severity set to `warn` or `info` (not `error`)
- `suspicious` rules **must** have severity set to `warn` or `error` (not `info`)
- `performance` rules **must** have severity set to `warn`
- Actions **must** have severity set to `info`

Include a note that legacy exceptions exist and will be removed in Biome 3.0.

### 2. Refactor Errors struct in xtask/rules_check

In `xtask/rules_check/src/lib.rs`:

1. Change `Errors` from a tuple struct to a named field struct:
   ```rust
   struct Errors {
       message: String,
   }
   ```

2. Add a `new()` constructor:
   ```rust
   const fn new(message: String) -> Self {
       Self { message }
   }
   ```

3. Remove the old specific methods `style_rule_error()` and `action_error()`

4. Update the `Display` impl to use the named field

5. Move `impl std::error::Error for Errors {}` to immediately follow the struct/impl block

### 3. Expand check_rules() to validate all groups

Update the `check_rules()` function to validate severity constraints for all groups:

- Add checks for `a11y`, `correctness`, `security` groups (must be `error`)
- Keep existing check for `style` group (must not be `error`)
- Add check for `complexity` group (must not be `error`)
- Add check for `performance` group (must be `warn`)
- Add check for `suspicious` group (must not be `info`)
- Keep existing check for Actions (must be `info`)

Include legacy exception lists for rules that don't follow these constraints yet (to be removed in Biome 3.0):
- For `a11y`/`correctness`/`security`: `noNodejsModules`, `noUnusedImports`, `noAlert`, `noNoninteractiveElementInteractions`, etc.
- For `performance`: `noAwaitInLoops`, `useGoogleFontPreconnect`, `useSolidForComponent`
- For `suspicious`: `noAlert`, `noBitwiseOperators`, `noConstantBinaryExpressions`, etc.

## Files to Look At

- `crates/biome_analyze/CONTRIBUTING.md` — add "Rule group and severity" section
- `xtask/rules_check/src/lib.rs` — refactor Errors struct and expand check_rules()

## Reference

The PR should address: https://github.com/biomejs/biome/pull/7758#issuecomment-3407279827
