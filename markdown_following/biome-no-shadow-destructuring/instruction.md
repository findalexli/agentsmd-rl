# Fix `noShadow` to recognise destructured bindings

You are working in a checkout of the [Biome](https://biomejs.dev) Rust
monorepo at `/workspace/biome`. Biome ships a JavaScript/TypeScript
linter; one of its lint rules is `noShadow`, in the `nursery` group, which
flags variables that shadow another variable from an outer scope.

## The bug

`noShadow` does not currently treat **destructured variable bindings** as
declarations. As a result it produces incorrect diagnostics in two
opposite directions:

1. **Missed shadows** — when a destructuring pattern in an inner scope
   uses a name that exists in the outer scope, the inner binding *should*
   be reported as a shadow but isn't. Examples that should produce a
   `nursery/noShadow` diagnostic but currently don't:

   ```js
   const x = 1;
   function shadowObj() {
       const { a: x } = { a: 2 };          // object pattern, renamed
   }

   const y = 1;
   function shadowArr() {
       const [y] = [2];                    // array pattern
   }

   const z = 1;
   function shadowNested() {
       const { a: { b: z } } = { a: { b: 2 } };  // nested
   }

   const w = 1;
   function shadowShorthand() {
       const { w } = { w: 2 };             // shorthand
   }

   const m = 1;
   function shadowMixed() {
       const [{ m }] = [{ m: 2 }];         // mixed object/array
   }

   const rest = 1;
   function shadowRestArr() {
       const [, ...rest] = [1, 2, 3];      // rest in array
   }

   const other = 1;
   function shadowRestObj() {
       const { a, ...other } = { a: 1, b: 2 };  // rest in object
   }
   ```

2. **False positives across sibling scopes** — when two sibling scopes
   (e.g. the `if` and `else` branches of the same function) each
   destructure into the same name, the rule incorrectly flags the second
   one as shadowing the first, even though they live in disjoint scopes
   and never overlap. Examples that should produce **no** diagnostics:

   ```js
   function objDestructuring(condition) {
       if (condition) {
           const str = 'hi';
           const { str: destructuredStr } = { str: 'hi' };
           return { str, destructuredStr };
       }
       const str = 'bye';
       const { str: destructuredStr } = { str: 'bye' };
       return { str, destructuredStr };
   }

   function shorthandDestructuring(condition) {
       if (condition) {
           const { x } = { x: 1 };
           return x;
       }
       const { x } = { x: 2 };
       return x;
   }

   function restDestructuring(condition) {
       if (condition) {
           const [head, ...tail] = [1, 2, 3];
           return { head, tail };
       }
       const [head, ...tail] = [4, 5, 6];
       return { head, tail };
   }
   ```

Both symptoms have the same underlying cause: the rule's notion of "is
this binding a declaration?" only walks one level up the syntax tree, so
identifiers that live inside a destructuring pattern (which sits between
the `JsIdentifierBinding` and the surrounding `JsVariableDeclarator`) are
not recognised as declarations.

## What you need to do

Update `noShadow` so that all of object destructuring, array
destructuring, nested destructuring, shorthand object destructuring, and
rest elements (in either flavour of destructuring) are recognised as
variable declarations and participate in the shadowing analysis exactly
like a plain `const x = …` would.

Both behaviours must change together: missed shadows should now be
reported, and the false positives across sibling scopes should
disappear. The fix should not affect non-destructuring cases — the
existing fixtures for `noShadow` continue to express the rule's intended
behaviour and must keep passing.

## Where to work

The rule lives in `crates/biome_js_analyze/src/lint/nursery/no_shadow.rs`.
Snapshot test fixtures live alongside it under
`crates/biome_js_analyze/tests/specs/nursery/noShadow/`. Two new fixtures
have already been placed there — `invalidDestructuring.js` and
`validDestructuring.js`, with their `.snap` files — and they encode the
expected behaviour described above. Your fix should make both of those
snapshot tests pass.

You may explore Biome's semantic helpers (look at `Binding` /
`JsIdentifierBinding` and the `binding_ext` module of `biome_js_syntax`)
to find a way to walk from an identifier up through any enclosing
binding pattern to the surrounding declaration.

## How to test

The relevant test binary is `spec_tests` in the `biome_js_analyze`
crate. The dependency graph is already compiled inside the image, so
incremental rebuilds after editing `no_shadow.rs` are quick:

```shell
cd /workspace/biome
cargo test -p biome_js_analyze --test spec_tests -- nursery::no_shadow
```

To run only one specific fixture:

```shell
cargo test -p biome_js_analyze --test spec_tests -- --exact \
    specs::nursery::no_shadow::invalid_destructuring_js
```

## Code Style Requirements

This codebase enforces both `cargo fmt` and `cargo clippy` lints in
CI; make sure your edits compile cleanly under the existing
project-wide warnings (no new clippy warnings, no unused imports). Use
`let` chains (`if let X = a && let Y = b { ... }`) where appropriate
rather than nested `if let` statements — this is a project convention.
