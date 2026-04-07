# Add User Usage View to Usage Page

## Problem

The usage page dropdown has view options for tags, teams, organizations, customers, and agents — but there is no way to view usage broken down by individual users. Admins need per-user spend tracking alongside the existing entity views.

Additionally, the `UsageExportHeader` filter component always renders a multi-select dropdown, but some backend endpoints (like the user daily activity endpoint) accept only a single value, not an array. This causes silently dropped selections when filtering by user.

## Expected Behavior

1. A "User Usage" option should appear in the usage page view selector (admin-only).
2. Selecting it should load spend data via the existing `userDailyActivityCall` endpoint.
3. The `UsageExportHeader` component should support both single-select and multi-select filter modes so that entity types backed by single-value endpoints get a single-select dropdown.
4. The `EntityType` type definition should include `"user"`.

After making the code changes, update the project's agent instruction files to document these patterns as pitfalls for future contributors:
- Add a pitfall about UI/backend contract mismatch (single value vs array) to the existing pitfalls section.
- Add a pitfall about always adding tests for new entity types.
- Update CLAUDE.md with a rule about testing new entity types and a section about UI/backend consistency.

## Files to Look At

- `ui/litellm-dashboard/src/components/EntityUsageExport/types.ts` — EntityType type definition
- `ui/litellm-dashboard/src/components/EntityUsageExport/UsageExportHeader.tsx` — shared filter header component
- `ui/litellm-dashboard/src/components/UsagePage/components/EntityUsage/EntityUsage.tsx` — entity spend view
- `ui/litellm-dashboard/src/components/UsagePage/components/UsageViewSelect/UsageViewSelect.tsx` — view selector dropdown
- `ui/litellm-dashboard/src/components/UsagePage/components/UsagePageView.tsx` — main usage page layout
- `AGENTS.md` — common pitfalls section
- `CLAUDE.md` — testing rules and development notes
