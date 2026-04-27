# Flow strip: `declare export default interface ...` is rejected by the parser

The repository at `/workspace/swc` is the [swc](https://github.com/swc-project/swc)
JavaScript / TypeScript / Flow toolchain. The Flow strip path uses the
`swc_ecma_parser` crate to recognise Flow-only forms before re-emitting
JavaScript.

## Symptom

When `swc_ecma_parser` is built with the `flow` feature and asked to parse
the following snippet:

```js
declare export default interface Foo {
  x: number;
}
```

the parser fails (or otherwise refuses to produce an interface
declaration). Other shapes immediately around it already work today:

* `declare export default class C { ... }` — parses as a class declaration
  with `declare = true`.
* `declare export default function f() { ... }` — parses as a function
  declaration with `declare = true`.
* `declare export default <type>;` — falls through to a synthetic
  type-alias declaration.

The interface form is the missing branch. It should parse to the same
interface-declaration node the rest of the codebase already uses for
`declare interface Foo { ... }`, with the `declare` flag set to `true` on
the resulting declaration.

## What "correct" looks like

A correct fix lets the parser accept

```js
declare export default interface Foo {
  x: number;
}
```

and produce a `TsInterfaceDeclaration` AST node where:

* the declaration's `declare` flag is `true`,
* the identifier is `Foo`,
* the body has exactly one member (the `x: number` property signature),
* `extends` is empty for the bare form, and non-empty when an `extends`
  clause is present (e.g. `... interface Bar extends Base { y: string; }`).

No parser errors should be reported for either form (`take_errors()` must
return an empty vector).

The pre-existing forms listed under "Symptom" above must continue to parse
exactly as they did before — in particular `declare export default class C { ... }`
must still produce a class declaration with `declare = true`, and
`declare export default number;` must still fall through to the synthetic
type-alias path.

## Where the gap lives

The Flow `declare export default` parsing ladder lives in the
`swc_ecma_parser` crate, in the TypeScript/Flow parser module. There is a
chain of `if`-branches that recognise `class`, `function`, and a
fallthrough type-annotation case; the new form belongs in this ladder
alongside the existing branches.

## Scope notes (mirrors the project's intent)

The change is intentionally **narrow**:

* No new behavior for `declare export default opaque type ...`.
* No change to semicolon-separated declare-export specifier lists like
  `declare export { Foo; Bar }`.
* The existing fallback for `declare export default <type>;` must keep
  working unchanged.

## How to verify locally

The repository's normal verification flow applies:

* `cargo check -p swc_ecma_parser --features flow --tests`
* `cargo test  -p swc_ecma_parser --features flow`

Both must pass after your fix. The crate's `tests/flow/**/*.js` fixture
harness (see `crates/swc_ecma_parser/tests/flow.rs`) is the project's
preferred way to lock in new parser surface, so any test fixture you add
should follow the existing `tests/flow/<dir>/<name>.js` +
`<name>.js.json` snapshot convention.

## Code Style Requirements

* The modified file must be `cargo fmt` clean — the verifier runs
  `cargo fmt -- --check` on the touched parser source and rejects
  formatting drift.
* Stable Rust only; no `#![feature(...)]` opt-ins.
* Comments and documentation, if any, must be in English.

## Repository conventions to keep in mind

The repo's `AGENTS.md` documents a few project-wide rules that apply here:

* Performance is the top priority — avoid gratuitous allocations or
  cloning in the parser hot path.
* Prefer fixture tests over inline `#[test]` functions for parser
  behavior.
* When constructing `Atom` values, prefer `&str` over `Cow<str>` over
  `String`.
