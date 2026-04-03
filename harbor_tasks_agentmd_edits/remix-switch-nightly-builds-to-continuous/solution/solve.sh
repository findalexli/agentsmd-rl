#!/usr/bin/env bash
set -euo pipefail

cd /workspace/remix

# Idempotent: skip if already applied
if grep -q 'remix#preview&path:packages/remix' README.md 2>/dev/null; then
    echo "Patch already applied."
    exit 0
fi

git apply --whitespace=fix - <<'PATCH'
diff --git a/.github/workflows/nightly.yml b/.github/workflows/nightly.yml
deleted file mode 100644
index 210291d0839..00000000000
--- a/.github/workflows/nightly.yml
+++ /dev/null
@@ -1,61 +0,0 @@
-# Create "installable" branches
-#
-# Primarily used via the `schedule` trigger to update the `nightly` branch with a
-# fresh build from `main` that can be used via direct pnpm install:
-#
-#   pnpm install "remix-run/remix#nightly&path:packages/remix"
-#
-# Can also be dispatched manually with base/installable branches to provide
-# `experimental` branches from PRs or otherwise.
-
-name: Create nightly/installable branch
-
-on:
-  schedule:
-    - cron: '0 7 * * *' # every day at 12AM PST
-  workflow_dispatch:
-    inputs:
-      baseBranch:
-        description: Base Branch
-        required: true
-      installableBranch:
-        description: Installable Branch
-        required: true
-
-concurrency:
-  group: ${{ github.workflow }}-${{ github.ref }}
-
-jobs:
-  build:
-    if: github.repository == 'remix-run/remix'
-    runs-on: ubuntu-latest
-    steps:
-      - name: Checkout
-        uses: actions/checkout@v4
-        with:
-          ref: ${{ inputs.baseBranch || 'main' }}
-
-      - name: Install pnpm
-        uses: pnpm/action-setup@v4
-
-      - name: Install Node.js
-        uses: actions/setup-node@v4
-        with:
-          node-version-file: 'package.json'
-          cache: pnpm
-
-      - name: Install dependencies
-        run: pnpm install --frozen-lockfile
-
-      - name: Setup git
-        run: |
-          git config --local user.email "hello@remix.run"
-          git config --local user.name "Remix Run Bot"
-
-      - name: Build installable branch
-        run: pnpm run setup-installable-branch ${{ inputs.installableBranch || 'nightly' }}
-
-      - name: Push changes
-        run: |
-          git push --force --set-upstream origin ${{ inputs.installableBranch || 'nightly' }}
-          echo "💿 pushed installable branch: https://github.com/$GITHUB_REPOSITORY/commit/$(git rev-parse HEAD)"
diff --git a/.github/workflows/preview.yml b/.github/workflows/preview.yml
index 16f53e2df3c..81176612d1b 100644
--- a/.github/workflows/preview.yml
+++ b/.github/workflows/preview.yml
@@ -1,10 +1,28 @@
-# Create "installable" PR preview branches
+# Create "installable" preview branches
 #
+# Commits to `main` push builds to a `preview` branch:
+#   pnpm install "remix-run/remix#preview&path:packages/remix"
+#
+# Pull Requests create `preview/{number}` branches:
 #   pnpm install "remix-run/remix#preview/12345&path:packages/remix"
+#
+# Can also be dispatched manually with base/installable branches to provide
+# `experimental` branches from PRs or otherwise.

-name: PR Preview
+name: Preview Build

 on:
+  push:
+    branches:
+      - main
+  workflow_dispatch:
+    inputs:
+      baseBranch:
+        description: Base Branch
+        required: true
+      installableBranch:
+        description: Installable Branch
+        required: true
   pull_request:
     types: [opened, synchronize, reopened, closed]

@@ -13,15 +31,27 @@ concurrency:
   cancel-in-progress: true

 jobs:
+  # Pushes to main or manually dispatched experimental previews
   preview:
     if: github.repository == 'remix-run/remix'
     runs-on: ubuntu-latest
     steps:
-      - name: Checkout
+      - name: Checkout (push)
+        if: github.event_name == 'push'
+        uses: actions/checkout@v4
+
+      - name: Checkout (pull_request)
+        if: github.event_name == 'pull_request'
         uses: actions/checkout@v4
         with:
           ref: ${{ github.event.pull_request.head.sha }}

+      - name: Checkout (workflow_dispatch)
+        if: github.event_name == 'workflow_dispatch'
+        uses: actions/checkout@v4
+        with:
+          ref: ${{ inputs.baseBranch }}
+
       - name: Install pnpm
         uses: pnpm/action-setup@v4

@@ -34,28 +64,43 @@ jobs:
       - name: Install dependencies
         run: pnpm install --frozen-lockfile

-      # Build previews when PR's are open
-      - name: Build preview branch
-        if: github.event.pull_request.state == 'open'
-        env:
-          GITHUB_TOKEN: ${{ github.token }}
+      - name: Setup git
         run: |
           git config --local user.email "hello@remix.run"
           git config --local user.name "Remix Run Bot"

-          PREVIEW_BRANCH_NAME="preview/${{ github.event.pull_request.number }}"
-          pnpm run setup-installable-branch $PREVIEW_BRANCH_NAME
+      # Build and force push over the preview branch
+      - name: Build/push branch (push)
+        if: github.event_name == 'push'
+        run: |
+          pnpm run setup-installable-branch preview
+          git push --force --set-upstream origin preview
+          echo "💿 pushed installable branch: https://github.com/$GITHUB_REPOSITORY/commit/$(git rev-parse HEAD)"

-          git push --force --set-upstream origin $PREVIEW_BRANCH_NAME
+      # Build and force push over the PR preview/* branch + comment on the PR
+      - name: Build/push branch (pull_request)
+        if: github.event_name == 'pull_request' && github.event.pull_request.state == 'open'
+        env:
+          GITHUB_TOKEN: ${{ github.token }}
+        run: |
+          pnpm run setup-installable-branch preview/${{ github.event.pull_request.number }}
+          git push --force --set-upstream origin preview/${{ github.event.pull_request.number }}
           echo "pushed installable branch: https://github.com/$GITHUB_REPOSITORY/commit/$(git rev-parse HEAD)"
+          pnpm run pr-preview comment ${{ github.event.pull_request.number }} preview/${{ github.event.pull_request.number }}

-          pnpm run pr-preview comment ${{ github.event.pull_request.number }} $PREVIEW_BRANCH_NAME
+      # Build and normal push for experimental releases to avoid unintended force
+      # pushes over remote branches in case of a branch name collision
+      - name: Build/push branch (workflow_dispatch)
+        if: github.event_name == 'workflow_dispatch'
+        run: |
+          pnpm run setup-installable-branch ${{ inputs.installableBranch }}
+          git push --set-upstream origin ${{ inputs.installableBranch }}
+          echo "💿 pushed installable branch: https://github.com/$GITHUB_REPOSITORY/commit/$(git rev-parse HEAD)"

-      # Cleanup previews when PR's are closed
+      # Cleanup PR preview/* branches when the PR is closed
       - name: Cleanup preview branch
-        if: github.event.pull_request.state == 'closed'
+        if: github.event_name == 'pull_request' && github.event.pull_request.state == 'closed'
         env:
           GITHUB_TOKEN: ${{ github.token }}
         run: |
-          PREVIEW_BRANCH_NAME="preview/${{ github.event.pull_request.number }}"
-          pnpm run pr-preview cleanup ${{ github.event.pull_request.number }} $PREVIEW_BRANCH_NAME
+          pnpm run pr-preview cleanup ${{ github.event.pull_request.number }} preview/${{ github.event.pull_request.number }}
diff --git a/CONTRIBUTING.md b/CONTRIBUTING.md
index 709044cd25a..b8618018e08 100644
--- a/CONTRIBUTING.md
+++ b/CONTRIBUTING.md
@@ -160,17 +160,17 @@ The prerelease suffix is stripped (e.g. `3.0.0-rc.7` → `3.0.0`). The bump type

-## Nightly Builds
+## Preview builds

-We also maintain installable nightly builds in a `nightly` branch as a way for folks to test out the latest `main` branch without needing to publish nightly releases to npm and clutter up the npm registry and version history UI.
+We maintain installable builds of `main` in a `preview` branch as a way for folks to test out the latest `main` branch without needing to publish releases to npm and clutter up the npm registry and version history UI.

-This is managed via the [`nightly` workflow](/.github/workflows/nightly.yaml) which uses the [`setup-installable-branch.ts`](./scripts/setup-installable-branch.ts) script to build and commit the build and required `package.json` changes to the `nightly` branch.
+This is managed via the [`preview` workflow](/.github/workflows/preview.yaml) which uses the [`setup-installable-branch.ts`](./scripts/setup-installable-branch.ts) script to build and commit the build and required `package.json` changes to the `preview` branch on every new commit to `main`.

-The nightly build can be [installed directly](https://pnpm.io/package-sources#install-from-a-git-repository-combining-different-parameters) with `pnpm` (version 9+):
+The `preview` branch build can be [installed directly](https://pnpm.io/package-sources#install-from-a-git-repository-combining-different-parameters) with `pnpm` (version 9+):

 ```sh
-pnpm install "remix-run/remix#nightly&path:packages/remix"
+pnpm install "remix-run/remix#preview&path:packages/remix"

 # Or, just install a single package
-pnpm install "remix-run/remix#nightly&path:packages/@remix-run/fetch-router"
+pnpm install "remix-run/remix#preview&path:packages/@remix-run/fetch-router"
 ```
diff --git a/README.md b/README.md
index 4d2a8c76a49..0de6064b1e5 100644
--- a/README.md
+++ b/README.md
@@ -70,13 +70,13 @@ npm install @remix-run/fetch-router
 ```

-If you want to play around with the bleeding edge, we also build the latest `main` branch every night into a `nightly` branch which can be [installed directly](https://pnpm.io/package-sources#install-from-a-git-repository-combining-different-parameters) with `pnpm` (version 9+):
+If you want to play around with the bleeding edge, we also build the latest `main` branch into a `preview` branch which can be [installed directly](https://pnpm.io/package-sources#install-from-a-git-repository-combining-different-parameters) with `pnpm` (version 9+):

 ```sh
-pnpm install "remix-run/remix#nightly&path:packages/remix"
+pnpm install "remix-run/remix#preview&path:packages/remix"

 # Or, just install a single package
-pnpm install "remix-run/remix#nightly&path:packages/@remix-run/fetch-router"
+pnpm install "remix-run/remix#preview&path:packages/@remix-run/fetch-router"
 ```
diff --git a/scripts/setup-installable-branch.ts b/scripts/setup-installable-branch.ts
index 4573dfc3a69..fc9e05d592b 100644
--- a/scripts/setup-installable-branch.ts
+++ b/scripts/setup-installable-branch.ts
@@ -5,9 +5,9 @@ import { logAndExec } from './utils/process.ts'

 /**
  * This script prepares a base branch (usually `main`) to be PNPM-installable
- * directly from GitHub via a new branch (usually `nightly`):
+ * directly from GitHub via a new branch (usually `preview`):
  *
- *   pnpm install "remix-run/remix#nightly&path:packages/remix"
+ *   pnpm install "remix-run/remix#preview&path:packages/remix"
  *
  * To do this, we can run a build, make some minor changes to the repo, and
  * commit the build + changes to the new branch. These changes would never be
@@ -22,35 +22,19 @@ import { logAndExec } from './utils/process.ts'
  *  - Copies all `publishConfig`'s down so we get `exports` from `dist/` instead of `src/`
  *  - Commits the changes
  *
- * Then, after pushing, `pnpm install "remix-run/remix#nightly&path:packages/remix"`
+ * Then, after pushing, `pnpm install "remix-run/remix#preview&path:packages/remix"`
  * sees the `remix` nested deps and they all point to github with similar URLs so
  * they install as nested deps the same way.
  */

-let { values, positionals } = util.parseArgs({
-  options: {
-    branch: {
-      type: 'string',
-      short: 'b',
-    },
-  },
+let { positionals } = util.parseArgs({
   allowPositionals: true,
 })

 // Use first positional argument or fall back to --branch flag or default
-let installableBranch = positionals[0] || values.branch || 'nightly'
-
-// Refuse to overwrite existing branches except for cron-driven workflow branches
-let allowedOverwrites = ['nightly']
-let remoteBranches = logAndExec('git branch -r', true)
-if (
-  remoteBranches.includes(`origin/${installableBranch}`) &&
-  !allowedOverwrites.includes(installableBranch)
-) {
-  throw new Error(
-    `Error: Branch \`${installableBranch}\` already exists on origin. ` +
-      `Delete it first or use a different branch name.`,
-  )
+let installableBranch = positionals[0]
+if (!installableBranch) {
+  throw new Error('Error: You must provide an installable branch name')
 }

 // Error if git status is not clean

PATCH

echo "Patch applied successfully."
