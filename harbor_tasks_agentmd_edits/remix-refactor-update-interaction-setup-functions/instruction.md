# Refactor interaction setup functions to use handle parameter

## Problem

The `@remix-run/interaction` package's custom interaction setup functions currently use `this` binding to access the `Interaction` context. This is inconsistent with the `@remix-run/component` package, which passes a `Handle` parameter. The `this`-based API forces use of `function` declarations (arrow functions lose `this`) and requires `.call()` internally to set the context.

For example, the current API looks like:

```ts
function MyInteraction(this: Interaction) {
  this.on(this.target, { ... })
}
```

## Expected Behavior

All interaction setup functions should receive the `Interaction` handle as a regular parameter instead of through `this` context:

```ts
function MyInteraction(handle: Interaction) {
  handle.on(handle.target, { ... })
}
```

This applies to:
- The `InteractionSetup` type definition
- The internal call site that invokes setup functions
- All built-in interaction setup functions (Press, Popover, FormReset, key interactions)
- The JSDoc describing the `Interaction` interface

After making the code changes, update the relevant documentation to reflect the new API. The package's README contains code examples in the "Custom Interactions" section that show the old `this`-based pattern. Also add an appropriate changeset file documenting this breaking change following the repository's conventions.

## Files to Look At

- `packages/interaction/src/lib/interaction.ts` — core type definitions and the internal call site
- `packages/interaction/src/lib/interactions/form.ts` — FormReset setup function
- `packages/interaction/src/lib/interactions/keys.ts` — key interaction setup functions
- `packages/interaction/src/lib/interactions/popover.ts` — Popover setup function
- `packages/interaction/src/lib/interactions/press.ts` — Press setup function
- `packages/interaction/README.md` — package documentation with code examples
- `packages/interaction/src/lib/interaction.test.ts` — tests using the setup function API
