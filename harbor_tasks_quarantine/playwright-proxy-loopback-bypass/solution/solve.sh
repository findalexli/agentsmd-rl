#!/bin/bash
set -e

cd /workspace/playwright

# Apply the fix for proxy bypass loopback issue
# This patch modifies chromium.ts to respect localhost bypass settings

# Check if already applied (idempotency check)
if grep -q "bypassesLoopback" packages/playwright-core/src/server/chromium/chromium.ts; then
    echo "Fix already applied, skipping"
    exit 0
fi

# Apply the code fix using a heredoc patch
cat > /tmp/fix.patch << 'EOF'
diff --git a/packages/playwright-core/src/server/chromium/chromium.ts b/packages/playwright-core/src/server/chromium/chromium.ts
index 04b6c01053ede..f0b955c13c631 100644
--- a/packages/playwright-core/src/server/chromium/chromium.ts
+++ b/packages/playwright-core/src/server/chromium/chromium.ts
@@ -349,7 +349,8 @@ export class Chromium extends BrowserType {
         proxyBypassRules.push('<-loopback>');
       if (proxy.bypass)
         proxyBypassRules.push(...proxy.bypass.split(',').map(t => t.trim()).map(t => t.startsWith('.') ? '*' + t : t));
-      if (!process.env.PLAYWRIGHT_DISABLE_FORCED_CHROMIUM_PROXIED_LOOPBACK && !proxyBypassRules.includes('<-loopback>'))
+      const bypassesLoopback = proxyBypassRules.some(rule => rule === '<-loopback>' || rule === 'localhost' || rule === '127.0.0.1' || rule === '::1');
+      if (!process.env.PLAYWRIGHT_DISABLE_FORCED_CHROMIUM_PROXIED_LOOPBACK && !bypassesLoopback)
         proxyBypassRules.push('<-loopback>');
       if (proxyBypassRules.length > 0)
         chromeArguments.push(`--proxy-bypass-list=${proxyBypassRules.join(';')}`);
EOF

# Apply the patch
git apply /tmp/fix.patch

# Create the new github.md skill file
mkdir -p .claude/skills/playwright-dev
cat > .claude/skills/playwright-dev/github.md << 'GITHUBMD'
---
name: playwright-github
description: Explains how to upload fixes to GitHub for Playwright issues
---

# Uploading a Fix for a GitHub Issue

## Branch naming

Create a branch named after the issue number:

```
git checkout -b fix-39562
```

## Committing changes

Use conventional commit format with a scope:

- `fix(proxy): description` — bug fixes
- `feat(locator): description` — new features
- `chore(cli): description` — maintenance, refactoring, tests

The commit body must be a single line: `Fixes: https://github.com/microsoft/playwright/issues/39562`

Stage only the files related to the fix. Do not use `git add -A` or `git add .`.

```
git add src/server/proxy.ts tests/proxy.spec.ts
git commit -m "$(cat <<'EOF'
fix(proxy): handle SOCKS proxy authentication

Fixes: https://github.com/microsoft/playwright/issues/39562
EOF
)"
```

## Pushing

Push the branch to origin:

```
git push origin fix-39562
```

## Full example

For issue https://github.com/microsoft/playwright/issues/39562:

```bash
git checkout -b fix-39562
# ... make changes ...
git add <changed-files>
git commit -m "$(cat <<'EOF'
fix(proxy): handle SOCKS proxy authentication

Fixes: https://github.com/microsoft/playwright/issues/39562
EOF
)"
git push origin fix-39562
```
GITHUBMD

# Update SKILL.md to reference the new github.md file
mkdir -p .claude/skills/playwright-dev
cat > .claude/skills/playwright-dev/SKILL.md << 'SKILLMD'
---
name: playwright-dev
description: Explains how to develop Playwright - add APIs, MCP tools, CLI commands, and vendor dependencies.
---

# Playwright Development Guide

## Table of Contents

- [Library Architecture](library.md) — client/server/dispatcher structure, protocol layer, DEPS rules
- [Adding and Modifying APIs](api.md) — define API docs, implement client/server, add tests
- [MCP Tools and CLI Commands](mcp-dev.md) — add MCP tools, CLI commands, config options
- [Vendoring Dependencies](vendor.md) — bundle third-party npm packages into playwright-core or playwright
- [Uploading Fixes to GitHub](github.md) — branch naming, commit format, pushing fixes for issues

## Build
- Assume watch is running and everything is up to date.
- If not, run `npm run build`.

## Lint
- Run `npm run flint` to lint everything before commit.
SKILLMD

echo "Fix applied successfully"
