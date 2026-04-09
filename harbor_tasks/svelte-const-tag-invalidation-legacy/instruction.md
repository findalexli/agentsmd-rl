# Fix @const tag invalidation when depending on another @const in legacy mode

## Problem

In Svelte's legacy mode (`runes={false}`), `@const` tags that derive their value from another `@const` through a function expression do not update reactively.

For example, consider this component:

```svelte
<svelte:options runes={false} />

<script>
    let message = 'hello';
</script>

<input bind:value={message} />

{#if true}
    {@const m1 = message}
    {@const m2 = (() => m1)()}

    <p>{m1}</p>
    <p>{m2}</p>
{/if}
```

When the user types into the input, `m1` updates correctly but `m2` stays stuck at `'hello'`. The second `@const` never reflects the updated value because the compiler's analysis phase fails to track that the arrow function expression captures `m1` from the enclosing scope.

## Expected Behavior

Both `m1` and `m2` should update when `message` changes. The compiler should recognize that function expressions (arrow functions, IIFEs) reference bindings from enclosing scopes, even when those scopes are at the same function nesting depth.

## Files to Look At

- `packages/svelte/src/compiler/phases/2-analyze/visitors/shared/function.js` -- the `visit_function` handler that determines which outer references a function expression captures and propagates to the expression's dependency tracking
