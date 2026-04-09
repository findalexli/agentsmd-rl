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
python3 << 'PYEOF'
import re
p = ".circleci/src/pipeline/@pipeline.yml"
with open(p) as f:
    txt = f.read()
txt = re.sub(
    r"      - unless:\n          condition:\n            # stop-only does not correctly match on windows.*?\n            equal: \[.*?windows-executor.*?\]\n          steps:\n            - run:\n                name: Stop \.only.*?\n                command: \|\n                  source \./scripts/ensure-node\.sh\n                  yarn stop-only-all\n",
    "",
    txt,
    flags=re.DOTALL
)
with open(p, "w") as f:
    f.write(txt)
PYEOF

# === 6. Update AGENTS.md — remove stop-only commands and update enforcement ===
python3 << 'PYEOF'
import re
p = "AGENTS.md"
with open(p) as f:
    txt = f.read()

# Remove stop-only command block
txt = re.sub(
    r"\n# Remove accidental \.only from test files \(specific file types\)\nyarn stop-only\n\n# Remove \.only from all test files in packages/\nyarn stop-only-all\n",
    "\n",
    txt
)

# Update the .only enforcement line
old_line = "- **No `.only` in tests** — \x60mocha/no-exclusive-tests: 'error'\x60; \x60yarn stop-only\x60 removes them."
new_line = "- **No `.only` in tests** — \x60mocha/no-exclusive-tests: 'error'\x60 (ESLint). Caught by \x60yarn lint\x60 and by pre-commit ESLint (\x60lint-staged\x60). For intentional \x60.only\x60 in fixtures or type samples, use \x60eslint-disable-next-line mocha/no-exclusive-tests\x60 (with a short comment)."
txt = txt.replace(old_line, new_line)

with open(p, "w") as f:
    f.write(txt)
PYEOF

echo "Patch applied successfully."
