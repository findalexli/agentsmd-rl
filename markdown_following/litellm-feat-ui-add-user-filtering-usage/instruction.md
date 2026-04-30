# Add User Usage View to Usage Page

## Problem

The usage page dropdown has view options for tags, teams, organizations, customers, and agents — but there is no way to view usage broken down by individual users. Admins need per-user spend tracking alongside the existing entity views.

Additionally, the filter header component always renders a multi-select dropdown, but some backend endpoints (like the user daily activity endpoint) accept only a single value, not an array. This causes silently dropped selections when filtering by user.

## Expected Behavior

1. A "User Usage" option should appear in the usage page view selector (admin-only).
2. Selecting it should load spend data via the existing `userDailyActivityCall` endpoint.
3. The filter header component should support both single-select and multi-select filter modes so that entity types backed by single-value endpoints get a single-select dropdown.
4. The `EntityType` type definition should include `"user"`.

After making the code changes, update the project agent instruction files to document these patterns as pitfalls for future contributors:
- Add a pitfall about UI/backend contract mismatch (single value vs array) to the existing pitfalls section. The pitfall should warn about "silently dropping" user selections.
- Add a pitfall about always adding tests for new entity types.
- Update CLAUDE.md with a rule about testing new entity types and a section about UI/backend consistency. The rule should state to "always add tests" when adding new entity types or features.

## Code Style Requirements

- The project uses TypeScript with React. All new UI components must pass TypeScript type checking (`tsc --noEmit`).
- Follow existing patterns in the codebase for component props, API call wiring, and test file conventions.
- Component tests use Vitest with React Testing Library.
