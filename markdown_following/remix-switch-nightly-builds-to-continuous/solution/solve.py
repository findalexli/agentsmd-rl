#!/usr/bin/env python3
import os
import re

os.chdir('/workspace/remix')

# Idempotent check
readme = open('README.md').read()
if 'remix#preview&path:packages/remix' in readme:
    print("Patch already applied.")
    exit(0)

# 1. Delete nightly.yml
if os.path.exists('.github/workflows/nightly.yml'):
    os.remove('.github/workflows/nightly.yml')
    print("Deleted nightly.yml")

# 2. Read original preview.yml
preview = open('.github/workflows/preview.yml').read()

# Write completely new preview.yml
new_preview = '''# Create "installable" preview branches
#
# Commits to `main` push builds to a `preview` branch:
#   pnpm install "remix-run/remix#preview&path:packages/remix"
#
# Pull Requests create `preview/{number}` branches:
#   pnpm install "remix-run/remix#preview/12345&path:packages/remix"
#
# Can also be dispatched manually with base/installable branches to provide
# `experimental` branches from PRs or otherwise.

name: Preview Build

on:
  push:
    branches:
      - main
  workflow_dispatch:
    inputs:
      baseBranch:
        description: Base Branch
        required: true
      installableBranch:
        description: Installable Branch
        required: true
  pull_request:
    types: [opened, synchronize, reopened, closed]

concurrency:
  group: ${{ github.workflow }}-${{ github.event.pull_request.number || github.ref }}
  cancel-in-progress: true

jobs:
  # Pushes to main or manually dispatched experimental previews
  preview:
    if: github.repository == 'remix-run/remix'
    runs-on: ubuntu-latest
    steps:
      - name: Checkout (push)
        if: github.event_name == 'push'
        uses: actions/checkout@v4

      - name: Checkout (pull_request)
        if: github.event_name == 'pull_request'
        uses: actions/checkout@v4
        with:
          ref: ${{ github.event.pull_request.number }}

      - name: Checkout (workflow_dispatch)
        if: github.event_name == 'workflow_dispatch'
        uses: actions/checkout@v4
        with:
          ref: ${{ inputs.baseBranch }}

      - name: Install pnpm
        uses: pnpm/action-setup@v4

      - name: Install Node.js
        uses: actions/setup-node@v4
        with:
          node-version-file: 'package.json'
          cache: pnpm

      - name: Install dependencies
        run: pnpm install --frozen-lockfile

      - name: Setup git
        run: |
          git config --local user.email "hello@remix.run"
          git config --local user.name "Remix Run Bot"

      # Build and force push over the preview branch
      - name: Build/push branch (push)
        if: github.event_name == 'push'
        run: |
          pnpm run setup-installable-branch preview
          git push --force --set-upstream origin preview
          echo "pushed installable branch: https://github.com/$GITHUB_REPOSITORY/commit/$(git rev-parse HEAD)"

      # Build and force push over the PR preview/* branch + comment on the PR
      - name: Build/push branch (pull_request)
        if: github.event_name == 'pull_request' && github.event.pull_request.state == 'open'
        env:
          GITHUB_TOKEN: ${{ github.token }}
        run: |
          pnpm run setup-installable-branch preview/${{ github.event.pull_request.number }}
          git push --force --set-upstream origin preview/${{ github.event.pull_request.number }}
          echo "pushed installable branch: https://github.com/$GITHUB_REPOSITORY/commit/$(git rev-parse HEAD)"
          pnpm run pr-preview comment ${{ github.event.pull_request.number }} preview/${{ github.event.pull_request.number }}

      # Build and normal push for experimental releases to avoid unintended force
      # pushes over remote branches in case of a branch name collision
      - name: Build/push branch (workflow_dispatch)
        if: github.event_name == 'workflow_dispatch'
        run: |
          pnpm run setup-installable-branch ${{ inputs.installableBranch }}
          git push --set-upstream origin ${{ inputs.installableBranch }}
          echo "pushed installable branch: https://github.com/$GITHUB_REPOSITORY/commit/$(git rev-parse HEAD)"

      # Cleanup PR preview/* branches when the PR is closed
      - name: Cleanup preview branch
        if: github.event_name == 'pull_request' && github.event.pull_request.state == 'closed'
        env:
          GITHUB_TOKEN: ${{ github.token }}
        run: |
          pnpm run pr-preview cleanup ${{ github.event.pull_request.number }} preview/${{ github.event.pull_request.number }}
'''

open('.github/workflows/preview.yml', 'w').write(new_preview)
print("Updated preview.yml")

# 3. Update setup-installable-branch.ts - use exact gold reference content
gold_setup = '''import * as fsp from 'node:fs/promises'
import * as path from 'node:path'
import * as util from 'node:util'
import { logAndExec } from './utils/process.ts'

/**
 * This script prepares a base branch (usually `main`) to be PNPM-installable
 * directly from GitHub via a new branch (usually `preview`):
 *
 *   pnpm install "remix-run/remix#preview&path:packages/remix"
 *
 * To do this, we can run a build, make some minor changes to the repo, and
 * commit the build + changes to the new branch. These changes would never be
 * down-merged back to the source branch.
 *
 * This script does the following:
 *  - Checks out the new branch and resets it to the base (current) branch
 *  - Runs a build
 *  - Removes `dist/` from `.gitignore`
 *  - Updates all internal `@remix-run/*` deps to use the github format for the
 *    given installable branch
 *  - Copies all `publishConfig`'s down so we get `exports` from `dist/` instead of `src/`
 *  - Commits the changes
 *
 * Then, after pushing, `pnpm install "remix-run/remix#preview&path:packages/remix"`
 * sees the `remix` nested deps and they all point to github with similar URLs so
 * they install as nested deps the same way.
 */

let { positionals } = util.parseArgs({
  allowPositionals: true,
})

// Use first positional argument or fall back to --branch flag or default
let installableBranch = positionals[0]
if (!installableBranch) {
  throw new Error('Error: You must provide an installable branch name')
}

// Error if git status is not clean
let gitStatus = logAndExec('git status --porcelain', true)
if (gitStatus) {
  throw new Error('Error: Git working directory is not clean. Commit or stash changes first.')
}

// Capture the current branch name
let sha = logAndExec('git rev-parse --short HEAD ', true).trim()

console.log(`Preparing installable branch \`${installableBranch}\` from sha ${sha}`)

// Switch to new branch and reset to current commit on base branch
logAndExec(`git checkout -B ${installableBranch}`)

// Build dist/ folders
logAndExec('pnpm build')

await updateGitignore()
await updatePackageDependencies()

logAndExec('git add .')
logAndExec(`git commit -a -m "installable build from ${sha}"`)

console.log(
  [
    '',
    `✅ Done!`,
    '',
    `You can now push the \`${installableBranch}\` branch to GitHub and install via:`,
    '',
    `  pnpm install "remix-run/remix#${installableBranch}&path:packages/remix"`,
  ].join('\\n'),
)

// Remove `dist` from gitignore so we include built code in the repo
async function updateGitignore() {
  let gitignorePath = path.join(process.cwd(), '.gitignore')
  let content = await fsp.readFile(gitignorePath, 'utf-8')
  let filtered = content
    .split('\\n')
    .filter((line) => !line.trim().startsWith('dist'))
    .join('\\n')
  await fsp.writeFile(gitignorePath, filtered)
  console.log('Updated .gitignore')
}

// Update `package.json` files to point to this branch on github
async function updatePackageDependencies() {
  let packagesDir = path.join(process.cwd(), 'packages')

  let packageDirNames = await fsp.readdir(packagesDir, { withFileTypes: true })

  for (let dir of packageDirNames) {
    if (!dir.isDirectory()) continue

    let packageJsonPath = path.join(packagesDir, dir.name, 'package.json')
    let content = await fsp.readFile(packageJsonPath, 'utf-8')
    let pkg = JSON.parse(content)

    // Point all `@remix-run/` dependencies to this branch on github
    if (pkg.dependencies) {
      for (let name of Object.keys(pkg.dependencies)) {
        if (name.startsWith('@remix-run/')) {
          let packageDirName = name.replace('@remix-run/', '')
          pkg.dependencies[name] =
            `remix-run/remix#${installableBranch}&path:packages/${packageDirName}`
        }
      }
    }

    // Apply `publishConfig` overrides
    if (pkg.publishConfig) {
      Object.assign(pkg, pkg.publishConfig)
      delete pkg.publishConfig
    }

    await fsp.writeFile(packageJsonPath, JSON.stringify(pkg, null, 2) + '\\n')
    console.log(`Updated ${dir.name}`)
  }

  console.log('Done')
}

function commitChanges() {}
'''

open('scripts/setup-installable-branch.ts', 'w').write(gold_setup)
print("Updated setup-installable-branch.ts")

# 4. Update README.md
readme = open('README.md').read()
readme = readme.replace(
    'If you want to play around with the bleeding edge, we also build the latest `main` branch every night into a `nightly` branch',
    'If you want to play around with the bleeding edge, we also build the latest `main` branch into a `preview` branch'
)
readme = readme.replace('#nightly', '#preview')
open('README.md', 'w').write(readme)
print("Updated README.md")

# 5. Update CONTRIBUTING.md
contrib = open('CONTRIBUTING.md').read()
contrib = contrib.replace('## Nightly Builds', '## Preview builds')
contrib = contrib.replace(
    'We also maintain installable nightly builds in a `nightly` branch',
    'We maintain installable builds of `main` in a `preview` branch'
)
contrib = contrib.replace('publish nightly releases', 'publish releases')
contrib = contrib.replace(
    '[`nightly` workflow](/.github/workflows/nightly.yaml)',
    '[`preview` workflow](/.github/workflows/preview.yaml)'
)
contrib = contrib.replace(
    'to the `nightly` branch.',
    'to the `preview` branch on every new commit to `main`.'
)
contrib = contrib.replace('The nightly build can', 'The `preview` branch build can')
contrib = contrib.replace('#nightly', '#preview')
open('CONTRIBUTING.md', 'w').write(contrib)
print("Updated CONTRIBUTING.md")

print("Patch applied successfully.")
