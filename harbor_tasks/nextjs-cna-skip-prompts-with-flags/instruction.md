# Bug: `create-next-app` enters interactive mode even when CLI flags are provided

## Summary

When users (or AI agents) run `create-next-app` with explicit configuration flags like `--typescript --tailwind --app --src-dir`, the CLI still drops into interactive mode and prompts for every option that wasn't explicitly provided. For example:

```
npx create-next-app my-app --typescript --tailwind --eslint --app --src-dir --use-pnpm
✔ Would you like to use React Compiler? … No / Yes
✔ Would you like to customize the import alias (`@/*` by default)? … No / Yes
? Would you like to include AGENTS.md? › No / Yes
```

This is a significant problem for non-interactive callers (CI pipelines, AI agents, scripts) because they cannot always answer interactive prompts. When they fail to navigate the prompts, they fall back to scaffolding the project from scratch using stale patterns.

## Expected Behavior

When any configuration flags are explicitly provided on the command line, the CLI should **skip all interactive prompts** and use the recommended defaults for any unspecified options. It should also print a summary of which defaults were assumed, so the caller knows what flags to pass to override them.

The `--yes` flag and CI-mode behavior should remain unchanged.

## Relevant Code

The main CLI logic is in `packages/create-next-app/index.ts`, in the `run()` function. Look at:

- The `hasProvidedOptions` variable (around line 320) which detects if any `--` flags were passed
- The `skipPrompt` variable that controls whether interactive prompts are shown
- The `displayConfig` array (around line 253) which maps option keys to their display labels

Currently, `hasProvidedOptions` only skips the initial "use recommended defaults?" meta-prompt but still shows individual prompts for each missing option.

## Hints

- The fix should be contained to `packages/create-next-app/index.ts`
- The `displayConfig` array has the information needed to generate a summary of assumed defaults
- Consider what flags a user could pass to override each default
