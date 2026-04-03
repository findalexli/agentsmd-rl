# Fix `noShadow` rule: destructured variable bindings in sibling scopes

## Problem

The `noShadow` lint rule incorrectly flags destructured variable bindings in sibling scopes as shadowing. For example, this code triggers a false positive:

```js
function example(condition) {
  if (condition) {
    const { name } = getFirst();
    return name;
  }
  const { name } = getSecond();  // FALSE POSITIVE: flagged as shadowing
  return name;
}
```

Object destructuring (`const { x } = ...`), array destructuring (`const [x] = ...`), nested patterns, rest elements, and shorthand destructuring are all affected. The rule doesn't recognize these as proper variable declarations when checking sibling scopes.

## Expected Behavior

Destructured bindings in sibling scopes (e.g., different `if`/`else` branches) should not be flagged as shadowing each other. The rule should still correctly detect destructured bindings that genuinely shadow an outer variable (e.g., `const x = 1; function f() { const { x } = obj; }`).

## Files to Look At

- `crates/biome_js_analyze/src/lint/nursery/no_shadow.rs` — the lint rule implementation. The `is_declaration()` and `is_on_initializer()` helper functions need to handle bindings inside destructuring patterns, not just direct variable declarators.

## Additional Context

- Test spec files should be added for both valid (no false positives) and invalid (true shadow detection) destructuring cases under `crates/biome_js_analyze/tests/specs/nursery/noShadow/`.
- After fixing the code, update the project's agent instructions to improve documentation around test file naming conventions, since the existing guidance in `.claude/skills/testing-codegen/SKILL.md` is incomplete about how `valid`/`invalid` in file and folder names controls diagnostic expectations.
