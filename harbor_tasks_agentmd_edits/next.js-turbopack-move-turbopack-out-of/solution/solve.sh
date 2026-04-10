#!/usr/bin/env bash
set -euo pipefail

cd /workspace/next.js

# Idempotent: skip if already applied
if grep -q '"build-all":' package.json 2>/dev/null; then
    echo "Patch already applied."
    exit 0
fi

# 1. Add build-all script to root package.json
node -e "
const fs = require('fs');
const pkg = JSON.parse(fs.readFileSync('./package.json', 'utf8'));
pkg.scripts = pkg.scripts || {};
pkg.scripts['build-all'] = 'turbo run build build-native-auto --remote-cache-timeout 60 --summarize true';
fs.writeFileSync('./package.json', JSON.stringify(pkg, null, 2) + '\n');
console.log('Added build-all script to root package.json');
"

# 2. Rename build to build-native-auto in packages/next-swc/package.json
node -e "
const fs = require('fs');
const pkg = JSON.parse(fs.readFileSync('./packages/next-swc/package.json', 'utf8'));
pkg.scripts = pkg.scripts || {};
if (pkg.scripts.build && !pkg.scripts['build-native-auto']) {
    pkg.scripts['build-native-auto'] = pkg.scripts.build;
    delete pkg.scripts.build;
}
fs.writeFileSync('./packages/next-swc/package.json', JSON.stringify(pkg, null, 2) + '\n');
console.log('Renamed build to build-native-auto in next-swc/package.json');
"

# 3. Rename turbo.json to turbo.jsonc and update task name
mv packages/next-swc/turbo.json packages/next-swc/turbo.jsonc

# Update the task name from build to build-native-auto in turbo.jsonc
node -e "
const fs = require('fs');
let content = fs.readFileSync('./packages/next-swc/turbo.jsonc', 'utf8');

// Replace the build task with build-native-auto and add comment
content = content.replace(
    '\"build\": {',
    '// \"auto\" is used by the workspace \`pnpm build-all\` script. It checks to see\n    // if there\\'s already an up-to-date precompiled version of turbopack\n    // available before performing the build.\n    \"build-native-auto\": {'
);

fs.writeFileSync('./packages/next-swc/turbo.jsonc', content);
console.log('Updated turbo.jsonc with build-native-auto task');
"

# 4. Update AGENTS.md - update build commands documentation
node -e "
const fs = require('fs');
let content = fs.readFileSync('./AGENTS.md', 'utf8');

// Replace \"# Build everything\n pnpm build\" with JS/Rust separation
content = content.replace(
    /# Build everything\n(\s*)pnpm build/,
    '# Build all JS code\n\$1pnpm build\n\n\$1# Build all JS and Rust code\n\$1pnpm build-all'
);

// Update references to use pnpm build-all for full builds
content = content.replace(
    /Use full \\\`pnpm build\\\` for branch switches/,
    'Use full \`pnpm build-all\` for branch switches'
);

content = content.replace(
    /git checkout <branch>\n(\s*)pnpm build   # Sets up outputs/,
    'git checkout <branch>\n\$1pnpm build-all   # Sets up outputs'
);

content = content.replace(
    /- Capture to file once, then analyze: \\\`pnpm build 2>&1 \| tee \/tmp\/build\.log\\\`/,
    '- Capture to file once, then analyze: e.g. \`pnpm build 2>&1 | tee /tmp/build.log\`'
);

content = content.replace(
    /- \*\*First run after branch switch\/bootstrap \(or if unsure\)\?\*\* → \\\`pnpm build\\\`/,
    '- **First run after branch switch/bootstrap (or if unsure)?** → \`pnpm build-all\`'
);

content = content.replace(
    /- \*\*Edited Next\.js code or Turbopack \(Rust\)\?\*\* → \\\`pnpm build\\\`/,
    '- **Edited Next.js code or Turbopack (Rust)?** → \`pnpm build-all\`'
);

fs.writeFileSync('./AGENTS.md', content);
console.log('Updated AGENTS.md');
"

echo "Patch applied successfully."
