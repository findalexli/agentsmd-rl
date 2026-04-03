# Update change detection strategy references

## Problem

Angular v22 made `OnPush` the default change detection strategy, but the codebase still has documentation and configuration that treats `OnPush` as an optional performance optimization that developers must explicitly set. This includes:

- JSDoc comments in the core framework source (`packages/core/src/change_detection/constants.ts` and `packages/core/src/metadata/directives.ts`) that don't mention OnPush is now the default
- Documentation pages under `adev/src/content/` that describe OnPush as optional and show code snippets for manually enabling it
- AI/agent configuration files under `adev/src/context/` that still instruct agents to "Set `changeDetection: ChangeDetectionStrategy.OnPush` in `@Component` decorator" — this is now unnecessary and misleading since it's the default

## Expected Behavior

All references to the change detection strategy should be updated to reflect that `OnPush` is now the default:

1. **Core source JSDoc**: The `OnPush` enum member and `changeDetection` property should have notes indicating OnPush is the default. The old `Default` strategy reference should be updated to use `Eager`.
2. **Documentation**: Pages explaining change detection should describe OnPush as the default strategy (since v22), not as an optional optimization. Code examples showing how to manually set OnPush should be removed. References to the old "default" strategy should use `Eager`.
3. **Agent config files**: Rules instructing AI agents to always set OnPush should be removed, since it's now the default behavior.

## Files to Look At

- `packages/core/src/change_detection/constants.ts` — `ChangeDetectionStrategy` enum definition
- `packages/core/src/metadata/directives.ts` — `changeDetection` property JSDoc on `Component` interface
- `adev/src/content/best-practices/runtime-performance/skipping-subtrees.md` — change detection best practices guide
- `adev/src/content/guide/components/advanced-configuration.md` — component configuration docs
- `adev/src/context/airules.md` — AI rules configuration
- `adev/src/context/guidelines.md` — coding guidelines for AI agents
- `adev/src/context/angular-20.mdc` — Angular 20 best practices for AI agents
- `adev/src/content/tutorials/signals/steps/1-creating-your-first-signal/README.md` — signals tutorial
