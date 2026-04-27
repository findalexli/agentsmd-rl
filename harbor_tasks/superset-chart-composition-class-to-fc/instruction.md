# Convert chart-composition components to function components

The repository at `/workspace/superset` is the Apache Superset codebase, a
React/TypeScript front end alongside a Flask/Python back end. The frontend is
in the middle of a long-running modernization effort: legacy class
components are being converted to function components with hooks, in line
with the rules in this repository's agent-instruction files (`AGENTS.md`,
`CLAUDE.md`, `.cursor/rules/dev-standard.mdc`,
`.github/copilot-instructions.md`).

Three components in the `@superset-ui/core` package's chart-composition
module have not yet been converted:

- `ChartFrame`
- `WithLegend`
- `TooltipFrame`

(All three currently extend React's `PureComponent`.)

Convert these three components from class components to function components
while preserving all observable behavior.

## Required outcome

After your changes, each of the three components must satisfy **all** of
the following:

1. The default export is the result of calling `React.memo(...)` on the
   component (i.e. its runtime `$$typeof` is `Symbol.for('react.memo')`).
   This preserves the shallow-prop bail-out semantics of the previous
   `PureComponent`.
2. The inner component (the value passed to `memo`) is a plain function —
   it must not be a class, and it must not extend `PureComponent` or
   `Component`. (`Component.prototype.isReactComponent` must be undefined.)
3. The source file must no longer import `PureComponent` from `react` and
   must no longer declare a `class <Name>` for any of the three components.
4. Default-prop values previously set via `static defaultProps` should be
   expressed as default values in the destructured function parameters.
5. Existing observable rendering behavior must be preserved:
   - **`ChartFrame`** — when `renderContent` is omitted the component must
     render without throwing. When the requested content fits inside the
     frame the function's return value renders the `renderContent` output
     inline (no scroll wrapper). When `contentWidth` exceeds the frame's
     `width`, the output is wrapped in a `<div>` with `overflow-x: auto`,
     and `renderContent` is invoked with content sized at least as large
     as the requested overflow dimensions.
   - **`TooltipFrame`** — children render inside a `<div>`, and a provided
     `className` prop is applied to that `<div>`.
   - **`WithLegend`** — the outer container has the `with-legend` class.
     When `renderLegend` is provided, a `legend-container` element is
     rendered. With `position="left"` (a horizontal layout), the legend
     direction is `column` (so the rendered legend element should reflect
     `direction: 'column'`).

## Conventions to follow

The repository's agent-instruction files prescribe the following rules.
The relevant ones for this change:

- **Functional components with hooks** — class components are deprecated
  in this codebase.
- **NO `any` types** — do not introduce `: any`, `as any`, or `<any>` in
  your changes.
- **Apache License Header** — these files already carry an ASF license
  header; do not remove it.
- **Avoid time-specific language in comments** — do not add comments that
  use words like "now", "currently", or "today"; comments should be
  timeless.

## Code Style Requirements

- Source files must remain valid TSX (parseable by the TypeScript loader)
  with no syntax errors.
- Do not introduce new `any` types in the three files you touch.

## Notes

- Use React's built-in hooks (`useMemo` etc.) where appropriate to
  preserve memoization behavior that previously came from `PureComponent`
  shallow-prop checks.
- If a `static defaultProps` previously defined `renderContent() {}`
  (returning `undefined`), the function-component equivalent should have
  a default that returns a valid React node so that omitting the prop
  does not cause the renderer to receive `undefined`.
- The diff scope is limited to these three files; do not modify other
  packages, tests, or build configuration.
