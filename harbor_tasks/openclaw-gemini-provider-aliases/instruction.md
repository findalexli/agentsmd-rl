# Bug: Gemini 3.1 models fail to resolve for Google provider aliases and flash-lite misclassified as flash

## Problem

When using Google provider aliases like `google-vertex` or `google-gemini-cli`, Gemini 3.1 models cannot be resolved. The forward-compat resolver only works when the runtime provider is exactly `google`, causing model resolution to fail for aliased providers.

Additionally, `gemini-3.1-flash-lite` models are incorrectly resolved as `gemini-3.1-flash`. The current prefix matching checks for "flash" before "flash-lite", and since "flash-lite" starts with "flash", flash-lite models get matched to the wrong template.

## Affected Components

- Extensions for Google provider integration
- Model resolution logic for Gemini 3.1 series
- Template lookup mechanism that should support cross-provider resolution

## Expected Behavior

The following test assertions must pass in `extensions/google/provider-models.test.ts` when run with `npx vitest run extensions/google/provider-models.test.ts --reporter=verbose`:

1. **Cross-provider resolution for aliases**: When the runtime provider is an alias (like `google-gemini-cli`), the resolver should look up templates from the `google` provider as a fallback. The test named "resolves gemini 3.1 pro for alias provider via cross-provider lookup" must pass.

2. **Direct provider resolution**: When the runtime provider is `google`, the resolver should directly look up templates from that provider. The test named "resolves gemini 3.1 flash from direct google templates" must pass.

3. **Prefix ordering for flash-lite**: The resolver must correctly distinguish `gemini-3.1-flash-lite` from `gemini-3.1-flash`. The test named "flash-lite models resolve to their own template, not the broader flash prefix" must pass. This test verifies that `gemini-3-flash-preview` is NOT queried when resolving a `gemini-3.1-flash-lite-preview-001` model.

4. **Runtime provider from context**: The resolver must use the actual runtime provider ID from the resolution context rather than a hardcoded string literal.

5. **Template provider fallback parameter**: The resolution function must accept a parameter enabling cross-provider template lookup.

## Required Test Coverage

The test file `extensions/google/provider-models.test.ts` must exist and contain tests covering:
- Resolution of `gemini-3.1-pro-preview` via cross-provider lookup when runtime provider is `google-gemini-cli` and fallback provider is `google`
- Resolution of `gemini-3.1-flash-preview` from direct `google` provider templates
- Correct resolution of `gemini-3.1-flash-lite-preview-001` to its own template without querying `gemini-3-flash-preview`
- Return of `undefined` for non-matching model IDs like `some-other-model`

## Specific Values and Constraints

- The constant `GOOGLE_GEMINI_CLI_PROVIDER_ID` must be used in the implementation to represent the `google-gemini-cli` provider
- The model IDs that must be recognized:
  - `gemini-3.1-pro` (prefix for pro models)
  - `gemini-3.1-flash-lite` (prefix for flash-lite models)
  - `gemini-3.1-flash` (prefix for flash models)
- Template IDs to query:
  - For pro: `gemini-3-pro-preview`
  - For flash-lite: `gemini-3.1-flash-lite-preview`
  - For flash: `gemini-3-flash-preview`

## Files Context

The bug exists within the Google extensions. The relevant modules are in the `extensions/google/` directory and handle model resolution for the Google provider and its aliases.
