#!/bin/bash
set -e

cd /workspace/playwright

# Check if already applied
if [ -f "packages/playwright-cli-stub/playwright-cli-stub.js" ]; then
    echo "Gold patch already applied."
    exit 0
fi

# Create the playwright-cli-stub package directory
mkdir -p packages/playwright-cli-stub

# Create package.json for the stub package
cat > packages/playwright-cli-stub/package.json << 'PKG_EOF'
{
  "name": "playwright-cli-stub",
  "version": "0.0.0",
  "private": true,
  "bin": {
    "playwright-cli": "playwright-cli-stub.js"
  }
}
PKG_EOF

# Create the stub JavaScript file
cat > packages/playwright-cli-stub/playwright-cli-stub.js << 'JS_EOF'
#!/usr/bin/env node
/**
 * Copyright (c) Microsoft Corporation.
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
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
JS_EOF

chmod +x packages/playwright-cli-stub/playwright-cli-stub.js

# Update package.json - remove playwright-cli script
# Use node to modify package.json
node << 'NODE_EOF'
const fs = require('fs');
const pkg = JSON.parse(fs.readFileSync('package.json', 'utf8'));
if (pkg.scripts && pkg.scripts['playwright-cli']) {
    delete pkg.scripts['playwright-cli'];
    fs.writeFileSync('package.json', JSON.stringify(pkg, null, 2) + '\n');
    console.log('Removed playwright-cli script from package.json');
} else {
    console.log('playwright-cli script already removed or not present');
}
NODE_EOF

# Link the new package to node_modules
if ! grep -q "playwright-cli-stub" package-lock.json 2>/dev/null; then
    # Add to package-lock.json workspaces if needed
    node << 'NODE_EOF'
const fs = require('fs');
try {
    const pkgLock = JSON.parse(fs.readFileSync('package-lock.json', 'utf8'));
    if (pkgLock.packages && pkgLock.packages['']) {
        // Ensure node_modules/playwright-cli-stub is linked
        pkgLock.packages['node_modules/playwright-cli-stub'] = {
            resolved: 'packages/playwright-cli-stub',
            link: true
        };
        // Add the actual package entry
        pkgLock.packages['packages/playwright-cli-stub'] = {
            version: '0.0.0',
            bin: {
                'playwright-cli': 'playwright-cli-stub.js'
            }
        };
        fs.writeFileSync('package-lock.json', JSON.stringify(pkgLock, null, 2) + '\n');
        console.log('Updated package-lock.json');
    }
} catch (e) {
    console.log('Could not update package-lock.json:', e.message);
}
NODE_EOF
fi

# Update SKILL.md with the new installation instructions
cat > packages/playwright/src/skill/SKILL.md << 'SKILL_EOF'
---
name: playwright-cli
description: Automates browser interactions for web testing, form filling, screenshots, and data extraction. Use when the user needs to navigate websites, interact with web pages, fill forms, take screenshots, test web applications, or extract information from web pages.
allowed-tools: Bash(playwright-cli:*)
---

# Browser Automation with playwright-cli

## Quick start

\`\`\`bash
# open new browser
playwright-cli open
# navigate to a page
playwright-cli goto https://playwright.dev
# interact with the page using refs from the snapshot
playwright-cli click e15
playwright-cli type "page.click"
playwright-cli press Enter
# take a screenshot (rarely used, as snapshot is more common)
playwright-cli screenshot
# close the browser
playwright-cli close
\`\`\`

## Commands

### Core

\`\`\`bash
playwright-cli open
# open and navigate right away
playwright-cli open https://example.com/
playwright-cli goto https://playwright.dev
playwright-cli type "search query"
playwright-cli click e3
playwright-cli dblclick e7
playwright-cli fill e5 "user@example.com"
playwright-cli drag e2 e8
playwright-cli hover e4
playwright-cli select e9 "option-value"
playwright-cli upload ./document.pdf
playwright-cli check e12
playwright-cli uncheck e12
playwright-cli snapshot
playwright-cli snapshot --filename=after-click.yaml
playwright-cli eval "document.title"
playwright-cli eval "el => el.textContent" e5
playwright-cli dialog-accept
playwright-cli dialog-accept "confirmation text"
playwright-cli dialog-dismiss
playwright-cli resize 1920 1080
playwright-cli close
\`\`\`

### Navigation

\`\`\`bash
playwright-cli go-back
playwright-cli go-forward
playwright-cli reload
\`\`\`

### Keyboard

\`\`\`bash
playwright-cli press Enter
playwright-cli press ArrowDown
playwright-cli keydown Shift
playwright-cli keyup Shift
\`\`\`

### Mouse

\`\`\`bash
playwright-cli mousemove 150 300
playwright-cli mousedown
playwright-cli mousedown right
playwright-cli mouseup
playwright-cli mouseup right
playwright-cli mousewheel 0 100
\`\`\`

### Save as

\`\`\`bash
playwright-cli screenshot
playwright-cli screenshot e5
playwright-cli screenshot --filename=page.png
playwright-cli pdf --filename=page.pdf
\`\`\`

### Tabs

\`\`\`bash
playwright-cli tab-list
playwright-cli tab-new
playwright-cli tab-new https://example.com/page
playwright-cli tab-close
playwright-cli tab-close 2
\`\`\`

### Session

\`\`\`bash
playwright-cli save-snapshot snapshot.yaml
playwright-cli load-snapshot snapshot.yaml
\`\`\`

### Misc

\`\`\`bash
# wait for specific element
timeout 60s playwright-cli wait-for e12
# kill all browser processes (useful on errors)
playwright-cli kill-all
\`\`\`

## Installation

If global \`playwright-cli\` command is not available, try a local version via \`npx playwright-cli\`:

\`\`\`bash
npx playwright-cli --version
\`\`\`

When local version is available, use \`npx playwright-cli\` in all commands. Otherwise, install \`playwright-cli\` as a global command:

\`\`\`bash
npm install -g @playwright/cli@latest
\`\`\`

## Example: Form submission

\`\`\`bash
# Navigate to the page
playwright-cli open https://example.com/contact

# Take a snapshot to see element refs
playwright-cli snapshot

# Fill the form using the refs from snapshot
playwright-cli fill e3 "John Doe"
playwright-cli fill e4 "john@example.com"
playwright-cli fill e5 "Hello, this is a test message"

# Submit the form
playwright-cli click e6

# Verify success message
playwright-cli eval "document.body.innerText.includes('Thank you')"

# Close browser
playwright-cli close
\`\`\`

## Troubleshooting

- If commands timeout, check that the element ref is still valid (page may have changed)
- Use \`playwright-cli kill-all\` if browser hangs
- Run with \`PWDEBUG=1\` environment variable for verbose logging
SKILL_EOF

echo "Gold patch applied successfully."
