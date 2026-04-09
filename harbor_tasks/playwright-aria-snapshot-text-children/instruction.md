# fix(aria-snapshot): include text children when name is longer than text

## Problem

When generating ARIA snapshots (e.g. via `toMatchAriaSnapshot`), text children are silently dropped from the snapshot output when the accessible name of the parent element is longer than the text content. For example, a `progressbar` with `aria-label="Alpha Beta"` containing child text nodes `<span>Alpha</span>` and `<span>7</span>` produces a snapshot that omits the text entirely, even though "7" is informative content not covered by the accessible name.

This affects any element where the accessible name is longer than its text children — the text is unconditionally stripped regardless of whether it actually contributes information beyond the name.

## Expected Behavior

Text children should be included in the generated ARIA snapshot whenever they contribute information not already present in the accessible name. The existing heuristic for determining text-vs-name overlap should be used for all cases, not short-circuited based on string length alone.

## Files to Look At

- `packages/injected/src/ariaSnapshot.ts` — contains the `textContributesInfo` function that decides whether a text child should be included in the rendered snapshot
