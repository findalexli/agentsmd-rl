# Update change detection strategy documentation

## Problem

Angular v22 made `OnPush` the default change detection strategy. However, the codebase still contains documentation and configuration that treats `OnPush` as an optional performance optimization and describes the old `Default` strategy (now renamed `Eager`) as the normal behavior.

Specifically:
- The JSDoc comments for the `ChangeDetectionStrategy` enum do not indicate that `OnPush` is now the default
- The JSDoc for the `changeDetection` property on component metadata lacks information about the new default behavior
- Documentation pages describe `OnPush` as something that must be manually enabled
- Documentation pages describe the (now-renamed) `Eager` strategy as the default
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

1. The JSDoc comment immediately above the `OnPush = 0` enum member in `constants.ts` indicates that OnPush is enabled by default

2. The JSDoc comment immediately above the `changeDetection?` property in `directives.ts`:
   - Indicates that OnPush is enabled by default
   - References the `Eager` strategy (the renamed replacement for the old `Default` strategy)

3. The documentation and configuration files no longer describe OnPush as a strategy that must be manually enabled. Specifically:
   - `adev/src/content/best-practices/runtime-performance/skipping-subtrees.md` should describe OnPush as the default (not as a manual setting) — the current version includes a code example with `changeDetection: ChangeDetectionStrategy.OnPush,` showing how to manually set it
   - `adev/src/content/tutorials/signals/steps/1-creating-your-first-signal/README.md` should not have the callout titled "About ChangeDetectionStrategy.OnPush" about manually setting OnPush
   - `adev/src/context/airules.md` currently has the line `changeDetection: ChangeDetectionStrategy.OnPush` telling agents to set OnPush in @Component decorators — this must be removed
   - `adev/src/context/guidelines.md` currently has the line `changeDetection: ChangeDetectionStrategy.OnPush` telling agents to set OnPush in @Component decorators — this must be removed
   - `adev/src/context/angular-20.mdc` currently instructs "Always set `changeDetection: ChangeDetectionStrategy.OnPush`" in components — this must be removed

4. The documentation accurately describes `OnPush` as the default strategy and `Eager` as an optional mode. Specifically:
   - The first mention of `OnPush` in `skipping-subtrees.md` should be in context with the word "default"
   - The first mention of `Eager` in `advanced-configuration.md` should be in context with the word "optional"

Your task is to identify all locations where the documentation contradicts the new default behavior and update them appropriately.
