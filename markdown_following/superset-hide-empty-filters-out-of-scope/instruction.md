# Hide the "Filters out of scope" section when there are no out-of-scope filters

## Repository

You are working in a clone of [apache/superset](https://github.com/apache/superset)
checked out to a parent of the merge that introduced the fix you are about to
recreate. The clone lives at `/workspace/superset`. The frontend code lives
under `/workspace/superset/superset-frontend` (React + TypeScript, tested with
Jest + React Testing Library).

You can run frontend tests with:

```bash
cd /workspace/superset/superset-frontend
npx jest <path-to-test-file>
```

`npm ci` has already been run; `node_modules` is populated.

## Symptom

The dashboard filter bar exposes a collapsible section labelled
`Filters out of scope (N)` where `N` is the number of filters that are not
applied to the current dashboard tab. When `N` is `0` — i.e. every filter is
in scope for the current tab — the section is **still being rendered**. It
shows up in the DOM as a label reading literally:

```
Filters out of scope (0)
```

…and the collapsible is rendered but disabled. Users see a useless empty
"Filters out of scope (0)" line above the **Apply Filters** button at the
bottom of the filter list. The expected behaviour is that the section is
**not rendered at all** when there is nothing out of scope.

The bug is reproducible by opening the Sales dashboard and scrolling to the
bottom of the filter list — there is no out-of-scope filter, yet
`Filters out of scope (0)` appears.

## Required behaviour

The "Filters out of scope" section must satisfy all three of these
contracts:

1. **Empty out-of-scope list ⇒ not rendered.** When the array of
   out-of-scope filters is empty, no element matching the text
   `Filters out of scope` may be present in the rendered DOM.
2. **Non-empty out-of-scope list ⇒ rendered.** When at least one filter is
   out of scope (and the panel is otherwise allowed to show), the
   "Filters out of scope" section must be rendered as before.
3. **`showCollapsePanel` flag continues to gate the section.** When the
   parent component sets `showCollapsePanel` to `false`, the section must
   stay hidden regardless of how many filters are out of scope.

These three contracts apply both inside the vertical filter bar
(`FilterControls`) and inside the horizontal-mode dropdown content
(`FiltersDropdownContent`). Both rendering paths must observe the new
behaviour.

The previous implementation worked around the empty case by passing
`collapsible="disabled"` to the underlying Ant Design `Collapse`. That
workaround is no longer reachable once the parents stop rendering the
component on the empty path, so any code that exists only to handle the
empty-array case from inside the collapsible itself becomes dead code and
should be removed.

## Tests

The reward harness runs three pytest checks (which in turn drive Jest):

- `test_oracle_filters_out_of_scope_visibility` — verifies all three
  contracts above against the `FiltersDropdownContent` component using
  React Testing Library and the helper at
  `superset-frontend/spec/helpers/testing-library`. The hidden assertions
  query the rendered DOM with `screen.queryByText(/Filters out of scope/)`
  and `screen.getByText(/Filters out of scope/)`.
- `test_repo_actionbuttons_regression` — runs
  `superset-frontend/src/dashboard/components/nativeFilters/FilterBar/ActionButtons/ActionButtons.test.tsx`
  to guard against unintended regressions in adjacent code.
- `test_repo_filtercontrols_suite_passes` — runs the existing
  `FilterControls.test.tsx` suite end-to-end. All tests in it must pass.

Add or modify tests as you see fit, but the public contract above is what is
ultimately checked. The grader treats `screen.queryByText(/Filters out of scope/)`
as the authoritative probe for whether the section is "rendered".

## Code Style Requirements

This codebase has strict frontend conventions enforced via pre-commit / ESLint /
Prettier and described in `CLAUDE.md` and `AGENTS.md` at the repository root.
Of particular relevance to this task:

- **No `any` types.** Use proper TypeScript types (interfaces, generics, or
  `unknown` with explicit narrowing). New code must compile with the project's
  strict type checks.
- **Functional components with hooks** — no class components.
- **Tests use top-level `test()`**, not `describe()` blocks (the codebase
  follows the "avoid nesting when testing" principle).
- **Jest + React Testing Library only** — Enzyme is fully removed; do not
  introduce it.
- **`@superset-ui/core` / `@superset-ui/core/components`** is the source of
  UI primitives and theming tokens — do not import directly from `antd`.
- **Apache License header** on every new TypeScript file (the standard ASF
  block already used by all sibling files).
- **No time-relative words** ("now", "currently", "today") in code
  comments — comments should remain accurate regardless of when they are
  read.

The pre-commit hook (`pre-commit run --all-files`) covers prettier, eslint,
and TypeScript; nothing extra to configure.

## Where to look

The two rendering call sites both live under
`/workspace/superset/superset-frontend/src/dashboard/components/nativeFilters/FilterBar/`,
and the underlying collapsible component lives under the same tree. The
existing tests next to those components illustrate the testing-library
helper and the expected import shape.
