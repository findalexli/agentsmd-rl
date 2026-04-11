#!/usr/bin/env bash
set -euo pipefail

cd /workspace/infisical

# Idempotent: skip if already applied
if grep -q 'Dependency Policy' CLAUDE.md 2>/dev/null; then
    echo "Patch already applied."
    exit 0
fi

# Create backend .npmrc
echo "min-release-age=7" > backend/.npmrc

# Create frontend .npmrc  
echo "min-release-age=7" > frontend/.npmrc

# Add engines to backend/package.json after "main" field using node
node -e '
const fs = require("fs");
const pkg = JSON.parse(fs.readFileSync("backend/package.json", "utf8"));
pkg.engines = { npm: ">=11.10.0" };
fs.writeFileSync("backend/package.json", JSON.stringify(pkg, null, 2) + "\n");
'

# Add engines to frontend/package.json
node -e '
const fs = require("fs");
const pkg = JSON.parse(fs.readFileSync("frontend/package.json", "utf8"));
pkg.engines = { npm: ">=11.10.0" };
fs.writeFileSync("frontend/package.json", JSON.stringify(pkg, null, 2) + "\n");
'

# Add Dependency Policy to CLAUDE.md before "## Cross-Cutting Patterns"
sed -i '/^## Cross-Cutting Patterns$/i \
### Dependency Policy\
\
Both `backend/` and `frontend/` enforce a minimum release age of 7 days for npm packages (configured via `.npmrc` in each directory). This means `npm install` will only resolve package versions published at least 7 days ago, as a supply-chain security measure.\
' CLAUDE.md

echo "Patch applied successfully."
