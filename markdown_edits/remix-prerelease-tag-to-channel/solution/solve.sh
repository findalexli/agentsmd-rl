#!/usr/bin/env bash
set -euo pipefail

cd /workspace/remix

# Idempotent: skip if already applied
if grep -q '"channel"' packages/remix/.changes/prerelease.json 2>/dev/null; then
    echo "Patch already applied."
    exit 0
fi

git apply - <<'PATCH'
diff --git a/AGENTS.md b/AGENTS.md
index 3e4f423a37b..f3c1acd66dc 100644
--- a/AGENTS.md
+++ b/AGENTS.md
@@ -49,9 +49,9 @@
   - For **v1.x+ packages**: Use standard semver - "major" for breaking changes, "minor" for new features, "patch" for bug fixes.
   - **Breaking changes are relative to main**: If you introduce a new API in a PR and then change it within the same PR before merging, that's not considered a breaking change.
   - _For the `remix` package only:_
-    - **Prelease mode**: An optional `.changes/prerelease.json` file denotes that the package is in prerelease mode and what the npm dist-tag is. **This is only supported for the `remix` package.**
+    - **Prerelease mode**: An optional `.changes/prerelease.json` file denotes that the package is in prerelease mode. The `channel` field (e.g. `"alpha"`, `"beta"`, `"rc"`) determines the version suffix, while the npm dist-tag is always `"next"`. **This is only supported for the `remix` package.**
     - **Bumping prerelease versions**: You can use normal change files. These will bump the prerelease counter (e.g. `3.0.0-alpha.1` → `3.0.0-alpha.2`). Changelog entries still get proper Major/Minor/Patch sections, but otherwise the bump type is ignored and only the prerelease counter is bumped.
-    - **Transitioning between prerelease tags** (e.g. `alpha` → `beta`): Update `prerelease.json` tag and add a change file. Version resets to new tag (e.g. `3.0.0-alpha.7` → `3.0.0-beta.0`). The bump type is for changelog categorization only—by convention, use `patch`.
+    - **Transitioning between prerelease channels** (e.g. `alpha` → `beta`): Update `prerelease.json` channel and add a change file. Version resets to new channel (e.g. `3.0.0-alpha.7` → `3.0.0-beta.0`). The bump type is for changelog categorization only—by convention, use `patch`.
     - **Graduating from prerelease to latest stable version**: Delete `prerelease.json` and add a change file. The prerelease suffix will be stripped (e.g. `3.0.0-rc.7` → `3.0.0`). The bump type is for changelog categorization only—by convention, use `major` for a major release announcement.
 - **Validating changes**: `pnpm changes:validate` checks that all change files follow the correct naming convention and format.
 - **Previewing releases**: `pnpm changes:preview` shows which packages will be released, what the CHANGELOG will look like, and the commit message.
diff --git a/CONTRIBUTING.md b/CONTRIBUTING.md
index 28dbb1ba02c..709044cd25a 100644
--- a/CONTRIBUTING.md
+++ b/CONTRIBUTING.md
@@ -132,24 +132,24 @@ The `remix` package supports prerelease mode via an optional `.changes/prereleas

 ```json
 {
-  "tag": "alpha"
+  "channel": "alpha"
 }
 ```

-This is only supported for `remix` because it's the only package that needs to publish prereleases alongside an existing stable version on npm. All other packages in this monorepo are new and publish directly as `latest`.
+The `channel` field determines the version suffix (e.g. `alpha`, `beta`, `rc`), while prereleases are always published to npm with the `next` tag. This is only supported for `remix` because it's the only package that needs to publish prereleases alongside an existing stable version on npm. All other packages in this monorepo are new and publish directly as `latest`.

 #### Bumping `remix` prerelease versions

 While in prerelease mode, add change files as normal. The prerelease counter increments (e.g. `3.0.0-alpha.1` → `3.0.0-alpha.2`). Changelog entries still get proper "Major Changes" / "Minor Changes" / "Patch Changes" sections, but the bump type is otherwise ignored—only the prerelease counter is bumped.

-#### Transitioning between `remix` prerelease tags
+#### Transitioning between `remix` prerelease channels

-To transition between tags (e.g. `alpha` → `beta`):
+To transition between channels (e.g. `alpha` → `beta`):

-1. Update `.changes/prerelease.json` to the new tag
+1. Update `.changes/prerelease.json` to the new channel
 2. Add a change file describing the transition

-Version resets to the new tag (e.g. `3.0.0-alpha.7` → `3.0.0-beta.0`). The bump type is for changelog categorization only—by convention, use `patch`.
+Version resets to the new channel (e.g. `3.0.0-alpha.7` → `3.0.0-beta.0`). The bump type is for changelog categorization only—by convention, use `patch`.

 #### Graduating `remix` to stable

diff --git a/packages/remix/.changes/prerelease.json b/packages/remix/.changes/prerelease.json
index 54ae57930a4..bbf2eb32a29 100644
--- a/packages/remix/.changes/prerelease.json
+++ b/packages/remix/.changes/prerelease.json
@@ -1,3 +1,3 @@
 {
-  "tag": "alpha"
+  "channel": "alpha"
 }
diff --git a/scripts/publish.ts b/scripts/publish.ts
index da282932bc0..500200c495d 100644
--- a/scripts/publish.ts
+++ b/scripts/publish.ts
@@ -4,7 +4,7 @@
  * This script uses pnpm publish with --report-summary, reads the summary file,
  * and creates Git tags + GitHub releases. When the remix package is in prerelease
  * mode (has .changes/prerelease.json), it publishes in two phases: all other
- * packages as "latest", then remix with its prerelease tag (e.g., "alpha").
+ * packages as "latest", then remix with the "next" tag.
  *
  * This script is designed for CI use. For previewing releases, use `pnpm changes:preview`.
  *
@@ -196,19 +196,16 @@ async function main() {

   // Check if remix is in prerelease mode
   let remixPrereleaseConfig = readRemixPrereleaseConfig()
-  let remixPrereleaseTag: string | null = null
+  let remixPrereleaseChannel: string | null = null

   if (remixPrereleaseConfig.exists) {
     if (!remixPrereleaseConfig.valid) {
       console.error('Error reading remix prerelease config:', remixPrereleaseConfig.error)
       process.exit(1)
     }
-    remixPrereleaseTag = remixPrereleaseConfig.config.tag
-    console.log(`Remix is in prerelease mode (tag: ${remixPrereleaseTag})`)
-    console.log(
-      'Publishing in two phases: other packages as "latest", then remix as',
-      `"${remixPrereleaseTag}"\n`,
-    )
+    remixPrereleaseChannel = remixPrereleaseConfig.config.channel
+    console.log(`Remix is in prerelease mode (channel: ${remixPrereleaseChannel})`)
+    console.log('Publishing in two phases: other packages as "latest", then remix as "next"\n')
   }

   // Publish packages to npm
@@ -216,12 +213,12 @@ async function main() {

   let published: PublishedPackage[] = []

-  if (remixPrereleaseTag) {
+  if (remixPrereleaseChannel) {
     let publishCommands = [
       // Phase 1: Publish everything in `packages` except remix (with --report-summary so we know what was published)
       'pnpm publish --recursive --filter "./packages/*" --filter "!remix" --access public --no-git-checks --report-summary',
-      // Phase 2: Publish remix with prerelease tag (with --report-summary so we know if remix was published)
-      `pnpm publish --filter remix --tag ${remixPrereleaseTag} --access public --no-git-checks --report-summary`,
+      // Phase 2: Publish remix with "next" tag (with --report-summary so we know if remix was published)
+      'pnpm publish --filter remix --tag next --access public --no-git-checks --report-summary',
     ]

     if (dryRun) {
diff --git a/scripts/utils/changes.ts b/scripts/utils/changes.ts
index 447cc436d80..3e72ed2f7b3 100644
--- a/scripts/utils/changes.ts
+++ b/scripts/utils/changes.ts
@@ -15,7 +15,7 @@ type BumpType = (typeof bumpTypes)[number]
 // Prerelease configuration (from packages/remix/.changes/prerelease.json)
 // Only the remix package supports prerelease mode.
 export interface RemixPrereleaseConfig {
-  tag: string
+  channel: string
 }

 export type ParsedRemixPrereleaseConfig =
@@ -46,25 +46,25 @@ export function readRemixPrereleaseConfig(): ParsedRemixPrereleaseConfig {
     return {
       exists: true,
       valid: false,
-      error: 'prerelease.json must be an object with a "tag" field',
+      error: 'prerelease.json must be an object with a "channel" field',
     }
   }

   let obj = content as Record<string, unknown>

-  if (!('tag' in obj)) {
-    return { exists: true, valid: false, error: 'prerelease.json must have a "tag" field' }
+  if (!('channel' in obj)) {
+    return { exists: true, valid: false, error: 'prerelease.json must have a "channel" field' }
   }

-  if (typeof obj.tag !== 'string' || obj.tag.trim().length === 0) {
+  if (typeof obj.channel !== 'string' || obj.channel.trim().length === 0) {
     return {
       exists: true,
       valid: false,
-      error: 'prerelease.json "tag" must be a non-empty string',
+      error: 'prerelease.json "channel" must be a non-empty string',
     }
   }

-  return { exists: true, valid: true, config: { tag: obj.tag.trim() } }
+  return { exists: true, valid: true, config: { channel: obj.channel.trim() } }
 }

 /**
@@ -91,17 +91,17 @@ function getNextVersion(

   if (prereleaseConfig !== null) {
     // In prerelease mode
-    let targetTag = prereleaseConfig.tag
+    let targetChannel = prereleaseConfig.channel

-    if (currentPrereleaseId === targetTag) {
-      // Same tag - just bump the counter
-      let nextVersion = semver.inc(currentVersion, 'prerelease', targetTag)
+    if (currentPrereleaseId === targetChannel) {
+      // Same channel - just bump the counter
+      let nextVersion = semver.inc(currentVersion, 'prerelease', targetChannel)
       if (nextVersion == null) {
         throw new Error(`Invalid prerelease increment: ${currentVersion}`)
       }
       return nextVersion
     } else {
-      // Entering prerelease or transitioning to a new tag (e.g., stable → alpha, or alpha → beta)
+      // Entering prerelease or transitioning to a new channel (e.g., stable → alpha, or alpha → beta)
       // Apply the bump type to get the base version, then add prerelease suffix
       let baseVersion = isCurrentPrerelease
         ? currentVersion.replace(/-.*$/, '') // Strip existing prerelease suffix
@@ -111,7 +111,7 @@ function getNextVersion(
         throw new Error(`Invalid version increment: ${currentVersion} + ${bumpType}`)
       }

-      return `${baseVersion}-${targetTag}.0`
+      return `${baseVersion}-${targetChannel}.0`
     }
   } else {
     // Not in prerelease mode
@@ -229,14 +229,14 @@ function parsePackageChanges(packageDirName: string): ParsedPackageChanges {
     // Config exists
     if (
       currentVersionPrereleaseId !== null &&
-      currentVersionPrereleaseId !== prereleaseConfig.tag
+      currentVersionPrereleaseId !== prereleaseConfig.channel
     ) {
-      // Tag mismatch (e.g., version is alpha but config says beta) - need change files to transition
+      // Channel mismatch (e.g., version is alpha but config says beta) - need change files to transition
       if (!hasChangeFiles) {
         errors.push({
           packageDirName,
           file: '.changes/prerelease.json',
-          error: `prerelease.json tag '${prereleaseConfig.tag}' doesn't match version's prerelease identifier '${currentVersionPrereleaseId}'. Add a change file to transition to ${prereleaseConfig.tag}.`,
+          error: `prerelease.json channel '${prereleaseConfig.channel}' doesn't match version's prerelease identifier '${currentVersionPrereleaseId}'. Add a change file to transition to ${prereleaseConfig.channel}.`,
         })
       }
     } else if (!isCurrentVersionPrerelease && !hasChangeFiles) {
@@ -253,7 +253,7 @@ function parsePackageChanges(packageDirName: string): ParsedPackageChanges {
       errors.push({
         packageDirName,
         file: '.changes/',
-        error: `Version ${currentVersion} is a prerelease but no prerelease.json exists. Either add prerelease.json with { "tag": "${currentVersionPrereleaseId}" }, or add a change file to graduate to stable.`,
+        error: `Version ${currentVersion} is a prerelease but no prerelease.json exists. Either add prerelease.json with { "channel": "${currentVersionPrereleaseId}" }, or add a change file to graduate to stable.`,
       })
     }
   }

PATCH

echo "Patch applied successfully."
