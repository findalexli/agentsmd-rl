# Improve error message for deprecated `experimental.dynamicIO` config

## Problem

When a developer upgrades Next.js and has `experimental.dynamicIO` in their `next.config` file, they see only a generic "Unrecognized key(s) in object: 'dynamicIO'" warning. There is no guidance on what replaced it or what to use instead, forcing them to search through documentation and changelogs.

Other deprecated experimental config keys already have specific, actionable error messages that point to their replacements. For example, `turbopackPersistentCaching` produces a fatal error suggesting the user switch to `turbopackFileSystemCacheForDev`. The `dynamicIO` key is missing this treatment.

## Expected Behavior

The `normalizeNextConfigZodErrors` function in `packages/next/src/server/config.ts` processes Zod validation errors for the Next.js config. It should be updated so that:

1. When `experimental.dynamicIO` is present in the config, the validation produces a **fatal error** (not a warning). The `dynamicIO` key should appear in `fatalErrors`, not `warnings`.
2. The fatal error message must mention `cacheComponents` as the feature that replaced `dynamicIO`.
3. The fatal error message must include a link to the relevant documentation: `https://nextjs.org/docs/app/api-reference/config/next-config-js/cacheComponents`
4. The existing behavior for `turbopackPersistentCaching` must be preserved — it should still produce a fatal error whose message mentions `turbopackFileSystemCacheForDev`.
5. Generic unrecognized keys (i.e., any key that is not explicitly handled) should continue to produce only **warnings**, not fatal errors.

## Files to Look At

- `packages/next/src/server/config.ts` — contains `normalizeNextConfigZodErrors`, which processes Zod validation errors for the Next.js config and provides specific migration guidance for deprecated experimental keys
