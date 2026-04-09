#!/bin/bash
set -e

cd /workspace/router

# Apply the fix using Python to modify the script
python3 << 'EOF'
import re

with open('scripts/create-github-release.mjs', 'r') as f:
    content = f.read()

# 1. Add 'breaking' to typeOrder (before 'feat') - use regex to handle varying indentation
content = re.sub(r"(const typeOrder = \[\n\s*)'feat',", r"\1'breaking',\n  'feat',", content)

# 2. Add 'breaking' to typeLabels
content = content.replace(
    "const typeLabels = {\n  feat:",
    "const typeLabels = {\n  breaking: '⚠️ Breaking Changes',\n  feat:")

# 3. Update comment
content = content.replace(
    '// Parse conventional commit: type(scope): message',
    '// Parse conventional commit: type(scope)!: message')

# 4. Update regex to capture ! marker
content = content.replace(
    r"const conventionalMatch = subject.match(/^(\w+)(?:\(([^)]*)\))?:\s*(.*)$/)",
    r"const conventionalMatch = subject.match(/^(\w+)(?:\(([^)]*)\))?(!)?:\s*(.*)$/)")

# 5. Update isBreaking to extract from conventionalMatch[3]
content = content.replace(
    'const isBreaking = false',
    'const isBreaking = conventionalMatch ? !!conventionalMatch[3] : false')

# 6. Update message index from 3 to 4
content = content.replace(
    'conventionalMatch ? conventionalMatch[3] : subject',
    'conventionalMatch ? conventionalMatch[4] : subject')

# 7. Update bucket assignment
content = content.replace(
    'const bucket = type',
    "const bucket = isBreaking ? 'breaking' : type")

# 8. Update groups[type] to groups[bucket]
content = content.replace(
    'if (!groups[type]) groups[type] = []',
    "if (!groups[bucket]) groups[bucket] = []")
content = content.replace(
    'groups[type].push({ hash, email, scope, message, prNumber })',
    'groups[bucket].push({ hash, email, scope, message, prNumber })')

with open('scripts/create-github-release.mjs', 'w') as f:
    f.write(content)

print("Fix applied successfully")
EOF

# Idempotency check - verify the distinctive line exists
grep -q "const conventionalMatch = subject.match" scripts/create-github-release.mjs
echo "Patch applied successfully"
