# Fix transitive ancestor filter chain in dashboard native filters

You are working in the Apache Superset repository at
`/workspace/superset`. The frontend code lives under `superset-frontend/`.

## Bug to fix

Dashboard native filters can be configured as a dependency chain. For example,
a user creates four native filters `A`, `B`, `C`, `D` where:

- `B` lists `A` in its `cascadeParentIds`
- `C` lists `B` in its `cascadeParentIds`
- `D` lists `C` in its `cascadeParentIds`

Each filter only references its **direct** parent in `cascadeParentIds`. This
is the default the filter-config modal saves when a user wires up a chain
visually.

When a chart on the dashboard depends on all four filters and the user picks
values for `A`, then `B`, then `C`, then `D` and clicks **Apply**, the chart
is filtered by only a subset of the selected values. A second click of
**Apply** is needed to get the correct result.

The root cause is in the React hook that aggregates the
`extra_form_data` a dependent filter inherits from its parents. The current
implementation only iterates a filter's *direct* `cascadeParentIds`. For a
chain `A -> B -> C -> D`, the merged `extra_form_data` emitted on D's behalf
therefore reflects only C's state — A's and B's clauses are dropped on the
first Apply, until the cascade has fully re-settled on a second Apply.

The readiness guard in the same area (the code that decides whether a child
filter has enough information from its parents to issue its options query)
suffers from the same single-hop assumption. If the readiness guard counts a
different set of parents than the merging logic, the two views can disagree
about whether a filter is ready, producing the same partial-result symptom
on the first Apply.

## Required behavior

For any filter `X` in a native-filter configuration, the merged
`extra_form_data` returned for `X` must reflect every transitive ancestor of
`X` — every filter reachable by repeatedly walking `cascadeParentIds` from
`X` — not only the direct parents.

Specifically:

- **Linear chains.** For `A -> B -> C -> D` (each level lists only its
  direct parent), the merged `extra_form_data` for `D` must include
  `extra_form_data` from `A`, `B`, and `C`.
- **Diamond / shared ancestors.** If a filter has multiple parents that
  share a common ancestor (e.g. `D` has parents `B` and `C`, and both
  depend on `A`), the shared ancestor must contribute exactly once — not
  twice.
- **Scalar override precedence.** `mergeExtraFormData` appends array fields
  like `filters` but **overrides** scalar fields like `time_range`. The
  ancestor traversal must visit ancestors in topological order so that the
  *closest* ancestor's scalar value wins over more distant ancestors. For
  `A -> B -> C` where both `A` and `B` set `time_range`, the result for `C`
  must be `B`'s `time_range`.
- **Cycle protection.** The filter-config modal forbids circular
  dependencies at save time, but a malformed saved configuration must not
  cause the traversal to loop forever. A cycle should be tolerated and the
  traversal should return a finite ancestor set.
- **Missing entries.** Referencing a parent id that is not present in the
  filter configuration map must not crash the traversal.

The readiness guard in the dependent-filter rendering path must use the
same transitive ancestor set that the merging logic uses, so the two cannot
disagree about which parents count.

## Scope

The fix is purely in the frontend (TypeScript / React) and does not touch
the Python backend or the database. The behavioral coverage for the fix
should be jest unit tests, not Cypress or Playwright.

## Code Style Requirements

- The repo's TypeScript guidelines (see `AGENTS.md`) prohibit the use of
  `any` types in new or modified code — use proper TypeScript types.
- New `.ts` / `.tsx` files require the standard Apache Software Foundation
  license header at the top.
- New jest tests should be flat `test()` calls rather than nested
  `describe()` blocks (see `AGENTS.md` testing guidance).
- Avoid time-specific language ("now", "currently", "today") in code
  comments.

## Verification

The behavioral fix is verified by jest tests that exercise
`useFilterDependencies` against a multi-level chain via
`@testing-library/react-hooks` and a `redux-mock-store`-backed Redux
provider. The existing jest tests in
`superset-frontend/src/dashboard/components/nativeFilters/FilterBar/FilterControls/`
must continue to pass.
