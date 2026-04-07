## Bug: useActionSWR auto-fetches on mount and breaks shared loading state

The `useActionSWR` hook in `src/libs/swr/index.ts` currently uses `useSWRMutation`, which causes two problems:

1. **Auto-fetch on mount**: When the SWR cache is empty and a component mounts, the hook triggers an unwanted fetch request. Even with `revalidateOnMount: false`, `useSWR` will auto-fetch when the cache is empty.
2. **No shared loading state**: `useSWRMutation`'s `isMutating` state is per-hook-instance, not shared globally by SWR key. This means multiple components using the same key (e.g., the "create agent" button and the "+" button in the header) don't share loading state.

The fix should switch `useActionSWR` to use `useSWR` with `fallbackData` set to an empty object, so SWR thinks initial data exists and won't auto-fetch on mount. Combined with `revalidateOnMount: false`, this prevents auto-fetch while preserving shared `isValidating` state across components.

Also, the project's `CLAUDE.md` has a large inline section for Linear issue management rules. This should be extracted into a separate `.cursor/rules/linear.mdc` file (following the pattern of other rules in `.cursor/rules/`), with `CLAUDE.md` just containing a reference to it. Keep the section heading but replace the full rules with a single line pointing to the external file.

The comments in the SWR module should be in English only -- remove any non-English comments and translate them if needed.
