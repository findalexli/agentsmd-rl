# Update change detection strategy documentation

## Problem

Angular v22 made `OnPush` the default change detection strategy. However, the codebase still contains documentation and configuration that treats `OnPush` as an optional performance optimization and describes `Default`/`Eager` as the normal behavior.

Specifically:
- The JSDoc comments for the `ChangeDetectionStrategy` enum do not indicate that `OnPush` is now the default
- The JSDoc for the `changeDetection` property on component metadata lacks information about the new default behavior and the relationship to the `Eager` strategy
- Documentation pages describe `OnPush` as something that must be manually enabled and show code examples for setting it
- Documentation pages describe `Eager` as the default strategy when it should be described as optional
- AI agent configuration files contain rules instructing agents to always set `OnPush` in component decorators

## Affected Files

The following files need review and possible updates to align with the new default behavior:

- `packages/core/src/change_detection/constants.ts` — `ChangeDetectionStrategy` enum definition with JSDoc comments
- `packages/core/src/metadata/directives.ts` — `Component` interface with `changeDetection` property JSDoc
- `adev/src/content/best-practices/runtime-performance/skipping-subtrees.md` — change detection best practices guide
- `adev/src/content/guide/components/advanced-configuration.md` — component configuration docs
- `adev/src/context/airules.md` — AI rules configuration
- `adev/src/context/guidelines.md` — coding guidelines for AI agents
- `adev/src/context/angular-20.mdc` — Angular 20 best practices for AI agents
- `adev/src/content/tutorials/signals/steps/1-creating-your-first-signal/README.md` — signals tutorial

## Expected Behavior After Fix

When the updates are complete, the codebase should reflect that `OnPush` is the default change detection strategy (as of Angular v22). The tests will verify:

1. The JSDoc comment immediately above the `OnPush = 0` enum member in `constants.ts` contains the exact text: `OnPush is enabled by default`

2. The JSDoc comment immediately above the `changeDetection?` property in `directives.ts`:
   - Contains the exact text: `OnPush is enabled by default`
   - References `ChangeDetectionStrategy#Eager` (the text "Eager" must appear)

3. The following string patterns do NOT appear in the specified files:
   - `adev/src/content/best-practices/runtime-performance/skipping-subtrees.md`: `ChangeDetectionStrategy.OnPush,`
   - `adev/src/content/tutorials/signals/steps/1-creating-your-first-signal/README.md`: `About ChangeDetectionStrategy.OnPush`
   - `adev/src/context/airules.md`: `changeDetection: ChangeDetectionStrategy.OnPush`
   - `adev/src/context/guidelines.md`: `changeDetection: ChangeDetectionStrategy.OnPush`
   - `adev/src/context/angular-20.mdc`: `Always set \`changeDetection: ChangeDetectionStrategy.OnPush\``

4. The documentation accurately describes `OnPush` as the default strategy and `Eager` as an optional mode. Specifically:
   - The first mention of `OnPush` in `skipping-subtrees.md` occurs near the word "default"
   - The first mention of `Eager` in `advanced-configuration.md` occurs near the word "optional"

Your task is to identify all locations where the documentation contradicts the new default behavior and update them appropriately. The tests will verify the expected content is present and the deprecated patterns have been removed.
