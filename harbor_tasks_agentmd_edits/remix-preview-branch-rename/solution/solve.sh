#!/usr/bin/env bash
set -euo pipefail

cd /workspace/remix

# Idempotent: skip if already applied
if grep -q 'preview/main' README.md 2>/dev/null; then
    echo "Patch already applied."
    exit 0
fi

git apply --whitespace=fix - <<'PATCH'
diff --git a/.github/workflows/preview.yml b/.github/workflows/preview.yml
index 28e625d50e0..ae7398c7d4c 100644
--- a/.github/workflows/preview.yml
+++ b/.github/workflows/preview.yml
@@ -1,7 +1,7 @@
 # Create "installable" preview branches
 #
-# Commits to `main` push builds to a `preview` branch:
-#   pnpm install "remix-run/remix#preview&path:packages/remix"
+# Commits to `main` push builds to a `preview/main` branch:
+#   pnpm install "remix-run/remix#preview/main&path:packages/remix"
 #
 # Pull Requests create `preview/{number}` branches:
 #   pnpm install "remix-run/remix#preview/12345&path:packages/remix"
@@ -69,25 +69,15 @@ jobs:
           git config --local user.email "hello@remix.run"
           git config --local user.name "Remix Run Bot"

-      # Build and force push over the preview branch
+      # Build and force push over the preview/main branch
       - name: Build/push branch (push)
         if: github.event_name == 'push'
         run: |
-          pnpm run setup-installable-branch preview
-
-          echo ""
-          set -x
-          git status
-          git fetch origin
-          git branch --all
-
-          git push --force --set-upstream origin preview
-
-          set +x
-
+          pnpm run setup-installable-branch preview/main
+          git push --force --set-upstream origin preview/main
           echo "💿 pushed installable branch: https://github.com/$GITHUB_REPOSITORY/commit/$(git rev-parse HEAD)"

-      # Build and force push over the PR preview/* branch + comment on the PR
+      # Build and force push over the PR preview/{number} branch + comment on the PR
       - name: Build/push branch (pull_request)
         if: github.event_name == 'pull_request' && github.event.pull_request.state == 'open'
         env:
@@ -107,7 +97,7 @@ jobs:
           git push --set-upstream origin ${{ inputs.installableBranch }}
           echo "💿 pushed installable branch: https://github.com/$GITHUB_REPOSITORY/commit/$(git rev-parse HEAD)"

-      # Cleanup PR preview/* branches when the PR is closed
+      # Cleanup PR preview/{number} branches when the PR is closed
       - name: Cleanup preview branch
         if: github.event_name == 'pull_request' && github.event.pull_request.state == 'closed'
         env:
diff --git a/CONTRIBUTING.md b/CONTRIBUTING.md
index 893a3b810f2..f0172c1e238 100644
--- a/CONTRIBUTING.md
+++ b/CONTRIBUTING.md
@@ -162,15 +162,15 @@ The prerelease suffix is stripped (e.g. `3.0.0-rc.7` → `3.0.0`). The bump type

 ## Preview builds

-We maintain installable builds of `main` in a `preview` branch as a way for folks to test out the latest `main` branch without needing to publish releases to npm and clutter up the npm registry and version history UI.
+We maintain installable builds of `main` in a `preview/main` branch as a way for folks to test out the latest `main` branch without needing to publish releases to npm and clutter up the npm registry and version history UI.

-This is managed via the [`preview` workflow](/.github/workflows/preview.yaml) which uses the [`setup-installable-branch.ts`](./scripts/setup-installable-branch.ts) script to build and commit the build and required `package.json` changes to the `preview` branch on every new commit to `main`.
+This is managed via the [`preview` workflow](/.github/workflows/preview.yaml) which uses the [`setup-installable-branch.ts`](./scripts/setup-installable-branch.ts) script to build and commit the build and required `package.json` changes to the `preview/main` branch on every new commit to `main`.

-The `preview` branch build can be [installed directly](https://pnpm.io/package-sources#install-from-a-git-repository-combining-different-parameters) with `pnpm` (version 9+):
+The `preview/main` branch build can be [installed directly](https://pnpm.io/package-sources#install-from-a-git-repository-combining-different-parameters) with `pnpm` (version 9+):

 ```sh
-pnpm install "remix-run/remix#preview&path:packages/remix"
+pnpm install "remix-run/remix#preview/main&path:packages/remix"

 # Or, just install a single package
-pnpm install "remix-run/remix#preview&path:packages/@remix-run/fetch-router"
+pnpm install "remix-run/remix#preview/main&path:packages/@remix-run/fetch-router"
 ```
diff --git a/README.md b/README.md
index 0de6064b1e5..e6ffa1c0ed5 100644
--- a/README.md
+++ b/README.md
@@ -70,13 +70,13 @@ npm install @remix-run/fetch-router
 ```

-If you want to play around with the bleeding edge, we also build the latest `main` branch into a `preview` branch which can be [installed directly](https://pnpm.io/package-sources#install-from-a-git-repository-combining-different-parameters) with `pnpm` (version 9+):
+If you want to play around with the bleeding edge, we also build the latest `main` branch into a `preview/main` branch which can be [installed directly](https://pnpm.io/package-sources#install-from-a-git-repository-combining-different-parameters) with `pnpm` (version 9+):

 ```sh
-pnpm install "remix-run/remix#preview&path:packages/remix"
+pnpm install "remix-run/remix#preview/main&path:packages/remix"

 # Or, just install a single package
-pnpm install "remix-run/remix#preview&path:packages/@remix-run/fetch-router"
+pnpm install "remix-run/remix#preview/main&path:packages/@remix-run/fetch-router"
 ```
diff --git a/scripts/setup-installable-branch.ts b/scripts/setup-installable-branch.ts
index fc9e05d592b..ebf6f10e14e 100644
--- a/scripts/setup-installable-branch.ts
+++ b/scripts/setup-installable-branch.ts
@@ -5,9 +5,9 @@ import { logAndExec } from './utils/process.ts'

 /**
  * This script prepares a base branch (usually `main`) to be PNPM-installable
- * directly from GitHub via a new branch (usually `preview`):
+ * directly from GitHub via a new branch (usually `preview/main`):
  *
- *   pnpm install "remix-run/remix#preview&path:packages/remix"
+ *   pnpm install "remix-run/remix#preview/main&path:packages/remix"
  *
  * To do this, we can run a build, make some minor changes to the repo, and
  * commit the build + changes to the new branch. These changes would never be
@@ -22,7 +22,7 @@ import { logAndExec } from './utils/process.ts'
  *  - Copies all `publishConfig`'s down so we get `exports` from `dist/` instead of `src/`
  *  - Commits the changes
  *
- * Then, after pushing, `pnpm install "remix-run/remix#preview&path:packages/remix"`
+ * Then, after pushing, `pnpm install "remix-run/remix#preview/main&path:packages/remix"`
  * sees the `remix` nested deps and they all point to github with similar URLs so
  * they install as nested deps the same way.
  */

PATCH

echo "Patch applied successfully."
