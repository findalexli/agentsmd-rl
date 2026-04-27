# Make the team filter on the Usage page searchable

The LiteLLM admin dashboard's Usage page exposes a "Team Usage" tab where users
filter daily activity by team. The current filter on that tab is a static
dropdown that loads every team up-front and offers **no text search**, so users
on a deployment with many teams have to scroll through the entire list to find
the team they want — and worse, they cannot search by team ID at all.

## What's wrong

When `entityType === "team"` on the Usage page, the filter that the user sees
is the legacy `UsageExportHeader` filter, which is fed by an unpaginated
upstream call and rendered as a plain Ant Design `Select` with **no search,
no pagination, and no debounce**. As a result:

- Typing into the dropdown does nothing useful (no filtering of options).
- Teams are limited to whatever the unpaginated `/team/list` returned.
- Users cannot find a team by **team ID**, only by visual scroll.

For other entity types (`tag`, `organization`, `customer`, `agent`, `user`),
the existing filter UI is fine and **must not change**.

## What we want

When `entityType === "team"`:

1. The legacy filter UI provided by `UsageExportHeader` for the team case
   must be **disabled** (the existing label / placeholder logic for
   `entityType !== "team"` is unchanged).
2. A new filter must appear above the export header. It must:
   - Be labelled exactly **`Filter by team`** (visible to the user).
   - Be a **multi-select** (users select more than one team) backed by an
     **Ant Design `<Select>`** with `mode="multiple"` so the rendered
     element carries the `ant-select-multiple` CSS class.
   - Show a real text input inside the selector (i.e. `showSearch` is on,
     so the rendered DOM contains an
     `.ant-select-multiple .ant-select-selection-search-input` element).
   - Use the project's **paginated, debounced infinite-scroll teams hook**
     `useInfiniteTeams` from `@/app/(dashboard)/hooks/teams/useTeams` for
     server-side search, with the page size passed through as the **first
     positional argument** to that hook (so callers can configure it via a
     `pageSize` prop, default `20`).
   - Display each team option using the team's alias (the visible label) —
     mocked teams `Alpha Team` and `Bravo Team` must appear in the rendered
     popup options when supplied to the hook.
   - Default placeholder text containing the literal phrase
     `Search teams by alias...` (that exact substring must be present in
     the rendered DOM somewhere — e.g. in the `placeholder` of the search
     input).
   - Reuse the project's currently selected team IDs (the existing
     `selectedTags` state on `EntityUsage`) for `value`, and call back to
     the existing `setSelectedTags` setter on change.

3. The new selector should live as a reusable component in the
   dashboard's common-component layer (it is needed only here today, but
   following the project convention for shared, framework-agnostic UI
   pieces makes it discoverable for future callers).

## Where to write code

- The wiring change goes in
  `ui/litellm-dashboard/src/components/UsagePage/components/EntityUsage/EntityUsage.tsx`.
  This is acceptable to disclose because the localisation is part of the
  symptom: the existing test file
  `EntityUsage.test.tsx` already exercises this component for every entity
  type, and the bug is specifically about the team branch of its render.

You may add new files as you see fit. Do **not** introduce new top-level
dependencies — every package you need (`antd`, `@ant-design/icons`,
`@tanstack/react-pacer`, `react`) is already in `package.json` at the
base commit.

## Constraints

- The change is purely UI; do not touch any backend code, networking
  module, or unrelated component.
- Existing UsagePage behaviour for `entityType !== "team"` (tag / org /
  customer / agent / user) **must remain identical** — all 23 tests in
  `EntityUsage.test.tsx` must still pass.
- The single-select `team_dropdown.tsx` component is in use elsewhere
  and **must remain a single-select** (it must not gain
  `mode="multiple"`).
- Do **not** import any `@tremor/...` modules in any new component file
  you create. Tremor is deprecated for new UI work in this repo.
- Place any new shared component under
  `ui/litellm-dashboard/src/components/common_components/` to follow the
  project's "use common components" convention from `AGENTS.md`.

## Code Style Requirements

The dashboard uses `prettier` and `eslint` (see `package.json` scripts
`format` and `lint`). New code should follow the existing TypeScript
conventions in `team_dropdown.tsx`, which serves as a close stylistic
reference for the single-select sibling of this multi-select.
