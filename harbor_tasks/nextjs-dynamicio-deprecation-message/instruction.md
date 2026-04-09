# Improve error message for deprecated `experimental.dynamicIO` config

## Problem

When a developer upgrades Next.js and has `experimental.dynamicIO` in their `next.config` file, they see only a generic "Unrecognized key(s) in object: 'dynamicIO'" warning. There is no guidance on what replaced it or what to use instead, forcing them to search through documentation and changelogs.

Other deprecated experimental config keys like `turbopackPersistentCaching` already have specific, actionable error messages that point to their replacements. The `dynamicIO` key is missing this treatment.

## Expected Behavior

When `experimental.dynamicIO` is present in the config, the validation should produce a **fatal error** (not just a warning) with a clear message explaining that `dynamicIO` has been replaced, what to use instead, and a link to the relevant documentation.

## Files to Look At

- `packages/next/src/server/config.ts` — contains `normalizeNextConfigZodErrors`, which processes Zod validation errors for the Next.js config and provides specific migration guidance for deprecated experimental keys
