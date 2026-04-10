#!/usr/bin/env bash
set -euo pipefail

cd /workspace/remix

# Idempotent: skip if already applied
if [ -f scripts/release-pr.ts ] && grep -q "prTitle = 'Release'" scripts/release-pr.ts 2>/dev/null; then
    echo "Patch already applied."
    exit 0
fi

git apply --whitespace=fix - <<'PATCH'
diff --git a/.github/workflows/changes-version-pr.yaml b/.github/workflows/release-pr.yaml
similarity index 89%
rename from .github/workflows/changes-version-pr.yaml
rename to .github/workflows/release-pr.yaml
index 222f48a6cf5..017a16b0258 100644
--- a/.github/workflows/changes-version-pr.yaml
+++ b/.github/workflows/release-pr.yaml
@@ -1,4 +1,4 @@
-name: Update "Version Packages" PR
+name: Update "Release" PR

 on:
   push:
@@ -34,6 +34,6 @@ jobs:
         run: pnpm install --frozen-lockfile

       - name: Update PR
-        run: node scripts/changes-version-pr.ts
+        run: node scripts/release-pr.ts
         env:
           GITHUB_TOKEN: ${{ secrets.GH_REMIX_PAT }}
diff --git a/AGENTS.md b/AGENTS.md
index f3c1acd66dc..9a6a467c1fe 100644
--- a/AGENTS.md
+++ b/AGENTS.md
@@ -55,7 +55,7 @@
     - **Graduating from prerelease to latest stable version**: Delete `prerelease.json` and add a change file. The prerelease suffix will be stripped (e.g. `3.0.0-rc.7` → `3.0.0`). The bump type is for changelog categorization only—by convention, use `major` for a major release announcement.
 - **Validating changes**: `pnpm changes:validate` checks that all change files follow the correct naming convention and format.
 - **Previewing releases**: `pnpm changes:preview` shows which packages will be released, what the CHANGELOG will look like, and the commit message.
-- **Automated releases**: When changes are pushed to `main`, the [changes-version-pr workflow](/.github/workflows/changes-version-pr.yaml) automatically opens/updates a "Version Packages" PR. The [publish workflow](/.github/workflows/publish.yaml) runs on every push to `main` and publishes when no change files are present (i.e., after merging the Version Packages PR).
+- **Automated releases**: When changes are pushed to `main`, the [release-pr workflow](/.github/workflows/release-pr.yaml) automatically opens/updates a "Release" PR. The [publish workflow](/.github/workflows/publish.yaml) runs on every push to `main` and publishes when no change files are present (i.e., after merging the Release PR).
 - **Manual releases**: `pnpm changes:version` updates package.json, CHANGELOG.md, and creates a git commit. Push to `main` and the publish workflow will handle the rest (including tags and GitHub releases).
 - **How publishing works**: The publish workflow checks for change files. If none exist, it runs `pnpm publish --recursive --report-summary`, reads the summary JSON to see what was published, then creates git tags and GitHub releases for each published package.
-- **Test change/release code with preview scripts**: When modifying any change/release code, run `pnpm changes:preview` to test locally. For the version PR script, run `node ./scripts/changes-version-pr.ts --preview`. For the publish script, run `node ./scripts/publish.ts --dry-run` to see what commands would be executed without actually publishing.
+- **Test change/release code with preview scripts**: When modifying any change/release code, run `pnpm changes:preview` to test locally. For the release PR script, run `node ./scripts/release-pr.ts --preview`. For the publish script, run `node ./scripts/publish.ts --dry-run` to see what commands would be executed without actually publishing.
diff --git a/CONTRIBUTING.md b/CONTRIBUTING.md
index 709044cd25a..251459aedfc 100644
--- a/CONTRIBUTING.md
+++ b/CONTRIBUTING.md
@@ -94,11 +94,11 @@ pnpm changes:validate

 ## Releases

-Releases are automated via the [changes-version-pr workflow](/.github/workflows/changes-version-pr.yaml) and [publish workflow](/.github/workflows/publish.yaml).
+Releases are automated via the [release-pr workflow](/.github/workflows/release-pr.yaml) and [publish workflow](/.github/workflows/publish.yaml).

 1. **You push changes to `main`** with change files in `packages/*/.changes/`

-2. **A "Version Packages" PR is automatically opened** (or updated if one exists)
+2. **A "Release" PR is automatically opened** (or updated if one exists)

    The PR contains:

@@ -112,7 +112,7 @@ Releases are automated via the [changes-version-pr workflow](/.github/workflows/

 ### Manual Versioning

-The "Version Packages" PR simply automates the `pnpm changes:version` command. If needed, you can run this command manually. This will update the `package.json` versions, `CHANGELOG.md` files, and delete the change files. It will then commit the result.
+The "Release" PR simply automates the `pnpm changes:version` command. If needed, you can run this command manually. This will update the `package.json` versions, `CHANGELOG.md` files, and delete the change files. It will then commit the result.

 ```sh
 pnpm changes:version
diff --git a/scripts/publish.ts b/scripts/publish.ts
index 500200c495d..992fe2b09e7 100644
--- a/scripts/publish.ts
+++ b/scripts/publish.ts
@@ -250,7 +250,7 @@ async function main() {

   // In dry run mode, query npm to determine what would be published
   // and preview the GitHub releases. This is designed to be run against
-  // the contents of the "Version Packages" PR / `pnpm changes:version` output.
+  // the contents of the "Release" PR / `pnpm changes:version` output.
   if (dryRun) {
     console.log('Checking npm for unpublished versions...\n')

diff --git a/scripts/changes-version-pr.ts b/scripts/release-pr.ts
similarity index 94%
rename from scripts/changes-version-pr.ts
rename to scripts/release-pr.ts
index 1490f73b185..81a66178d33 100644
--- a/scripts/changes-version-pr.ts
+++ b/scripts/release-pr.ts
@@ -1,14 +1,14 @@
 /**
- * Opens or updates the version PR.
+ * Opens or updates the release PR.
  *
  * Usage:
- *   node scripts/changes-version-pr.ts [--preview]
+ *   node scripts/release-pr.ts [--preview]
  *
  * Environment:
  *   GITHUB_TOKEN - Required (unless --preview)
  */
 import { parseAllChangeFiles, generateCommitMessage } from './utils/changes.ts'
-import { generatePrBody } from './utils/version-pr.ts'
+import { generatePrBody } from './utils/release-pr.ts'
 import { logAndExec } from './utils/process.ts'
 import { findOpenPr, createPr, updatePr, setPrPkgLabels, closePr } from './utils/github.ts'

@@ -16,8 +16,8 @@ let args = process.argv.slice(2)
 let preview = args.includes('--preview')

 let baseBranch = 'main'
-let prBranch = 'changes-version-pr/main'
-let prTitle = 'Version Packages'
+let prBranch = 'release-pr/main'
+let prTitle = 'Release'

 async function main() {
   console.log(preview ? '🔍 PREVIEW MODE\n' : '')
diff --git a/scripts/utils/changes.ts b/scripts/utils/changes.ts
index 3e72ed2f7b3..b0cf1e66af7 100644
--- a/scripts/utils/changes.ts
+++ b/scripts/utils/changes.ts
@@ -6,6 +6,9 @@ import {
   getPackageFile,
   getPackagePath,
   packageNameToDirectoryName,
+  getTransitiveDependents,
+  getGitHubReleaseUrl,
+  getPackageDependencies,
 } from './packages.ts'
 import { fileExists, readFile, readJson } from './fs.ts'

@@ -373,6 +376,15 @@ function parsePackageChanges(packageDirName: string): ParsedPackageChanges {
   return { valid: true, changes, prereleaseConfig }
 }

+/**
+ * Represents a dependency that was bumped, triggering this release.
+ */
+export interface DependencyBump {
+  packageName: string
+  version: string
+  releaseUrl: string
+}
+
 export interface PackageRelease {
   packageDirName: string
   packageName: string
@@ -380,6 +392,8 @@ export interface PackageRelease {
   nextVersion: string
   bump: BumpType
   changes: ChangeFile[]
+  /** Dependencies that were bumped, triggering this release (if any) */
+  dependencyBumps: DependencyBump[]
 }

 type ParsedChanges =
@@ -388,13 +402,34 @@ type ParsedChanges =

 /**
  * Parses and validates all change files across all packages.
+ * Also includes packages that need to be released due to dependency changes.
  * Returns releases if valid, or errors if invalid.
  */
 export function parseAllChangeFiles(): ParsedChanges {
   let packageDirNames = getAllPackageDirNames()
-  let releases: PackageRelease[] = []
   let errors: ValidationError[] = []

+  // Build maps for lookup
+  let dirNameToPackageName = new Map<string, string>()
+  let packageNameToDirName = new Map<string, string>()
+
+  // First pass: collect package info and validate change files
+  interface ParsedPackageInfo {
+    packageDirName: string
+    packageName: string
+    currentVersion: string
+    changes: ChangeFile[]
+    prereleaseConfig: RemixPrereleaseConfig | null
+  }
+  let parsedPackages: ParsedPackageInfo[] = []
+
+  // Read the remix prerelease config once (only remix supports prerelease mode)
+  let remixPrereleaseConfig = readRemixPrereleaseConfig()
+  let validRemixPrereleaseConfig: RemixPrereleaseConfig | null = null
+  if (remixPrereleaseConfig.exists && remixPrereleaseConfig.valid) {
+    validRemixPrereleaseConfig = remixPrereleaseConfig.config
+  }
+
   for (let packageDirName of packageDirNames) {
     let parsed = parsePackageChanges(packageDirName)

@@ -403,33 +438,127 @@ export function parseAllChangeFiles(): ParsedChanges {
       continue
     }

-    // Only create a release if there are changes
-    if (parsed.changes.length > 0) {
-      let packageJsonPath = getPackageFile(packageDirName, 'package.json')
-      let packageJson = readJson(packageJsonPath)
-      let packageName = packageJson.name as string
-      let currentVersion = packageJson.version as string
-
-      let bump = getHighestBump(parsed.changes.map((c) => c.bump))
-      if (bump == null) continue
+    let packageJsonPath = getPackageFile(packageDirName, 'package.json')
+    let packageJson = readJson(packageJsonPath)
+    let packageName = packageJson.name as string
+    let currentVersion = packageJson.version as string

-      let nextVersion = getNextVersion(currentVersion, bump, parsed.prereleaseConfig)
+    dirNameToPackageName.set(packageDirName, packageName)
+    packageNameToDirName.set(packageName, packageDirName)

-      releases.push({
-        packageDirName,
-        packageName,
-        currentVersion,
-        nextVersion,
-        bump,
-        changes: parsed.changes,
-      })
+    // For remix package, use the prerelease config even if there are no change files
+    // (to correctly bump prerelease counter for dependency-triggered releases)
+    let prereleaseConfig = parsed.prereleaseConfig
+    if (packageDirName === 'remix' && prereleaseConfig === null && validRemixPrereleaseConfig) {
+      prereleaseConfig = validRemixPrereleaseConfig
     }
+
+    parsedPackages.push({
+      packageDirName,
+      packageName,
+      currentVersion,
+      changes: parsed.changes,
+      prereleaseConfig,
+    })
   }

   if (errors.length > 0) {
     return { valid: false, errors }
   }

+  // Find packages with direct changes
+  let directlyChangedPackages = new Set<string>()
+  for (let pkg of parsedPackages) {
+    if (pkg.changes.length > 0) {
+      directlyChangedPackages.add(pkg.packageName)
+    }
+  }
+
+  // Find all packages that transitively depend on changed packages
+  let transitiveDependents = getTransitiveDependents(directlyChangedPackages)
+
+  // Determine all packages that will be released
+  let allReleasingPackages = new Set<string>([
+    ...directlyChangedPackages,
+    ...transitiveDependents.keys(),
+  ])
+
+  // Compute next versions for all releasing packages
+  // We need to do this in dependency order to correctly compute dependency bumps
+  let packageVersions = new Map<string, string>() // packageName -> nextVersion
+
+  // First, compute versions for directly changed packages
+  for (let pkg of parsedPackages) {
+    if (pkg.changes.length > 0) {
+      let bump = getHighestBump(pkg.changes.map((c) => c.bump))
+      if (bump == null) continue
+      let nextVersion = getNextVersion(pkg.currentVersion, bump, pkg.prereleaseConfig)
+      packageVersions.set(pkg.packageName, nextVersion)
+    }
+  }
+
+  // Then, compute versions for dependency-triggered releases
+  // We need to do this iteratively because a package's version depends on knowing
+  // which of its dependencies are being released
+  for (let pkg of parsedPackages) {
+    if (!directlyChangedPackages.has(pkg.packageName) && allReleasingPackages.has(pkg.packageName)) {
+      // This package is being released due to dependency changes
+      // Use the package's prerelease config if it has one (e.g., remix in prerelease mode)
+      let nextVersion = getNextVersion(pkg.currentVersion, 'patch', pkg.prereleaseConfig)
+      packageVersions.set(pkg.packageName, nextVersion)
+    }
+  }
+
+  // Now build the final releases with dependency bumps
+  let releases: PackageRelease[] = []
+
+  for (let pkg of parsedPackages) {
+    if (!allReleasingPackages.has(pkg.packageName)) {
+      continue
+    }
+
+    let nextVersion = packageVersions.get(pkg.packageName)
+    if (nextVersion == null) continue
+
+    // Compute dependency bumps: which of this package's direct dependencies are being released?
+    let dependencyBumps: DependencyBump[] = []
+    let deps = getPackageDependencies(pkg.packageName)
+
+    for (let depName of deps) {
+      if (allReleasingPackages.has(depName)) {
+        let depVersion = packageVersions.get(depName)
+        if (depVersion) {
+          dependencyBumps.push({
+            packageName: depName,
+            version: depVersion,
+            releaseUrl: getGitHubReleaseUrl(depName, depVersion),
+          })
+        }
+      }
+    }
+
+    // Sort dependency bumps alphabetically by package name
+    dependencyBumps.sort((a, b) => a.packageName.localeCompare(b.packageName))
+
+    let bump: BumpType = 'patch'
+    if (pkg.changes.length > 0) {
+      bump = getHighestBump(pkg.changes.map((c) => c.bump)) ?? 'patch'
+    }
+
+    releases.push({
+      packageDirName: pkg.packageDirName,
+      packageName: pkg.packageName,
+      currentVersion: pkg.currentVersion,
+      nextVersion,
+      bump,
+      changes: pkg.changes,
+      dependencyBumps,
+    })
+  }
+
+  // Sort by package name for consistency
+  releases.sort((a, b) => a.packageName.localeCompare(b.packageName))
+
   return { valid: true, releases }
 }

@@ -549,6 +678,33 @@ function generateBumpTypeSection(
   return lines.join('\n')
 }

+/**
+ * Generates the dependency bumps section for a changelog entry
+ */
+function generateDependencyBumpsSection(
+  dependencyBumps: DependencyBump[],
+  subheadingLevel: number,
+): string | null {
+  if (dependencyBumps.length === 0) {
+    return null
+  }
+
+  let lines: string[] = []
+  let subheadingPrefix = '#'.repeat(subheadingLevel)
+
+  lines.push(`${subheadingPrefix} Patch Changes`)
+  lines.push('')
+  lines.push('- Bumped `@remix-run/*` dependencies:')
+
+  for (let dep of dependencyBumps) {
+    lines.push(`  - [\`${dep.packageName}@${dep.version}\`](${dep.releaseUrl})`)
+  }
+
+  lines.push('')
+
+  return lines.join('\n')
+}
+
 /**
  * Generates changelog content for a package release
  */
@@ -579,6 +735,26 @@ export function generateChangelogContent(
     }
   }

+  // Add dependency bumps section if there are any
+  // Only add if there are no other patch changes (to avoid duplicate "Patch Changes" heading)
+  if (release.dependencyBumps.length > 0) {
+    let hasPatchChanges = release.changes.some((c) => c.bump === 'patch')
+    if (hasPatchChanges) {
+      // Append to existing patch section (without heading)
+      lines.push('- Bumped `@remix-run/*` dependencies:')
+      for (let dep of release.dependencyBumps) {
+        lines.push(`  - [\`${dep.packageName}@${dep.version}\`](${dep.releaseUrl})`)
+      }
+      lines.push('')
+    } else {
+      // Create new patch section with heading
+      let section = generateDependencyBumpsSection(release.dependencyBumps, subheadingLevel)
+      if (section) {
+        lines.push(section)
+      }
+    }
+  }
+
   return lines.join('\n')
 }

@@ -586,7 +762,7 @@ export function generateChangelogContent(
  * Generates the commit message for all releases
  */
 export function generateCommitMessage(releases: PackageRelease[]): string {
-  let subject = 'Version Packages'
+  let subject = 'Release'
   let body = releases
     .map((r) => `- ${r.packageName}: ${r.currentVersion} -> ${r.nextVersion}`)
     .join('\n')
diff --git a/scripts/utils/packages.ts b/scripts/utils/packages.ts
index 632acd30513..af69b745317 100644
--- a/scripts/utils/packages.ts
+++ b/scripts/utils/packages.ts
@@ -9,6 +9,8 @@ export const packagesDir = path.relative(
   path.resolve(__dirname, '..', '..', 'packages'),
 )

+export const GITHUB_REPO_URL = 'https://github.com/remix-run/remix'
+
 export function getAllPackageDirNames(): string[] {
   return fs.readdirSync(packagesDir).filter((name) => {
     let packagePath = getPackagePath(name)
@@ -68,3 +70,162 @@ let getNpmPackageNameToDirectoryMap = (() => {
 export function packageNameToDirectoryName(packageName: string): string | null {
   return getNpmPackageNameToDirectoryMap().get(packageName) ?? null
 }
+
+/**
+ * Returns the short name used in git tags for a package.
+ * For @remix-run/* packages, strips the scope. For "remix", returns "remix".
+ *
+ * Examples:
+ *   "@remix-run/headers" -> "headers"
+ *   "remix" -> "remix"
+ */
+export function getPackageShortName(packageName: string): string {
+  if (packageName.startsWith('@remix-run/')) {
+    return packageName.slice('@remix-run/'.length)
+  }
+  return packageName
+}
+
+/**
+ * Generates the git tag for a package release.
+ *
+ * Examples:
+ *   ("@remix-run/headers", "0.11.0") -> "headers@0.11.0"
+ *   ("remix", "3.0.0") -> "remix@3.0.0"
+ */
+export function getGitTag(packageName: string, version: string): string {
+  return `${getPackageShortName(packageName)}@${version}`
+}
+
+/**
+ * Generates the GitHub release URL for a package release.
+ */
+export function getGitHubReleaseUrl(packageName: string, version: string): string {
+  let tag = getGitTag(packageName, version)
+  return `${GITHUB_REPO_URL}/releases/tag/${tag}`
+}
+
+interface PackageInfo {
+  name: string
+  version: string
+  dirName: string
+  dependencies: string[] // Only @remix-run/* dependencies
+}
+
+/**
+ * Gets information about all packages in the monorepo, including their
+ * @remix-run/* dependencies.
+ */
+let getPackageInfoMap = (() => {
+  let map: Map<string, PackageInfo> | null = null
+
+  return function getPackageInfoMap(): Map<string, PackageInfo> {
+    if (map !== null) {
+      return map
+    }
+
+    map = new Map()
+    let dirNames = getAllPackageDirNames()
+
+    for (let dirName of dirNames) {
+      let packageJsonPath = getPackageFile(dirName, 'package.json')
+      if (fs.existsSync(packageJsonPath)) {
+        try {
+          let packageJson = JSON.parse(fs.readFileSync(packageJsonPath, 'utf-8'))
+          let name = packageJson.name as string
+          let version = packageJson.version as string
+
+          // Collect @remix-run/* dependencies from the dependencies field
+          let dependencies: string[] = []
+          let deps = packageJson.dependencies as Record<string, string> | undefined
+          if (deps) {
+            for (let depName of Object.keys(deps)) {
+              if (depName.startsWith('@remix-run/') || depName === 'remix') {
+                dependencies.push(depName)
+              }
+            }
+          }
+
+          map.set(name, { name, version, dirName, dependencies })
+        } catch {
+          // Skip invalid package.json files
+        }
+      }
+    }
+
+    return map
+  }
+})()
+
+/**
+ * Gets the @remix-run/* dependencies for a package.
+ */
+export function getPackageDependencies(packageName: string): string[] {
+  let info = getPackageInfoMap().get(packageName)
+  return info?.dependencies ?? []
+}
+
+/**
+ * Builds a reverse dependency graph: maps each package to the set of packages
+ * that depend on it.
+ */
+export function buildReverseDependencyGraph(): Map<string, Set<string>> {
+  let graph = new Map<string, Set<string>>()
+  let packageInfoMap = getPackageInfoMap()
+
+  // Initialize empty sets for all packages
+  for (let packageName of packageInfoMap.keys()) {
+    graph.set(packageName, new Set())
+  }
+
+  // Build reverse edges
+  for (let [packageName, info] of packageInfoMap) {
+    for (let dep of info.dependencies) {
+      let dependents = graph.get(dep)
+      if (dependents) {
+        dependents.add(packageName)
+      }
+    }
+  }
+
+  return graph
+}
+
+/**
+ * Gets all packages that transitively depend on any of the given packages.
+ * Returns a map from dependent package name to the set of changed packages it depends on.
+ */
+export function getTransitiveDependents(
+  changedPackages: Set<string>,
+): Map<string, Set<string>> {
+  let reverseGraph = buildReverseDependencyGraph()
+  let result = new Map<string, Set<string>>()
+
+  // For each changed package, find all its transitive dependents
+  function addDependents(changedPackage: string, originalChangedPackage: string) {
+    let directDependents = reverseGraph.get(changedPackage)
+    if (!directDependents) return
+
+    for (let dependent of directDependents) {
+      // Skip if this is one of the originally changed packages
+      if (changedPackages.has(dependent)) continue
+
+      // Track which changed packages this dependent needs
+      let changedDeps = result.get(dependent)
+      if (!changedDeps) {
+        changedDeps = new Set()
+        result.set(dependent, changedDeps)
+      }
+      changedDeps.add(originalChangedPackage)
+
+      // Recursively process dependents
+      addDependents(dependent, originalChangedPackage)
+    }
+  }
+
+  for (let changedPackage of changedPackages) {
+    addDependents(changedPackage, changedPackage)
+  }
+
+  return result
+}
diff --git a/scripts/utils/version-pr.ts b/scripts/utils/release-pr.ts
similarity index 93%
rename from scripts/utils/version-pr.ts
rename to scripts/utils/release-pr.ts
index f40a9c5f28a..b6be114f72c 100644
--- a/scripts/utils/version-pr.ts
+++ b/scripts/utils/release-pr.ts
@@ -5,7 +5,7 @@ import { generateChangelogContent } from './changes.ts'
 let maxBodyLength = 60_000

 /**
- * Generates the PR body for a version PR
+ * Generates the PR body for a release PR
  */
 export function generatePrBody(releases: PackageRelease[]): string {
   let header = generateHeader()
@@ -29,7 +29,7 @@ export function generatePrBody(releases: PackageRelease[]): string {

 function generateHeader(): string {
   return [
-    'This PR is managed by the [`changes-version-pr`](https://github.com/remix-run/remix/blob/main/.github/workflows/changes-version-pr.yaml) workflow. ' +
+    'This PR is managed by the [`release-pr`](https://github.com/remix-run/remix/blob/main/.github/workflows/release-pr.yaml) workflow. ' +
       'Do not edit it manually. ' +
       'See [CONTRIBUTING.md](https://github.com/remix-run/remix/blob/main/CONTRIBUTING.md#releases) for more.',
   ].join('\n')

PATCH

echo "Patch applied successfully."
