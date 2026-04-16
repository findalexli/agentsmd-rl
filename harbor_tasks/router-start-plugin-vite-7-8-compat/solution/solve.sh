#!/bin/bash
set -e

cd /workspace/router

# Check if already applied (idempotency)
if grep -q "rollupOptions: bundlerOptions" packages/start-plugin-core/src/plugin.ts; then
    echo "Fix already applied"
    exit 0
fi

# Step 1: Fix utils.ts - remove isRolldown and bundlerOptionsKey, keep getBundlerOptions
cat > packages/start-plugin-core/src/utils.ts << 'ENDOFFILE'
/** Read `build.rollupOptions` or `build.rolldownOptions` from a build config. */
export function getBundlerOptions(build: any): any {
  return build?.rolldownOptions ?? build?.rollupOptions
}

export function resolveViteId(id: string) {
  return `\0${id}`
}

export function createLogger(prefix: string) {
  const label = `[${prefix}]`
  return {
    log: (...args: any) => console.log(label, ...args),
    debug: (...args: any) => console.debug(label, ...args),
    info: (...args: any) => console.info(label, ...args),
    warn: (...args: any) => console.warn(label, ...args),
    error: (...args: any) => console.error(label, ...args),
  }
}
ENDOFFILE

# Step 2: Fix plugin.ts using Python for complex replacements
python3 << 'PYEOF'
import re

# Read the plugin.ts file
with open('packages/start-plugin-core/src/plugin.ts', 'r') as f:
    content = f.read()

# Fix the import line
content = content.replace(
    "import { bundlerOptionsKey, getBundlerOptions } from './utils'",
    "import { getBundlerOptions } from './utils'"
)

# Fix the client environment build config
old_client = '''build: {
                [bundlerOptionsKey]: {
                  input: {
                    main: ENTRY_POINTS.client,
                  },
                },
                outDir: getClientOutputDirectory(viteConfig),
              },'''

new_client = '''build: (() => {
                // Use the same object reference for both keys to avoid
                // Vite 8's deprecation warning when both are present.
                // Vite 7 reads rollupOptions, Vite 8 reads rolldownOptions.
                const bundlerOptions = {
                  input: {
                    main: ENTRY_POINTS.client,
                  },
                }
                return {
                  rollupOptions: bundlerOptions,
                  rolldownOptions: bundlerOptions,
                  outDir: getClientOutputDirectory(viteConfig),
                }
              })(),'''

content = content.replace(old_client, new_client)

# Fix the server environment build config
old_server = '''[bundlerOptionsKey]: {
                  input:
                    getBundlerOptions(
                      viteConfig.environments?.[VITE_ENVIRONMENT_NAMES.server]
                        ?.build,
                    )?.input ?? serverAlias,
                },'''

new_server = '''...(() => {
                  const bundlerOptions = {
                    input:
                      getBundlerOptions(
                        viteConfig.environments?.[VITE_ENVIRONMENT_NAMES.server]
                          ?.build,
                      )?.input ?? serverAlias,
                  }
                  return {
                    rollupOptions: bundlerOptions,
                    rolldownOptions: bundlerOptions,
                  }
                })(),'''

content = content.replace(old_server, new_server)

# Write the updated content
with open('packages/start-plugin-core/src/plugin.ts', 'w') as f:
    f.write(content)

print("plugin.ts updated successfully")
PYEOF

# Verify the patch was applied
if ! grep -q "rollupOptions: bundlerOptions" packages/start-plugin-core/src/plugin.ts; then
    echo "ERROR: Patch was not applied correctly"
    echo "Looking for pattern in plugin.ts:"
    grep -n "rollupOptions" packages/start-plugin-core/src/plugin.ts || echo "Pattern not found"
    exit 1
fi

if ! grep -q "rolldownOptions: bundlerOptions" packages/start-plugin-core/src/plugin.ts; then
    echo "ERROR: rolldownOptions not applied correctly"
    exit 1
fi

# Rebuild to ensure the fix compiles (follow AGENTS.md: use CI=1 NX_DAEMON=false, prefer pnpm nx)
export CI=1
export NX_DAEMON=false
pnpm nx run @tanstack/start-plugin-core:build

echo "Fix applied successfully"
