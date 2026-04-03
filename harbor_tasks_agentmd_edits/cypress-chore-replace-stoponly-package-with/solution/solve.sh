#!/usr/bin/env bash
set -euo pipefail

cd /workspace/cypress

# Idempotent: skip if already applied
if grep -q "mocha/no-exclusive-tests.*error" packages/eslint-config/src/baseConfig.ts 2>/dev/null; then
    echo "Patch already applied."
    exit 0
fi

# === 1. Add mocha/no-exclusive-tests rule to ESLint baseConfig ===
sed -i "s|'mocha/no-mocha-arrows': 'off',|'mocha/no-exclusive-tests': 'error',\n      'mocha/no-mocha-arrows': 'off',|" \
    packages/eslint-config/src/baseConfig.ts

# === 2. Remove stop-only scripts from package.json ===
sed -i '/"stop-only":/d' package.json
sed -i '/"stop-only-all":/d' package.json

# Remove the stop-only dependency line
sed -i '/"stop-only": "3\.4\.1"/d' package.json

# === 3. Add eslint-disable comment to cypress-tests.ts ===
sed -i '1i\/* eslint-disable mocha/no-exclusive-tests -- dtslint-style samples for Mocha/Cypress API typings */' \
    cli/types/tests/cypress-tests.ts

# === 4. Add node_modules to eslint-plugin-dev .eslintignore ===
echo "node_modules" >> npm/eslint-plugin-dev/.eslintignore

# === 5. Remove Stop .only CI step from CircleCI pipeline ===
python3 -c "
import re
p = '.circleci/src/pipeline/@pipeline.yml'
with open(p) as f:
    txt = f.read()
# Remove the unless block for stop-only (the 10-line block)
txt = re.sub(
    r'      - unless:\n          condition:\n            # stop-only does not correctly match on windows.*?\n            equal: \[.*?windows-executor.*?\]\n          steps:\n            - run:\n                name: Stop \.only.*?\n                command: \|\n                  source \./scripts/ensure-node\.sh\n                  yarn stop-only-all\n',
    '',
    txt,
    flags=re.DOTALL
)
with open(p, 'w') as f:
    f.write(txt)
"

# === 6. Update AGENTS.md — remove stop-only commands and update enforcement ===
python3 -c "
import re
p = 'AGENTS.md'
with open(p) as f:
    txt = f.read()

# Remove stop-only command block
txt = re.sub(
    r'\n# Remove accidental \.only from test files \(specific file types\)\nyarn stop-only\n\n# Remove \.only from all test files in packages/\nyarn stop-only-all\n',
    '\n',
    txt
)

# Update the .only enforcement line
txt = txt.replace(
    \"- **No \\\`.only\\\` in tests** — \\\`mocha/no-exclusive-tests: 'error'\\\`; \\\`yarn stop-only\\\` removes them.\",
    \"- **No \\\`.only\\\` in tests** — \\\`mocha/no-exclusive-tests: 'error'\\\` (ESLint). Caught by \\\`yarn lint\\\` and by pre-commit ESLint (\\\`lint-staged\\\`). For intentional \\\`.only\\\` in fixtures or type samples, use \\\`eslint-disable-next-line mocha/no-exclusive-tests\\\` (with a short comment).\"
)

with open(p, 'w') as f:
    f.write(txt)
"

echo "Patch applied successfully."
