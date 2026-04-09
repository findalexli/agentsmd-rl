#!/usr/bin/env bash
set -euo pipefail

cd /workspace/remix

# Idempotent: skip if already applied
if grep -q 'setup-installable-branch' package.json 2>/dev/null; then
    echo "Patch already applied."
    exit 0
fi

echo "Applying fixes..."

# Fix 1: Modify scripts/utils/process.ts - logAndExec function using patch
patch -p1 --fuzz=3 << 'PROCESSEOF'
diff --git a/scripts/utils/process.ts b/scripts/utils/process.ts
index a44bd81cd46..476ce92e27a 100644
--- a/scripts/utils/process.ts
+++ b/scripts/utils/process.ts
@@ -15,7 +15,12 @@ export function getRootDir(): string {
   return process.cwd()
 }
 
-export function logAndExec(command: string, options?: cp.ExecSyncOptions): void {
+export function logAndExec(command: string, captureOutput = false): string {
   console.log(`$ ${command}`)
-  cp.execSync(command, { stdio: 'inherit', ...options })
+  if (captureOutput) {
+    return cp.execSync(command, { stdio: 'pipe', encoding: 'utf-8' }).trim()
+  } else {
+    cp.execSync(command, { stdio: 'inherit' })
+    return ''
+  }
 }
 
PROCESSEOF

# Fix 2: Add script to package.json - after lint:fix line
patch -p1 --fuzz=3 << 'PACKAGEEOF'
diff --git a/package.json b/package.json
index ec43b574503..0f71cc96a60 100644
--- a/package.json
+++ b/package.json
@@ -32,6 +32,7 @@
     "generate-remix": "node scripts/generate-remix.ts",
     "lint": "eslint . --max-warnings=0",
     "lint:fix": "eslint . --fix",
+    "setup-installable-branch": "node scripts/setup-installable-branch.ts",
     "test": "pnpm --parallel run test",
     "typecheck": "pnpm -r typecheck"
   }
PACKAGEEOF

# Fix 3: Create .github/workflows/nightly.yml
mkdir -p .github/workflows
cat > .github/workflows/nightly.yml << 'WORKFLOWEOF'
# Create "installable" branches
#
# Primarily used via the `schedule` trigger to update the `nightly` branch with a
# fresh build from `main` that can be used via direct pnpm install:
#
#   pnpm i "remix-run/remix#nightly&path:packages/remix"
#
# Can also be dispatched manually with base/installable branches to provide
# `experimental` branches from PRs or otherwise

name: 💿 Nightly/Installable Branch

on:
  schedule:
    - cron: "0 7 * * *" # every day at 12AM PST
  workflow_dispatch:
    inputs:
      baseBranch:
        description: Base Branch
        required: true
      installableBranch:
        description: Installable Branch
        required: true

concurrency:
  group: ${{ github.workflow }}-${{ github.ref }}

jobs:
  build:
    if: github.repository == 'remix-run/remix'
    runs-on: ubuntu-latest
    steps:
      - name: Checkout
        uses: actions/checkout@v4
        with:
          ref: ${{ inputs.baseBranch || 'main' }}

      - name: Install pnpm
        uses: pnpm/action-setup@v4

      - name: Install Node.js
        uses: actions/setup-node@v4
        with:
          node-version-file: "package.json"
          cache: pnpm

      - name: Install dependencies
        run: pnpm install --frozen-lockfile

      - name: Setup git
        run: |
          git config --local user.email "hello@remix.run"
          git config --local user.name "Remix Run Bot"

      - name: Build installable branch
        run: pnpm run setup-installable-branch ${{ inputs.installableBranch || 'nightly' }}

      - name: Push changes
        run: |
          git push
          echo "💿 pushed updates: https://github.com/$GITHUB_REPOSITORY/commit/$(git rev-parse HEAD)"
WORKFLOWEOF

# Fix 4: Create scripts/setup-installable-branch.ts
cat > scripts/setup-installable-branch.ts << 'SCRIPTEOF'
import * as fsp from "node:fs/promises";
import * as path from "node:path";
import * as util from "node:util";
import { logAndExec } from "./utils/process.ts";

/**
 * This script prepares a base branch (usually `main`) to be PNPM-installable
 * directly from GitHub via a new branch (usually `nightly`):
 *
 *   pnpm install "remix-run/remix#nightly&path:packages/remix"
 *
 * To do this, we can run a build, make some minor changes to the repo, and
 * commit the build + changes to the new branch. These changes would never be
 * down-merged back to the source branch.
 *
 * This script does the following:
 *  - Checks out the new branch and resets it to the base (current) branch
 *  - Runs a build
 *  - Removes `dist/` from `.gitignore`
 *  - Moves all `@remix-run/*` peerDeps up to normal deps to get past any peerDep
 *    warnings on install
 *  - Updates all internal `@remix-run/*` deps to use the github format for the
 *    given installable branch
 *  - Copies all `publishConfig`'s down so we get `exports` from `dist/` instead of `src/`
 *  - Commits the changes
 *
 *
 * Then, after pushing, `pnpm install "remix-run/remix#nightly&path:packages/remix"`
 * sees the `remix` nested deps and they all point to github with similar URLs so
 * they install as nested deps the same way.
 */

let { values, positionals } = util.parseArgs({
  options: {
    branch: {
      type: "string",
      short: "b",
    },
  },
  allowPositionals: true,
});

// Use first positional argument or fall back to --branch flag or default
let installableBranch = positionals[0] || values.branch || "nightly";

// Refuse to overwrite existing branches except for cron-driven workflow branches
let allowedOverwrites = ["nightly"];
let remoteBranches = logAndExec("git branch -r", true);
if (
  remoteBranches.includes(`origin/${installableBranch}`) &&
  !allowedOverwrites.includes(installableBranch)
) {
  throw new Error(
    `Error: Branch \`${installableBranch}\` already exists on origin. ` +
      `Delete it first or use a different branch name.`,
  );
}

// Error if git status is not clean
let gitStatus = logAndExec("git status --porcelain", true);
if (gitStatus) {
  throw new Error(
    "Error: Git working directory is not clean. Commit or stash changes first.",
  );
}

// Capture the current branch name
let baseBranch = logAndExec("git branch --show-current", true).trim();
let sha = logAndExec("git rev-parse --short HEAD ", true).trim();

console.log(
  `Preparing installable branch \`${installableBranch}\` from ` +
    `base branch \`${baseBranch}\` at sha ${sha}`,
);

// Switch to new branch and reset to current commit on base branch
logAndExec(`git checkout -B ${installableBranch}`);

// Build dist/ folders
logAndExec("pnpm build");

await updateGitignore();
await updatePackageDependencies();

logAndExec("git add .");
logAndExec(`git commit -a -m "installable build from ${baseBranch} at ${sha}"`);

console.log(
  [
    "",
    `✅ Done!`,
    "",
    `You can now push the \`${installableBranch}\` branch to GitHub and install via:`,
    "",
    `  pnpm install "remix-run/remix#${installableBranch}&path:packages/remix"`,
  ].join("\n"),
);

// Remove `dist` from gitignore so we include built code in the repo
async function updateGitignore() {
  let gitignorePath = path.join(process.cwd(), ".gitignore");
  let content = await fsp.readFile(gitignorePath, "utf-8");
  let filtered = content
    .split("\n")
    .filter((line) => !line.trim().startsWith("dist"))
    .join("\n");
  await fsp.writeFile(gitignorePath, filtered);
  console.log("Updated .gitignore");
}

// Update `package.json` files to point to this branch on github
async function updatePackageDependencies() {
  let packagesDir = path.join(process.cwd(), "packages");

  let packageDirs = await fsp.readdir(packagesDir, { withFileTypes: true });

  for (let dir of packageDirs) {
    if (!dir.isDirectory()) continue;

    let packageJsonPath = path.join(packagesDir, dir.name, "package.json");
    let content = await fsp.readFile(packageJsonPath, "utf-8");
    let pkg = JSON.parse(content);

    // To avoid any peerDep warnings, move any `@remix-run/` peerDeps to deps
    if (pkg.peerDependencies) {
      for (let name of Object.keys(pkg.peerDependencies)) {
        if (name.startsWith("@remix-run/")) {
          if (!pkg.dependencies) pkg.dependencies = {};
          pkg.dependencies[name] = pkg.peerDependencies[name];
          delete pkg.peerDependencies[name];
        }
      }
    }

    // Point all `@remix-run/` dependencies to this branch on github
    if (pkg.dependencies) {
      for (let name of Object.keys(pkg.dependencies)) {
        if (name.startsWith("@remix-run/")) {
          let packageName = name.replace("@remix-run/", "");
          pkg.dependencies[name] =
            `remix-run/remix#${installableBranch}&path:packages/${packageName}`;
        }
      }
    }

    // Apply `publishConfig` overrides
    if (pkg.publishConfig) {
      if (pkg.name === "remix" && pkg.publishConfig.peerDependencies) {
        // Delete these from the remix package if they exist
        delete pkg.publishConfig.peerDependencies;
      }
      Object.assign(pkg, pkg.publishConfig);
      delete pkg.publishConfig;
    }

    await fsp.writeFile(packageJsonPath, JSON.stringify(pkg, null, 2) + "\n");
    console.log(`Updated ${dir.name}`);
  }

  console.log("Done");
}

function commitChanges() {}
SCRIPTEOF

# Fix 5: Add installation section to README.md (before Contributing section)
if ! grep -q "## Installation" README.md; then
    cat > /tmp/readme_insert.txt << 'EOF'

## Installation

```sh
npm install remix

# Or, just install a single package
npm install @remix-run/fetch-router
```

If you want to play around with the bleeding edge, we also build the latest `main` branch every night into a `nightly` branch which can be [installed directly](https://pnpm.io/package-sources#install-from-a-git-repository-combining-different-parameters) with `pnpm` (version 9+):

```sh
pnpm install "remix-run/remix#nightly&path:packages/remix"

# Or, just install a single package
pnpm install "remix-run/remix#nightly&path:packages/@remix-run/fetch-router"
```

EOF
    # Insert before "## Contributing"
    sed -i '/^## Contributing$/e cat /tmp/readme_insert.txt' README.md
fi

# Fix 6: Add nightly builds section to CONTRIBUTING.md (at end)
if ! grep -q "## Nightly Builds" CONTRIBUTING.md; then
    cat >> CONTRIBUTING.md << 'CONTRIBUTEEOF'

## Nightly Builds

We also maintain installable nightly builds in a `nightly` branch as a way for folks to test out the latest `main` branch without needing to publish nightly releases to npm and clutter up the npm registry and version history UI.

This is managed via the [`nightly` workflow](/.github/workflows/nightly.yaml) which uses the [`setup-installable-branch.ts`](./scripts/setup-installable-branch.ts) script to build and commit the build and required `package.json` changes to the `nightly` branch.

The nightly build can be [installed directly](https://pnpm.io/package-sources#install-from-a-git-repository-combining-different-parameters) with `pnpm` (version 9+):

```sh
pnpm install "remix-run/remix#nightly&path:packages/remix"

# Or, just install a single package
pnpm install "remix-run/remix#nightly&path:packages/@remix-run/fetch-router"
```
CONTRIBUTEEOF
fi

# Fix 7: Run format to fix any formatting issues in new files
corepack enable 2>/dev/null || true
pnpm format 2>/dev/null || true

echo "Patch applied successfully."
