#!/bin/bash
set -e

cd /workspace/playwright

# Check if already applied (idempotency)
if [ -f "packages/playwright-cli-stub/package.json" ]; then
    echo "Patch already applied, skipping"
    exit 0
fi

# Create the playwright-cli-stub package directory and files
mkdir -p packages/playwright-cli-stub

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

cat > packages/playwright-cli-stub/playwright-cli-stub.js << 'JS_EOF'
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
JS_EOF

# Make the script executable
chmod +x packages/playwright-cli-stub/playwright-cli-stub.js

# Remove the playwright-cli script from root package.json
sed -i '/"playwright-cli": "node packages\/playwright\/lib\/cli\/client\/cli.js"/d' package.json

echo "Patch applied successfully"
