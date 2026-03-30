# fix(google): resolve Gemini 3.1 models for all Google provider aliases

## Problem

Gemini 3.1 models (pro, flash, flash-lite) cannot be resolved when using Google provider aliases like `google-vertex` or `google-gemini-cli`. The forward-compat resolver only works with the direct `google` provider.

Additionally, `gemini-3.1-flash-lite` is misclassified as `gemini-3.1-flash` because the flash prefix check runs before the flash-lite check.

## Root Cause

1. `resolveGoogle31ForwardCompatModel()` in `extensions/google/provider-models.ts` is called with a hardcoded `providerId: "google"` from `extensions/google/index.ts`. When users configure `google-vertex` or other aliases, the template lookup fails because no templates exist under that provider ID.

2. The prefix ordering checks `gemini-3.1-flash` before `gemini-3.1-flash-lite`. Since `gemini-3.1-flash-lite` starts with `gemini-3.1-flash`, it matches the wrong branch.

## Expected Fix

1. In `extensions/google/index.ts`, pass the actual runtime `ctx.provider` ID instead of hardcoded `"google"`, and add a `templateProviderId` fallback for cross-provider template resolution.
2. In `extensions/google/provider-models.ts`:
   - Add a `templateProviderId` parameter to `resolveGoogle31ForwardCompatModel`
   - Create a helper that tries template lookup first with the actual provider ID, then falls back to the template provider ID
   - Fix prefix ordering: check `gemini-3.1-flash-lite` before `gemini-3.1-flash`

## Files to Modify

- `extensions/google/index.ts`
- `extensions/google/provider-models.ts`
