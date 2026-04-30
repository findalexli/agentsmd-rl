# Skill

Source: [vercel/flags#277](https://github.com/vercel/flags/pull/277)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `skills/flags-sdk/SKILL.md`
- `skills/flags-sdk/references/api.md`
- `skills/flags-sdk/references/nextjs.md`
- `skills/flags-sdk/references/providers.md`
- `skills/flags-sdk/references/sveltekit.md`

## What to add / change

This pull request adds comprehensive documentation for the Flags SDK, including a high-level guide and a detailed API reference. The new documentation covers core concepts, usage patterns, framework integrations, and the full API surface for the Flags SDK and its related packages.

**Major documentation additions:**

*General usage and conceptual documentation:*

- Added `SKILL.md` in `skills/flags-sdk`, providing an in-depth guide to using the Flags SDK (`flags` npm package). This includes explanations of declaring feature flags, server-side evaluation, the adapter pattern, precompute patterns for static pages, evaluation context setup, integrating with the Flags Explorer, framework-specific usage (Next.js and SvelteKit), writing custom adapters, encryption functions, and React component integration.

*API reference documentation:*

- Added `references/api.md` in `skills/flags-sdk`, documenting the complete API for the Flags SDK and its subpackages. The reference covers core utilities (`verifyAccess`, `mergeProviderData`, `reportValue`, encryption helpers, etc.), React components (`FlagValues`, `FlagDefinitions`), Next.js and SvelteKit integrations (flag declaration, precompute, dedupe, provider data, etc.), and all relevant parameters and usage patterns.

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
