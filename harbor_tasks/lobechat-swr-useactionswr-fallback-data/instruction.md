## Bug: useActionSWR auto-fetches on mount and breaks shared loading state

The `useActionSWR` hook in `src/libs/swr/index.ts` currently has two problems:

1. **Unnecessary fetch on mount**: When the SWR cache is empty and a component mounts, the hook triggers an unwanted network request. This causes issues especially for actions like "create agent" where the button and header use the same key but shouldn't each trigger their own fetch.

2. **No shared loading state**: The loading state is per-hook-instance, not shared globally by SWR key. This means multiple components using the same key don't share the same loading indicator.

The fix must:
- Prevent unnecessary network requests when a component mounts with an empty cache, while still sharing loading state across components that use the same key
- All comments in the SWR module must be written in English only (no Chinese characters)

---

## CLAUDE.md Restructuring

The project's `CLAUDE.md` currently contains a large inline section for Linear issue management rules. This should be refactored:

1. Create a new file at `.cursor/rules/linear.mdc` containing the Linear issue management rules
2. The new file must include:
   - Frontmatter with `alwaysApply: true`
   - A heading containing the text "Linear Issue Management"
   - A section titled "Completion Comment"
   - A section titled "Per-Issue Completion Rule"
   - A reference to "In Review" status
3. Update `CLAUDE.md` to reference `.cursor/rules/linear.mdc` instead of containing the full rules inline
4. `CLAUDE.md` must NOT contain the strings "Retrieve issue details" or "Per-Issue Completion Rule" after the restructure
5. Keep the section heading in `CLAUDE.md` but replace the full rules with a single line pointing to the external file

Follow the pattern of other rule files in `.cursor/rules/` (if they exist) for the frontmatter format.

## Code Style Requirements

Your solution will be checked by the repository's existing linters/formatters. All modified files must pass:

- `prettier (JS/TS/JSON/Markdown formatter)`
- `eslint (JS/TS linter)`
