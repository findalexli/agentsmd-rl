#!/bin/bash
set -e

cd /workspace/router

# Idempotency check - skip if already patched
if grep -q "rollupOptions: bundlerOptions" packages/start-plugin-core/src/plugin.ts 2>/dev/null; then
    echo "Patch already applied, skipping."
    exit 0
fi

# Fix utils.ts - remove version detection, keep only getBundlerOptions and other utils
cat > packages/start-plugin-core/src/utils.ts << 'EOF'
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
EOF

# Use node to fix plugin.ts
node << 'NODEJS'
const fs = require('fs');
const path = require('path');

const pluginPath = path.join(process.cwd(), 'packages/start-plugin-core/src/plugin.ts');
let content = fs.readFileSync(pluginPath, 'utf8');

// Fix import - remove bundlerOptionsKey
content = content.replace(
  "import { bundlerOptionsKey, getBundlerOptions } from './utils'",
  "import { getBundlerOptions } from './utils'"
);

// Fix client build config
const clientOldPattern = `build: {
                [bundlerOptionsKey]: {
                  input: {
                    main: ENTRY_POINTS.client,
                  },
                },
                outDir: getClientOutputDirectory(viteConfig),
              },`;

const clientNewPattern = `build: (() => {
                // Vite 7 reads rollupOptions, Vite 8 reads rolldownOptions.
                // Use the same object reference for both keys to avoid Vite 8's
                // deprecation warning when both are present.
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
              })(),`;

content = content.replace(clientOldPattern, clientNewPattern);

// Fix server build config
const serverOldPattern = `build: {
                ssr: true,
                [bundlerOptionsKey]: {
                  input:
                    getBundlerOptions(
                      viteConfig.environments?.[VITE_ENVIRONMENT_NAMES.server]
                        ?.build,
                    )?.input ?? serverAlias,
                },
                outDir: getServerOutputDirectory(viteConfig),
                commonjsOptions: {
                  include: [/node_modules/],
                },
                copyPublicDir:
                  viteConfig.environments?.[VITE_ENVIRONMENT_NAMES.server]
                    ?.build?.copyPublicDir ?? false,
              },`;

const serverNewPattern = `build: (() => {
                // Vite 7 reads rollupOptions, Vite 8 reads rolldownOptions.
                // Use the same object reference for both keys to avoid Vite 8's
                // deprecation warning when both are present.
                const bundlerOptions = {
                  input:
                    getBundlerOptions(
                      viteConfig.environments?.[VITE_ENVIRONMENT_NAMES.server]
                        ?.build,
                    )?.input ?? serverAlias,
                }
                return {
                  ssr: true,
                  rollupOptions: bundlerOptions,
                  rolldownOptions: bundlerOptions,
                  outDir: getServerOutputDirectory(viteConfig),
                  commonjsOptions: {
                    include: [/node_modules/],
                  },
                  copyPublicDir:
                    viteConfig.environments?.[VITE_ENVIRONMENT_NAMES.server]
                      ?.build?.copyPublicDir ?? false,
                }
              })(),`;

content = content.replace(serverOldPattern, serverNewPattern);

fs.writeFileSync(pluginPath, content);
console.log('plugin.ts fixed successfully');
NODEJS

# Create the changeset
mkdir -p .changeset
cat > .changeset/pretty-fans-eat.md << 'EOF'
---
'@tanstack/start-plugin-core': patch
---

fix(start-plugin-core): fix Vite 7/8 compat for bundler options
EOF

# Rebuild after patching
CI=1 NX_DAEMON=false pnpm nx run @tanstack/start-plugin-core:build --outputStyle=stream

echo "Patch applied successfully."
