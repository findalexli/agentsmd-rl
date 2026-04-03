# Remove hosted key support for Google Maps Speed Limits operation

## Problem

The Google Maps Speed Limits operation uses the Roads API, which Google has deprecated. New API keys no longer have permission to access this endpoint. Despite this, the speed limits tool (`apps/sim/tools/google_maps/speed_limits.ts`) still has a `hosting` configuration, meaning Sim tries to provide its own hosted key for speed limit requests — which will always fail since the hosted keys can't access the deprecated API.

Additionally, the block config (`apps/sim/blocks/blocks/google_maps.ts`) hides the API key field when hosted mode is active, which means users selecting the Speed Limits operation see no way to enter their own key (even though they must provide one for this operation).

## Expected Behavior

- The speed limits tool should **not** have hosted key support — users must always provide their own API key for this operation.
- When a user selects the Speed Limits operation, the API key field should always be visible (not hidden by hosted mode).
- All other Google Maps operations should continue to work with hosted keys as before.
- The project's skill documentation for adding hosted keys (`.cursor/skills/add-hosted-key/SKILL.md`) should be updated to document this pattern of excluding specific operations from hosted key support, so future developers know how to handle similar cases.

## Files to Look At

- `apps/sim/tools/google_maps/speed_limits.ts` — tool definition with the hosted key config that should be removed
- `apps/sim/blocks/blocks/google_maps.ts` — block config where the API key subblock visibility needs to be conditional per operation
- `.cursor/skills/add-hosted-key/SKILL.md` — skill guide for adding hosted keys; should document the exclusion pattern
