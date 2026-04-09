#!/usr/bin/env bash
set -euo pipefail

cd /workspace/playwright

# Idempotent: skip if already applied
if [ -f packages/playwright-cli-stub/playwright-cli-stub.js ]; then
    echo "Patch already applied."
    exit 0
fi

# --- 1. Create the playwright-cli-stub package ---
mkdir -p packages/playwright-cli-stub

cat > packages/playwright-cli-stub/package.json <<'EOF'
{
  "name": "playwright-cli-stub",
  "version": "0.0.0",
  "private": true,
  "bin": {
    "playwright-cli": "playwright-cli-stub.js"
  }
}
EOF

cat > packages/playwright-cli-stub/playwright-cli-stub.js <<'STUBEOF'
#!/usr/bin/env node
/**
 * Copyright (c) Microsoft Corporation.
 *
 * Licensed under the Apache License, Version 2.0 (the 'License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 * http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */

const { program } = require('playwright/lib/cli/client/program');

program().catch(e => {
  console.error(e.message);
  process.exit(1);
});
STUBEOF

chmod +x packages/playwright-cli-stub/playwright-cli-stub.js

# --- 2. Remove old playwright-cli script from root package.json ---
node -e "
const fs = require('fs');
const pkg = JSON.parse(fs.readFileSync('package.json', 'utf8'));
delete pkg.scripts['playwright-cli'];
fs.writeFileSync('package.json', JSON.stringify(pkg, null, 2) + '\n');
"

# --- 3. Update SKILL.md installation section ---
python3 - <<'PYEOF'
with open("packages/playwright/src/skill/SKILL.md", "r") as f:
    content = f.read()

old_section = """## Installation

If `playwright-cli` is not available, install it globally:

```bash
npm install -g @playwright/cli@latest
```

Once installed, `playwright-cli` will be available as a global command.

Alternatively, install the package locally and use `npx` to run without a global install. This is useful for hermetic environments, but adds a slight `npx` overhead on each command execution:

```bash
npx playwright-cli open https://example.com
npx playwright-cli click e1
```"""

new_section = """## Installation

If global `playwright-cli` command is not available, try a local version via `npx playwright-cli`:

```bash
npx playwright-cli --version
```

When local version is available, use `npx playwright-cli` in all commands. Otherwise, install `playwright-cli` as a global command:

```bash
npm install -g @playwright/cli@latest
```"""

content = content.replace(old_section, new_section)

with open("packages/playwright/src/skill/SKILL.md", "w") as f:
    f.write(content)
PYEOF

echo "Patch applied successfully."
