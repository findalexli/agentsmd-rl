# fix(clawhub): sanitize archive temp filenames

## Problem

`openclaw plugins install @scope/name` fails with `ENOENT` during the ClawHub archive download step because scoped package names containing `/` are used directly in the temp file path, creating nested directory paths instead of flat filenames.

## Root Cause

`downloadClawHubPackageArchive()` in `src/infra/clawhub.ts` builds the temp zip path with `path.join(tmpDir, \`${params.name}.zip\`)`. When the package name is scoped (e.g. `@soimy/dingtalk`), the `/` is interpreted as a directory separator, creating `<tmp>/@soimy/dingtalk.zip` which fails because the intermediate directory does not exist.

The same issue affects `downloadClawHubSkillArchive()` with slash-containing skill slugs like `ops/calendar`.

## Expected Fix

Use the existing `safeDirName()` helper (from `src/infra/install-safe-path.ts`) to sanitize the package name and skill slug before constructing the temp zip filename. This replaces slashes with double underscores (e.g. `@soimy/dingtalk` becomes `@soimy__dingtalk`).

Apply the fix in both:
1. `downloadClawHubPackageArchive` -- for `params.name`
2. `downloadClawHubSkillArchive` -- for `params.slug`

## Files to Modify

- `src/infra/clawhub.ts`
