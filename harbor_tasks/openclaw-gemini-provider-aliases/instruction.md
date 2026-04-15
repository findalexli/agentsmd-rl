# Bug: Gemini 3.1 models fail to resolve for Google provider aliases and flash-lite misclassified as flash

## Problem

Gemini 3.1 models (pro, flash, flash-lite) cannot be resolved when using Google provider aliases like `google-vertex` or `google-gemini-cli`. The forward-compat resolver only works with the direct `google` provider.

Additionally, `gemini-3.1-flash-lite` models are incorrectly resolved as `gemini-3.1-flash` because the flash prefix check runs before the flash-lite check, and "flash-lite" starts with "flash".

## Affected Components

- Extensions for Google provider integration
- Model resolution logic for Gemini 3.1 series
- Template lookup mechanism that should support cross-provider resolution

## Expected Behavior

After the fix, the following test assertions should pass in `extensions/google/provider-models.test.ts`:

1. **Cross-provider resolution for aliases**: When using `google-gemini-cli` as the runtime provider with constant `GOOGLE_GEMINI_CLI_PROVIDER_ID`, the resolver should look up templates from the `google` provider as a fallback. The test "resolves gemini 3.1 pro for alias provider via cross-provider lookup" must pass.

2. **Direct provider resolution**: When using `google` as the provider, the resolver should directly look up templates from that provider. The test "resolves gemini 3.1 flash from direct google templates" must pass.

3. **Prefix ordering for flash-lite**: The resolver must check for `gemini-3.1-flash-lite` before `gemini-3.1-flash` to avoid misclassification. The test "flash-lite models resolve to their own template, not the broader flash prefix" must pass and verify that `gemini-3-flash-preview` is not queried when resolving a flash-lite model.

4. **Runtime provider not hardcoded**: The code must use the actual runtime provider ID (from context) rather than a hardcoded string literal `"google"`.

5. **Template provider fallback**: The resolution function must accept a `templateProviderId` parameter to enable cross-provider template lookup.

## Files to Modify

- `extensions/google/index.ts`
- `extensions/google/provider-models.ts`

The `extensions/google/provider-models.test.ts` test file should contain the test cases named above and must pass when run with `npx vitest run extensions/google/provider-models.test.ts --reporter=verbose`.
