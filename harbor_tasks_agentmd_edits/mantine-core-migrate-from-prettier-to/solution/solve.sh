#!/usr/bin/env bash
set -euo pipefail

cd /workspace/mantine

# Idempotent: skip if already applied
if [ -f .oxfmtrc.json ]; then
    echo "Patch already applied."
    exit 0
fi

# --- 1. Create new config files ---

cat > .oxfmtrc.json << 'OXFMT'
{
  "printWidth": 100,
  "singleQuote": true,
  "trailingComma": "es5",
  "importOrder": [
    ".*styles.css$",
    "",
    "dayjs",
    "^react$",
    "^next$",
    "^next/.*$",
    "<BUILTIN_MODULES>",
    "<THIRD_PARTY_MODULES>",
    "^@mantine/(.*)$",
    "^@mantinex/(.*)$",
    "^@mantine-tests/(.*)$",
    "^@docs/(.*)$",
    "^@/.*$",
    "^../(?!.*\\.css$).*$",
    "^./(?!.*\\.css$).*$",
    "\\.module\\.css$",
    "(?<!\\.module)\\.css$"
  ],
  "sortPackageJson": false,
  "ignorePatterns": [
    "*.d.ts",
    "*.mdx",
    "*.md",
    "packages/*/*/styles.css",
    "packages/*/*/styles.layer.css",
    "packages/*/*/styles/*.css",
    "docs/.next",
    "docs/out"
  ]
}
OXFMT

mkdir -p .vscode
cat > .vscode/settings.json << 'VSCODE'
{
  "editor.defaultFormatter": "oxc.oxc-vscode",
  "editor.formatOnSave": true,
  "[typescript]": {
    "editor.defaultFormatter": "oxc.oxc-vscode"
  },
  "[typescriptreact]": {
    "editor.defaultFormatter": "oxc.oxc-vscode"
  },
  "[css]": {
    "editor.defaultFormatter": "oxc.oxc-vscode"
  }
}
VSCODE

# --- 2. Delete old prettier config ---

rm -f .prettierrc.mjs .prettierignore

# --- 3. Update .gitignore (remove .vscode/ exclusion) ---

sed -i '/^\.vscode\/$/d' .gitignore

# --- 4. Update package.json scripts ---

# Rename prettier:* → format:* scripts with new commands
sed -i 's/"prettier:test": "prettier --check/"format:test": "oxfmt --check/' package.json
sed -i 's/"prettier:write": "prettier --write/"format:write": "oxfmt --write/' package.json
sed -i 's/"prettier:write:files": "prettier --write"/"format:write:files": "oxfmt"/' package.json

# Update test:all to reference format:test
sed -i 's/npm run prettier:test/npm run format:test/' package.json

# Update generate-css-variables to use oxfmt
sed -i 's/prettier --write packages/oxfmt packages/' package.json

# Remove old deps
sed -i '/"@ianvs\/prettier-plugin-sort-imports"/d' package.json
sed -i '/"prettier": "\^3/d' package.json

# Add oxfmt dep (after the "open" line)
sed -i '/"open": "\^11.0.0",/a\    "oxfmt": "^0.42.0",' package.json

# --- 5. Update chmod.sh ---

sed -i 's/node_modules\/.bin\/prettier/node_modules\/.bin\/oxfmt/' scripts/utils/chmod.sh

# --- 6. Update agent config files ---

# CLAUDE.md: prettier:write:files → format:write:files
sed -i 's/npm run prettier:write:files/npm run format:write:files/' CLAUDE.md

# SKILL.md: prettier → oxfmt, prettier:write → format:write
sed -i 's/This runs prettier,/This runs oxfmt,/' .claude/skills/update-dependencies/SKILL.md
sed -i 's/npm run prettier:write$/npm run format:write/' .claude/skills/update-dependencies/SKILL.md

# llms/testing.md: prettier → format in description
sed -i 's/(prettier, syncpack,/(format, syncpack,/' llms/testing.md

echo "Patch applied successfully."
