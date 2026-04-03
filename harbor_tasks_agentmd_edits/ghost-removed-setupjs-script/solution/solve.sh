#!/usr/bin/env bash
set -euo pipefail

cd /workspace/Ghost

# Idempotent: skip if already applied
if ! [ -f .github/scripts/setup.js ]; then
    echo "Patch already applied."
    exit 0
fi

# Delete the setup.js script
rm -f .github/scripts/setup.js

# Update package.json: simplify setup script
python3 -c "
import json, pathlib
p = pathlib.Path('package.json')
data = json.loads(p.read_text())
data['scripts']['setup'] = 'yarn && git submodule update --init --recursive'
p.write_text(json.dumps(data, indent=2) + '\n')
"

# Update docs/README.md
cat > /tmp/docs_readme_patch.py << 'PYEOF'
import pathlib

p = pathlib.Path("docs/README.md")
content = p.read_text()

# Fix section 2: Install and Setup
content = content.replace(
    """```bash
# Run initial setup
# This installs dependencies, initializes the database,
# sets up git hooks, and initializes submodules
yarn setup
```""",
    """```bash
# Install dependencies and initialize submodules
yarn setup
```"""
)

# Fix section 3: Start Ghost
content = content.replace(
    "# Start development server (uses Docker for backend services)",
    "# Start development (runs Docker backend services + frontend dev servers)"
)

# Fix troubleshooting section
content = content.replace(
    """# Reset and reinitialize database
yarn knex-migrator reset
yarn knex-migrator init""",
    """# Reset running dev data
yarn reset:data"""
)

p.write_text(content)
PYEOF

python3 /tmp/docs_readme_patch.py

echo "Patch applied successfully."
