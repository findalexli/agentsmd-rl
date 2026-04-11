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
          ref: ${{ github.event.pull_request.head.sha }}

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

# 3. Update setup-installable-branch.ts
setup_content = open('scripts/setup-installable-branch.ts').read()

# Replace the entire parseArgs section and comments
new_setup = '''import * as fsp from 'node:fs/promises'
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
 * commit the changes to the new branch. These changes would never be
 * committed to `main` and exist only in the installable branch.
 *
 * Overview of the changes:
 *
 *  - Build packages
 *  - Updates peer deps to use `workspace:` protocol
 *  - Adds `main` field to packages that don't have them
 *  - Adds `types` field to packages that don't have them
 *  - Removes all `node:*` protocol prefixes from package.json deps
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
'''

# Keep everything after "Error if git status is not clean"
match = re.search(r'// Error if git status is not clean\n(.*)', setup_content, re.DOTALL)
if match:
    rest = match.group(1)
else:
    # Find the line that starts the git status check
    lines = setup_content.split('\n')
    start_idx = 0
    for i, line in enumerate(lines):
        if 'git status' in line and 'not clean' in line:
            start_idx = i + 1
            break
    rest = '\n'.join(lines[start_idx:])

open('scripts/setup-installable-branch.ts', 'w').write(new_setup + rest)
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
