#!/usr/bin/env bash
set -euo pipefail

cd /workspace/next.js

# Idempotent: skip if already applied
if grep -q '"build-all"' package.json 2>/dev/null; then
    echo "Patch already applied."
    exit 0
fi

# 1. Add "build-all" script to root package.json (after the "build" line)
sed -i '/"build": "turbo run build --remote-cache-timeout 60 --summarize true",/a\    "build-all": "turbo run build build-native-auto --remote-cache-timeout 60 --summarize true",' package.json

# 2. Rename "build" to "build-native-auto" in packages/next-swc/package.json
sed -i 's/"build": "node maybe-build-native.mjs"/"build-native-auto": "node maybe-build-native.mjs"/' packages/next-swc/package.json

# 3. Rename turbo.json -> turbo.jsonc and update task name + add comment
mv packages/next-swc/turbo.json packages/next-swc/turbo.jsonc

# Replace the first "build" task key with "build-native-auto" + comment
python3 -c "
p = 'packages/next-swc/turbo.jsonc'
t = open(p).read()
t = t.replace(
    '\"build\": {',
    '// \"auto\" is used by the workspace \`pnpm build-all\` script. It checks to see\n    // if there'\''s already an up-to-date precompiled version of turbopack\n    // available before performing the build.\n    \"build-native-auto\": {',
    1
)
open(p, 'w').write(t)
"

# 4. Update AGENTS.md references

# 4a. Change "Build everything" comment to "Build all JS code"
sed -i 's/^# Build everything$/# Build all JS code/' AGENTS.md

# 4b. Add "Build all JS and Rust code" section after "pnpm build" in Build Commands
python3 -c "
lines = open('AGENTS.md').readlines()
out = []
for i, line in enumerate(lines):
    out.append(line)
    if line.strip() == 'pnpm build' and i > 0 and 'Build all JS code' in out[-2]:
        out.append('\n')
        out.append('# Build all JS and Rust code\n')
        out.append('pnpm build-all\n')
open('AGENTS.md', 'w').writelines(out)
"

# 4c. Update "Use full pnpm build for branch switches" -> "pnpm build-all"
sed -i 's/Use full \`pnpm build\` for branch switches/Use full \`pnpm build-all\` for branch switches/' AGENTS.md

# 4d. Update bootstrap example: "pnpm build   # Sets up" -> "pnpm build-all   # Sets up"
sed -i 's/^pnpm build   # Sets up outputs/pnpm build-all   # Sets up outputs/' AGENTS.md

# 4e. Update "Capture to file" line to add "e.g."
sed -i 's/Capture to file once, then analyze: `pnpm build/Capture to file once, then analyze: e.g. `pnpm build/' AGENTS.md

# 4f. Update "First run after branch switch" -> build-all
sed -i 's|bootstrap (or if unsure)?\*\* → `pnpm build`|bootstrap (or if unsure)?** → `pnpm build-all`|' AGENTS.md

# 4g. Update "Edited Next.js code or Turbopack (Rust)?" -> build-all
sed -i 's|Turbopack (Rust)?\*\* → `pnpm build`|Turbopack (Rust)?** → `pnpm build-all`|' AGENTS.md

echo "Patch applied successfully."
