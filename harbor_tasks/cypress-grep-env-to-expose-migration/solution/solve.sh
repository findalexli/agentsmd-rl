#!/usr/bin/env bash
set -euo pipefail

cd /workspace/cypress

# Idempotent: skip if already applied
if grep -q 'expose?' npm/grep/src/plugin.ts 2>/dev/null; then
    echo "Patch already applied."
    exit 0
fi

git apply --whitespace=fix - <<'PATCH'
diff --git a/npm/grep/README.md b/npm/grep/README.md
index f58ac5bfe41..090eb21fed8 100644
--- a/npm/grep/README.md
+++ b/npm/grep/README.md
@@ -91,19 +91,19 @@ export default defineConfig({
 Run tests with "login" in the title:

 ```shell
-npx cypress run --env grep="login"
+npx cypress run --expose grep="login"
 ```

 Run tests with "user authentication" in the title:

 ```shell
-npx cypress run --env grep="user authentication"
+npx cypress run --expose grep="user authentication"
 ```

 Multiple title patterns (OR logic):

 ```shell
-npx cypress run --env grep="login; logout; signup"
+npx cypress run --expose grep="login; logout; signup"
 ```

 ### Filter by Tags
@@ -134,25 +134,25 @@ Then run by tags:
 Run tests with @smoke tag:

 ```shell
-npx cypress run --env grepTags="@smoke"
+npx cypress run --expose grepTags="@smoke"
 ```

 Run tests with @smoke OR @critical tags:

 ```shell
-npx cypress run --env grepTags="@smoke @critical"
+npx cypress run --expose grepTags="@smoke @critical"
 ```

 Run tests with BOTH @smoke AND @critical tags:

 ```shell
-npx cypress run --env grepTags="@smoke+@critical"
+npx cypress run --expose grepTags="@smoke+@critical"
 ```

 Run tests with @smoke tag but NOT @slow tag:

 ```shell
-npx cypress run --env grepTags="@smoke+-@slow"
+npx cypress run --expose grepTags="@smoke+-@slow"
 ```

 ### Combine Title and Tag Filters
@@ -160,13 +160,13 @@ npx cypress run --env grepTags="@smoke+-@slow"
 Run tests with "login" in title AND tagged @smoke:

 ```shell
-npx cypress run --env grep="login",grepTags="@smoke"
+npx cypress run --expose grep="login",grepTags="@smoke"
 ```

 Run tests with "user" in title AND tagged @critical OR @smoke:

 ```shell
-npx cypress run --env grep="user",grepTags="@critical @smoke"
+npx cypress run --expose grep="user",grepTags="@critical @smoke"
 ```

 ## Advanced Features
@@ -178,13 +178,13 @@ Skip loading specs that don't contain matching tests (requires plugin setup):
 Only run specs containing tests with "login" in title:

 ```shell
-npx cypress run --env grep="login",grepFilterSpecs=true
+npx cypress run --expose grep="login",grepFilterSpecs=true
 ```

 Only run specs containing tests tagged @smoke:

 ```shell
-npx cypress run --env grepTags="@smoke",grepFilterSpecs=true
+npx cypress run --expose grepTags="@smoke",grepFilterSpecs=true
 ```

 ### Omit Filtered Tests
@@ -192,7 +192,7 @@ npx cypress run --env grepTags="@smoke",grepFilterSpecs=true
 By default, filtered tests are marked as pending. To completely omit them:

 ```shell
-npx cypress run --env grep="login",grepOmitFiltered=true
+npx cypress run --expose grep="login",grepOmitFiltered=true
 ```

 ### Test Burning (Repeat Tests)
@@ -202,13 +202,13 @@ Run filtered tests multiple times to catch flaky behavior:
 Run matching tests 5 times:

 ```shell
-npx cypress run --env grep="login",burn=5
+npx cypress run --expose grep="login",burn=5
 ```

 Run all tests 10 times:

 ```shell
-npx cypress run --env burn=10
+npx cypress run --expose burn=10
 ```

 ### Inverted Filters
@@ -216,19 +216,19 @@ npx cypress run --env burn=10
 Run tests WITHOUT "slow" in the title:

 ```shell
-npx cypress run --env grep="-slow"
+npx cypress run --expose grep="-slow"
 ```

 Run tests WITHOUT @slow tag:

 ```shell
-npx cypress run --env grepTags="-@slow"
+npx cypress run --expose grepTags="-@slow"
 ```

 Complex combinations:

 ```shell
-npx cypress run --env grep="login; -slow",grepTags="@smoke+-@regression"
+npx cypress run --expose grep="login; -slow",grepTags="@smoke+-@regression"
 ```

 ### Run Untagged Tests
@@ -236,7 +236,7 @@ npx cypress run --env grep="login; -slow",grepTags="@smoke+-@regression"
 Run only tests without any tags:

 ```shell
-npx cypress run --env grepUntagged=true
+npx cypress run --expose grepUntagged=true
 ```

 ## Configuration Examples
@@ -248,7 +248,7 @@ import { defineConfig } from 'cypress'
 import { plugin as cypressGrepPlugin } from '@cypress/grep/plugin'

 export default defineConfig({
-  env: {
+  expose: {
     // Always filter by viewport tests
     grep: "viewport",
     // Always enable spec filtering
@@ -270,10 +270,10 @@ export default defineConfig({
 ```json
 {
   "scripts": {
-    "cy:smoke": "cypress run --env grepTags=@smoke",
-    "cy:critical": "cypress run --env grepTags=@critical",
-    "cy:fast": "cypress run --env grepTags=@fast",
-    "cy:burn": "cypress run --env grepTags=@smoke,burn=5"
+    "cy:smoke": "cypress run --expose grepTags=@smoke",
+    "cy:critical": "cypress run --expose grepTags=@critical",
+    "cy:fast": "cypress run --expose grepTags=@fast",
+    "cy:burn": "cypress run --expose grepTags=@smoke,burn=5"
   }
 }
 ```
@@ -338,7 +338,7 @@ Cypress.grep()

 1. **Spec Loading**: When not using `grepFilterSpecs`, all spec files are loaded before filtering occurs
 2. **Inverted Filters**: Negative filters (`-tag`, `-title`) are not compatible with `grepFilterSpecs`
-3. **Runtime Changes**: Cannot change grep filters at runtime using `Cypress.env()`
+3. **Runtime Changes**: Cannot change grep filters at runtime using `Cypress.expose()`
 4. **Cloud Recordings**: Filtered tests may still appear in Cypress Cloud recordings as pending tests

 ## Best Practices
@@ -369,7 +369,7 @@ it('should work', { tags: ['@smoke', '@fast'] }, () => {
 1. Run smoke tests first:

 ```shell
-npx cypress run --env grepTags="@smoke"
+npx cypress run --expose grepTags="@smoke"
 ```

 2. If smoke tests pass, run all tests:
@@ -381,11 +381,11 @@ npx cypress run
 3. For debugging, run specific test groups:

 ```shell
-npx cypress run --env grep="user management"
+npx cypress run --expose grep="user management"
 ```

 ```shell
-npx cypress run --env grepTags="@critical"
+npx cypress run --expose grepTags="@critical"
 ```

 ### Performance Tips
@@ -403,7 +403,7 @@ Enable debug logging to see what's happening:
 Terminal debug (for plugin):

 ```shell
-DEBUG=@cypress/grep npx cypress run --env grep="login"
+DEBUG=@cypress/grep npx cypress run --expose grep="login"
 ```

 Browser debug (for support file):
@@ -422,6 +422,21 @@ Then refresh and run tests.

 ## Migration

+### From v5 to v6
+
+`Cypress.env()` is deprecated in Cypress 15.10.0. For public configuration, the API has been replaced with `Cypress.expose()`
+
+To migrate, change your `--env`/`-e` CLI arguments from
+```sh
+npx cypress run --env grepTags="tag1 tag2"
+```
+
+to the following to use `--expose`/`-x`
+```sh
+npx cypress run --expose grepTags="tag1 tag2"
+```
+
+
 ### From v4 to v5

 The support file registration and plugin have changed their export signature, meaning:
diff --git a/npm/grep/cypress.config.ts b/npm/grep/cypress.config.ts
index 73a08d47fad..12866d7e091 100644
--- a/npm/grep/cypress.config.ts
+++ b/npm/grep/cypress.config.ts
@@ -8,7 +8,7 @@ import debug from 'debug'
 const debugInstance = debug('cypress:grep:compare-results')

 export default defineConfig({
-  allowCypressEnv: true,
+  allowCypressEnv: false,
   e2e: {
     defaultCommandTimeout: 1000,
     setupNodeEvents (on, config) {
diff --git a/npm/grep/cypress/e2e/grep-task.cy.ts b/npm/grep/cypress/e2e/grep-task.cy.ts
index e97f95d95ad..a4a42f3bd80 100644
--- a/npm/grep/cypress/e2e/grep-task.cy.ts
+++ b/npm/grep/cypress/e2e/grep-task.cy.ts
@@ -4,7 +4,7 @@ describe('plugin', () => {
       cy.task('grep', {
         excludeSpecPattern: ['**/test2.cy.ts', '**/test3.cy.ts'],
         specPattern: '**/*.cy.ts',
-        env: {
+        expose: {
           grepTags: 'smoke',
           grepFilterSpecs: true,
         },
@@ -18,7 +18,7 @@ describe('plugin', () => {
       cy.task('grep', {
         excludeSpecPattern: '**/test2.cy.ts',
         specPattern: '**/*.cy.ts',
-        env: {
+        expose: {
           grepTags: 'smoke',
           grepFilterSpecs: true,
         },
diff --git a/npm/grep/package.json b/npm/grep/package.json
index a968db23c92..6ee560a6ad0 100644
--- a/npm/grep/package.json
+++ b/npm/grep/package.json
@@ -7,32 +7,32 @@
     "cypress:open": "node ../../scripts/cypress.js open",
     "test": "vitest",
     "test-debug": "vitest --inspect-brk --no-file-parallelism --test-timeout=0",
-    "and": "PROJECT_NAME=and node ../../scripts/cypress.js run --env grep='Test 2',grepTags='smoke+high' --config specPattern='**/tags/*.cy.ts'",
-    "and:not": "PROJECT_NAME=and-not node ../../scripts/cypress.js run --env grep='Test 2',grepTags='smoke+-high' --config specPattern='**/tags/*.cy.ts'",
-    "burn": "PROJECT_NAME=burn node ../../scripts/cypress.js run --env burn=5 --config specPattern='**/burn.cy.ts'",
+    "and": "PROJECT_NAME=and node ../../scripts/cypress.js run --expose grep='Test 2',grepTags='smoke+high' --config specPattern='**/tags/*.cy.ts'",
+    "and:not": "PROJECT_NAME=and-not node ../../scripts/cypress.js run --expose grep='Test 2',grepTags='smoke+-high' --config specPattern='**/tags/*.cy.ts'",
+    "burn": "PROJECT_NAME=burn node ../../scripts/cypress.js run --expose burn=5 --config specPattern='**/burn.cy.ts'",
     "each": "PROJECT_NAME=each node ../../scripts/cypress.js run --config specPattern='**/each.cy.ts'",
-    "filter:specs": "PROJECT_NAME=filter-specs node ../../scripts/cypress.js run --env grep='Test 2',grepFilterSpecs=true --config specPattern='**/tags/*.cy.ts'",
+    "filter:specs": "PROJECT_NAME=filter-specs node ../../scripts/cypress.js run --expose grep='Test 2',grepFilterSpecs=true --config specPattern='**/tags/*.cy.ts'",
     "grep": "PROJECT_NAME=grep node ../../scripts/cypress.js run --config specPattern='**/grep-task.cy.ts'",
-    "inverted": "PROJECT_NAME=inverted node ../../scripts/cypress.js run --env grep='-Test 2' --config specPattern='**/tags/*.cy.ts'",
+    "inverted": "PROJECT_NAME=inverted node ../../scripts/cypress.js run --expose grep='-Test 2' --config specPattern='**/tags/*.cy.ts'",
     "lint": "eslint",
     "multiple-registrations": "PROJECT_NAME=multiple-registrations node ../../scripts/cypress.js run --config specPattern='**/multiple-registrations.cy.ts'",
-    "omit:specs": "PROJECT_NAME=omit-specs node ../../scripts/cypress.js run --env grep='Test 2',grepOmitFiltered=true --config specPattern='**/tags/*.cy.ts'",
-    "or": "PROJECT_NAME=or node ../../scripts/cypress.js run --env grep='Test 1',grepTags='regression high' --config specPattern='**/tags/*.cy.ts'",
+    "omit:specs": "PROJECT_NAME=omit-specs node ../../scripts/cypress.js run --expose grep='Test 2',grepOmitFiltered=true --config specPattern='**/tags/*.cy.ts'",
+    "or": "PROJECT_NAME=or node ../../scripts/cypress.js run --expose grep='Test 1',grepTags='regression high' --config specPattern='**/tags/*.cy.ts'",
     "skip": "PROJECT_NAME=skip node ../../scripts/cypress.js run --config specPattern='**/*skip.cy.ts'",
-    "tags:inverted": "PROJECT_NAME=tag-inverted node ../../scripts/cypress.js run --env grepTags='-regression' --config specPattern='**/tags/*.cy.ts'",
-    "tags": "PROJECT_NAME=tags node ../../scripts/cypress.js run --env grepTags=smoke --config specPattern='**/tags/*.cy.ts'",
-    "tags:and": "PROJECT_NAME=tags-and node ../../scripts/cypress.js run --env grepTags='smoke+high' --config specPattern='**/tags/*.cy.ts'",
-    "tags:and:not": "PROJECT_NAME=tags-and-not node ../../scripts/cypress.js run --env grepTags='smoke+-high' --config specPattern='**/tags/*.cy.ts'",
-    "tags:before": "PROJECT_NAME=tags-before node ../../scripts/cypress.js run --env grepTags=@staging --config specPattern='**/before.cy.ts'",
-    "tags:config": "PROJECT_NAME=tags-config node ../../scripts/cypress.js run --env grepTags=config --config specPattern='**/config-tags.cy.ts'",
-    "tags:describe": "PROJECT_NAME=tags-describe node ../../scripts/cypress.js run --env grepTags=@smoke --config specPattern='**/describe-tags.cy.ts'",
-    "tags:filter:specs": "PROJECT_NAME=tags-filter-specs node ../../scripts/cypress.js run --env grepTags='regression',grepFilterSpecs=true --config specPattern='**/tags/*.cy.ts'",
-    "tags:inherit": "PROJECT_NAME=tags-inherit node ../../scripts/cypress.js run --env grepTags=@screen-b --config specPattern='**/inherits-tag.cy.ts'",
-    "tags:nested-describe": "PROJECT_NAME=tags-nested-describe node ../../scripts/cypress.js run --env grepTags='@smoke @integration' --config specPattern='**/nested-describe.cy.ts'",
-    "tags:omit:specs": "PROJECT_NAME=tags-omit-specs node ../../scripts/cypress.js run --env grepTags='regression',grepOmitFiltered=true --config specPattern='**/tags/*.cy.ts'",
-    "tags:or": "PROJECT_NAME=tags-or node ../../scripts/cypress.js run --env grepTags='regression high' --config specPattern='**/tags/*.cy.ts'",
-    "this": "PROJECT_NAME=this node ../../scripts/cypress.js run --env grep='this context' --config specPattern='**/this.cy.ts'",
-    "untagged": "PROJECT_NAME=untagged node ../../scripts/cypress.js run --env grepUntagged=true --config specPattern='**/tags/*.cy.ts'"
+    "tags:inverted": "PROJECT_NAME=tag-inverted node ../../scripts/cypress.js run --expose grepTags='-regression' --config specPattern='**/tags/*.cy.ts'",
+    "tags": "PROJECT_NAME=tags node ../../scripts/cypress.js run --expose grepTags=smoke --config specPattern='**/tags/*.cy.ts'",
+    "tags:and": "PROJECT_NAME=tags-and node ../../scripts/cypress.js run --expose grepTags='smoke+high' --config specPattern='**/tags/*.cy.ts'",
+    "tags:and:not": "PROJECT_NAME=tags-and-not node ../../scripts/cypress.js run --expose grepTags='smoke+-high' --config specPattern='**/tags/*.cy.ts'",
+    "tags:before": "PROJECT_NAME=tags-before node ../../scripts/cypress.js run --expose grepTags=@staging --config specPattern='**/before.cy.ts'",
+    "tags:config": "PROJECT_NAME=tags-config node ../../scripts/cypress.js run --expose grepTags=config --config specPattern='**/config-tags.cy.ts'",
+    "tags:describe": "PROJECT_NAME=tags-describe node ../../scripts/cypress.js run --expose grepTags=@smoke --config specPattern='**/describe-tags.cy.ts'",
+    "tags:filter:specs": "PROJECT_NAME=tags-filter-specs node ../../scripts/cypress.js run --expose grepTags='regression',grepFilterSpecs=true --config specPattern='**/tags/*.cy.ts'",
+    "tags:inherit": "PROJECT_NAME=tags-inherit node ../../scripts/cypress.js run --expose grepTags=@screen-b --config specPattern='**/inherits-tag.cy.ts'",
+    "tags:nested-describe": "PROJECT_NAME=tags-nested-describe node ../../scripts/cypress.js run --expose grepTags='@smoke @integration' --config specPattern='**/nested-describe.cy.ts'",
+    "tags:omit:specs": "PROJECT_NAME=tags-omit-specs node ../../scripts/cypress.js run --expose grepTags='regression',grepOmitFiltered=true --config specPattern='**/tags/*.cy.ts'",
+    "tags:or": "PROJECT_NAME=tags-or node ../../scripts/cypress.js run --expose grepTags='regression high' --config specPattern='**/tags/*.cy.ts'",
+    "this": "PROJECT_NAME=this node ../../scripts/cypress.js run --expose grep='this context' --config specPattern='**/this.cy.ts'",
+    "untagged": "PROJECT_NAME=untagged node ../../scripts/cypress.js run --expose grepUntagged=true --config specPattern='**/tags/*.cy.ts'"
   },
   "dependencies": {
     "debug": "^4.3.4",
@@ -46,7 +46,7 @@
     "typescript": "~5.4.5"
   },
   "peerDependencies": {
-    "cypress": ">=10"
+    "cypress": ">=15.10.0"
   },
   "exports": {
     ".": {
diff --git a/npm/grep/src/plugin.ts b/npm/grep/src/plugin.ts
index 49aed0c7323..398bb113164 100644
--- a/npm/grep/src/plugin.ts
+++ b/npm/grep/src/plugin.ts
@@ -7,7 +7,7 @@ import { parseGrep, shouldTestRun } from './utils'
 const debug = debugModule('@cypress/grep')

 interface CypressConfigOptions {
-  env?: Record<string, any>
+  expose?: Record<string, any>
   specPattern?: string | string[]
   excludeSpecPattern?: string | string[]
 }
@@ -17,11 +17,11 @@ interface CypressConfigOptions {
  * @param {Cypress.ConfigOptions} config
  */
 export function plugin (config: CypressConfigOptions): CypressConfigOptions {
-  if (!config || !config.env) {
+  if (!config || !config.expose) {
     return config
   }

-  const { env } = config
+  const { expose } = config

   if (!config.specPattern) {
     throw new Error(
@@ -30,15 +30,15 @@ export function plugin (config: CypressConfigOptions): CypressConfigOptions {
   }

   debug('@cypress/grep plugin version %s', version)
-  debug('Cypress config env object: %o', env)
+  debug('Cypress config expose object: %o', expose)

-  const grep = env.grep ? String(env.grep) : undefined
+  const grep = expose.grep ? String(expose.grep) : undefined

   if (grep) {
     console.log('@cypress/grep: tests with "%s" in their names', grep.trim())
   }

-  const grepTags = env.grepTags || env['grep-tags']
+  const grepTags = expose.grepTags || expose['grep-tags']

   if (grepTags) {
     console.log('@cypress/grep: filtering using tag(s) "%s"', grepTags)
@@ -47,28 +47,28 @@ export function plugin (config: CypressConfigOptions): CypressConfigOptions {
     debug('parsed grep tags %o', parsedGrep.tags)
   }

-  const grepBurn = env.grepBurn || env['grep-burn'] || env.burn
+  const grepBurn = expose.grepBurn || expose['grep-burn'] || expose.burn

   if (grepBurn) {
     console.log('@cypress/grep: running filtered tests %d times', grepBurn)
   }

-  const grepUntagged = env.grepUntagged || env['grep-untagged']
+  const grepUntagged = expose.grepUntagged || expose['grep-untagged']

   if (grepUntagged) {
     console.log('@cypress/grep: running untagged tests')
   }

-  const omitFiltered = env.grepOmitFiltered || env['grep-omit-filtered']
+  const omitFiltered = expose.grepOmitFiltered || expose['grep-omit-filtered']

   if (omitFiltered) {
     console.log('@cypress/grep: will omit filtered tests')
   }

   const { specPattern, excludeSpecPattern } = config
-  const integrationFolder = env.grepIntegrationFolder || process.cwd()
+  const integrationFolder = expose.grepIntegrationFolder || process.cwd()

-  const grepFilterSpecs = env.grepFilterSpecs === true || String(env.grepFilterSpecs).toLowerCase() === 'true'
+  const grepFilterSpecs = expose.grepFilterSpecs === true || String(expose.grepFilterSpecs).toLowerCase() === 'true'

   if (grepFilterSpecs) {
     debug('specPattern', specPattern)
diff --git a/npm/grep/src/register.ts b/npm/grep/src/register.ts
index 092056124e2..a4d3387ddcd 100644
--- a/npm/grep/src/register.ts
+++ b/npm/grep/src/register.ts
@@ -21,27 +21,27 @@ export function register (): void {
   // define Cypress.grep function
   if (!Cypress.grep) {
     Cypress.grep = function grep (grep?: string, tags?: string, burn?: string): void {
-      Cypress.env('grep', grep)
-      Cypress.env('grepTags', tags)
-      Cypress.env('grepBurn', burn)
-      Cypress.env('grep-tags', null)
-      Cypress.env('grep-burn', null)
-      Cypress.env('burn', null)
+      Cypress.expose('grep', grep)
+      Cypress.expose('grepTags', tags)
+      Cypress.expose('grepBurn', burn)
+      Cypress.expose('grep-tags', null)
+      Cypress.expose('grep-burn', null)
+      Cypress.expose('burn', null)

       debugInstance('set new grep to "%o" restarting tests', { grep, tags, burn })
       restartTests()
     }
   }

-  let grep: string | undefined = Cypress.env('grep')
+  let grep: string | undefined = Cypress.expose('grep')

   if (grep) {
     grep = String(grep).trim()
   }

-  const grepTags: string | undefined = Cypress.env('grepTags') || Cypress.env('grep-tags')
-  const burnSpecified: string | undefined = Cypress.env('grepBurn') || Cypress.env('grep-burn') || Cypress.env('burn')
-  const grepUntagged: string | undefined = Cypress.env('grepUntagged') || Cypress.env('grep-untagged')
+  const grepTags: string | undefined = Cypress.expose('grepTags') || Cypress.expose('grep-tags')
+  const burnSpecified: string | undefined = Cypress.expose('grepBurn') || Cypress.expose('grep-burn') || Cypress.expose('burn')
+  const grepUntagged: string | undefined = Cypress.expose('grepUntagged') || Cypress.expose('grep-untagged')

   if (!grep && !grepTags && !burnSpecified && !grepUntagged) {
     debugInstance('Nothing to grep, version %s', version)
@@ -50,13 +50,13 @@ export function register (): void {
   }

   const grepBurn: number =
-    Cypress.env('grepBurn') ||
-    Cypress.env('grep-burn') ||
-    Cypress.env('burn') ||
+    Cypress.expose('grepBurn') ||
+    Cypress.expose('grep-burn') ||
+    Cypress.expose('burn') ||
     1

   const omitFiltered: boolean =
-    Cypress.env('grepOmitFiltered') || Cypress.env('grep-omit-filtered')
+    Cypress.expose('grepOmitFiltered') || Cypress.expose('grep-omit-filtered')

   debugInstance('grep %o', { grep, grepTags, grepBurn, omitFiltered, version })
   if (!Cypress._.isInteger(grepBurn) || grepBurn < 1) {

PATCH

echo "Patch applied successfully."
