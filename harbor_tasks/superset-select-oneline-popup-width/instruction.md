# Match Select dropdown popup width to the collapsed input width in `oneLine` mode

You are working in the Apache Superset frontend monorepo. The relevant
package is `@superset-ui/core`, located at:

```
/workspace/superset/superset-frontend/packages/superset-ui-core/
```

## Symptom

The reusable `<Select>` component in this package supports an `oneLine`
prop. When `oneLine` is enabled together with `mode="multiple"` and the
component already has selected values, opening the dropdown causes the
visible tags to collapse from the per-tag rendering to a single
"+ N ..." overflow indicator on the same line as the input. This
collapse shrinks the rendered width of the select input.

After the tags collapse, the dropdown popup that hangs below the input
keeps its **pre-collapse** width: it is rendered wider than the now-narrower
input, so the popup no longer aligns with the input's right edge. Users
see an obviously misaligned popup.

The expected behavior is that the dropdown popup width tracks the
post-collapse, layout-rendered width of the select input (the bounding
rectangle of the `.ant-select` element inside the component's
container). When the dropdown is closed and reopened, the popup's
inline `style.width` (in pixels) must equal the measured width of the
select input at the moment the tags have just collapsed.

When the dropdown closes, the next time it opens (before tags re-collapse)
the width should reset to the antd default ("match select width" — i.e.
the default boolean popup-width behavior). In other words, the narrowed
inline pixel width is only applied while collapsed; it must not stick
across open/close cycles.

This behavior change must apply **only** to `oneLine` mode. Non-oneLine
multi-select and single-select must continue to use antd's default
"match select width" popup behavior unchanged.

## How to measure the rendered width

JSDOM does not perform real layout, so the grader simulates a real
post-collapse width by mocking `getBoundingClientRect` on the
`.ant-select` element. Your fix must therefore measure the rendered
width via `getBoundingClientRect()` (the standard DOM-layout API) so
that the mocked value flows through. Reading `offsetWidth` /
`clientWidth` will not work under the test harness because those are
not mocked and JSDOM returns 0 for them.

The grader mocks the rectangle to return a positive width and expects
that the dropdown's inline `style.width` (parsed as an integer pixel
value) equals that mocked width — see "Acceptance criteria" below.

## Where the bug lives

The single source-of-truth file for the component is:

```
superset-frontend/packages/superset-ui-core/src/components/Select/Select.tsx
```

The component is a `forwardRef` functional React component. It already
contains a `useEffect` block that runs when `oneLine` is true and
toggles the maximum tag count based on whether the dropdown is visible
— inside the `requestAnimationFrame` callback that switches the tag
count to its collapsed value is the natural place to capture the
post-collapse layout width.

The `<Select>` returns an `AntdSelect` (the underlying antd select)
inside a `StyledContainer`. The antd select already exposes a
mechanism for controlling the popup's pixel width vs. matching the
select width — read `Select.tsx` to find the prop that is currently
hard-coded to the boolean default and replace its value with a
mode-aware expression.

## Acceptance criteria

A correct fix must:

1. In `oneLine` mode, when the dropdown opens and tags collapse to the
   "+ N ..." overflow, measure the layout-rendered width of the
   `.ant-select` element via `getBoundingClientRect()` and propagate
   that pixel width to the popup so its inline `style.width` matches
   exactly (`parseInt(dropdown.style.width, 10) === measuredWidth`).
2. When the dropdown closes, restore the popup width control to its
   default boolean state, so a subsequent open before re-collapse does
   not reuse the previous narrowed pixel width.
3. Leave non-`oneLine` mode behavior **unchanged**: the popup must
   continue to receive the boolean default for popup-width behavior
   when `oneLine` is `false`.
4. Not break any existing test in
   `superset-frontend/packages/superset-ui-core/src/components/Select/Select.test.tsx`.

The bug fix is purely a frontend TypeScript/React change inside
`Select.tsx`. No new files are required.

## Code Style Requirements

This codebase enforces strict TypeScript and frontend conventions
(see `AGENTS.md` and `CLAUDE.md` at the repo root). Your changes must
respect them:

- **No `any` types.** Use proper TypeScript types. If you need to widen,
  prefer a union (e.g., `number | true`) over `any`.
- **Functional components with hooks** — keep the existing
  `forwardRef` + hooks pattern; do not introduce class components.
- **Use `@superset-ui/core`** — do not import directly from `antd` if a
  re-export exists in `@superset-ui/core/components`.
- **Avoid `describe()` blocks for new tests** — prefer flat `test(...)`
  per the repo's testing-strategy guide.
- **Avoid time-specific language** ("now", "currently", "today") in
  code comments — write timeless comments.
- **No new custom CSS** for this fix; the change should be purely
  React state / props plumbing.

## How tests are run

The grader runs `npx jest` from
`/workspace/superset/superset-frontend/` against:

- `packages/superset-ui-core/src/components/Select/Select.benchmark.test.tsx`
  (a separately-injected behavioral test file the grader supplies)
- `packages/superset-ui-core/src/components/Select/Select.test.tsx`
  (the existing 78-test suite, must remain green)
