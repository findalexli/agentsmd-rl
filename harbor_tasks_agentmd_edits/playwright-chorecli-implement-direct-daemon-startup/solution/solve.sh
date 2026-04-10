#!/usr/bin/env bash
set -euo pipefail

cd /workspace/playwright

# Idempotent: skip if already applied
if grep -q 'throwBrowserIsNotInstalledError' packages/playwright/src/mcp/browser/browserContextFactory.ts 2>/dev/null; then
    echo 'Patch already applied.'
    exit 0
fi

echo 'Fetching gold versions from merge commit...'

# TypeScript files
git show e0e7f41e80247f857e97cb23f4833d2eee2122fe:packages/playwright/src/mcp/browser/browserContextFactory.ts > packages/playwright/src/mcp/browser/browserContextFactory.ts
git show e0e7f41e80247f857e97cb23f4833d2eee2122fe:packages/playwright/src/mcp/browser/browserServerBackend.ts > packages/playwright/src/mcp/browser/browserServerBackend.ts
git show e0e7f41e80247f857e97cb23f4833d2eee2122fe:packages/playwright/src/mcp/browser/context.ts > packages/playwright/src/mcp/browser/context.ts
git show e0e7f41e80247f857e97cb23f4833d2eee2122fe:packages/playwright/src/mcp/extension/cdpRelay.ts > packages/playwright/src/mcp/extension/cdpRelay.ts
git show e0e7f41e80247f857e97cb23f4833d2eee2122fe:packages/playwright/src/mcp/program.ts > packages/playwright/src/mcp/program.ts
git show e0e7f41e80247f857e97cb23f4833d2eee2122fe:packages/playwright/src/mcp/sdk/server.ts > packages/playwright/src/mcp/sdk/server.ts
git show e0e7f41e80247f857e97cb23f4833d2eee2122fe:packages/playwright/src/mcp/terminal/DEPS.list > packages/playwright/src/mcp/terminal/DEPS.list
git show e0e7f41e80247f857e97cb23f4833d2eee2122fe:packages/playwright/src/mcp/terminal/daemon.ts > packages/playwright/src/mcp/terminal/daemon.ts
git show e0e7f41e80247f857e97cb23f4833d2eee2122fe:packages/playwright/src/mcp/terminal/helpGenerator.ts > packages/playwright/src/mcp/terminal/helpGenerator.ts
git show e0e7f41e80247f857e97cb23f4833d2eee2122fe:packages/playwright/src/mcp/terminal/program.ts > packages/playwright/src/mcp/terminal/program.ts

# Markdown files
git show e0e7f41e80247f857e97cb23f4833d2eee2122fe:packages/playwright/src/skill/SKILL.md > packages/playwright/src/skill/SKILL.md
git show e0e7f41e80247f857e97cb23f4833d2eee2122fe:packages/playwright/src/skill/references/session-management.md > packages/playwright/src/skill/references/session-management.md

echo 'Patch applied successfully.'
