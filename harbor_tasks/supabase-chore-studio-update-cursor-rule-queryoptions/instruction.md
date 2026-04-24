# Refactor third-party auth integrations query to use `queryOptions` pattern

## Problem

The `apps/studio/data/third-party-auth/integrations-query.ts` file uses the old `useXQuery()` custom hook wrapper pattern for React Query data fetching. This pattern is being phased out in favor of TanStack Query v5's `queryOptions` factory, which provides better type inference, reusability (works with both `useQuery()` in components and `queryClient.fetchQuery()` for imperative fetching), and simplicity.

The current `useThirdPartyAuthIntegrationsQuery` hook wraps `useQuery` with custom generics and spreads `UseCustomQueryOptions`. The internal fetch function `getThirdPartyAuthIntegrations` is unnecessarily exported.

## Expected Behavior

1. **Refactor the query file** (`apps/studio/data/third-party-auth/integrations-query.ts`):
   - Replace the `useThirdPartyAuthIntegrationsQuery` custom hook with a `thirdPartyAuthIntegrationsQueryOptions` factory function that uses `queryOptions` from `@tanstack/react-query`
   - Make the internal `getThirdPartyAuthIntegrations` fetch function private (not exported)
   - Update type naming to follow the new convention (prefix with domain name)
   - Add an explicit error type export

2. **Update the component** (`apps/studio/components/interfaces/Auth/ThirdPartyAuthForm/index.tsx`) to use `useQuery(thirdPartyAuthIntegrationsQueryOptions(...))` directly instead of the old custom hook.

3. **Mark the legacy `UseCustomMutationOptions` type as deprecated** in `apps/studio/types/react-query.ts` since the new pattern doesn't need custom wrapper types.

4. **Update the Cursor rule** at `.cursor/rules/studio/queries/RULE.md` to recommend the `queryOptions` pattern. The rule should:
   - Replace the "Write a query hook" section with guidance on writing query options
   - Include a complete template showing the `queryOptions` factory pattern
   - Add documentation for using query options in components (with `useQuery`)
   - Add documentation for imperative fetching (with `queryClient.fetchQuery()`)
   - Update example file references to point to a file that uses the new pattern

## Files to Look At

- `apps/studio/data/third-party-auth/integrations-query.ts` — the query module to refactor
- `apps/studio/components/interfaces/Auth/ThirdPartyAuthForm/index.tsx` — component consuming the query
- `apps/studio/types/react-query.ts` — shared React Query type helpers
- `.cursor/rules/studio/queries/RULE.md` — Cursor rule for studio data fetching conventions

## Code Style Requirements

Your solution will be checked by the repository's existing linters/formatters. All modified files must pass:

- `prettier (JS/TS/JSON/Markdown formatter)`
