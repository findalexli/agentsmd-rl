#!/usr/bin/env bash
set -euo pipefail

cd /workspace/angular

# Idempotent: skip if already applied
if [ -L .agent/rules/agents.md ] 2>/dev/null; then
    echo "Patch already applied."
    exit 0
fi

# 1. Create .agent/rules/agents.md symlink to ../../AGENTS.md
mkdir -p .agent/rules
ln -s ../../AGENTS.md .agent/rules/agents.md

# 2. Add .agent/rules/agents.md to .prettierignore
python3 -c "
content = open('.prettierignore').read()
content = content.replace(
    '\nCHANGELOG.md',
    '\n# Antigravity rules\n.agent/rules/agents.md\n\nCHANGELOG.md'
)
if not content.endswith('\n'):
    content += '\n'
open('.prettierignore', 'w').write(content)
"

# 3. Add .agent/**/{*,.*} to .pullapprove.yml
python3 -c "
content = open('.pullapprove.yml').read()
content = content.replace(
    \"          '{*,.*}',\n\",
    \"          '{*,.*}',\n          '.agent/**/{*,.*}',\n\"
)
open('.pullapprove.yml', 'w').write(content)
"

# 4. Update AGENTS.md: add frontmatter, simplify text
python3 -c "
content = open('AGENTS.md').read()
# Add YAML frontmatter
content = '---\ntrigger: always_on\n---\n\n' + content
# Simplify test command line
content = content.replace(
    'to run tests. Do not use \`ng test\`, or just \`bazel\`',
    'to run tests.'
)
# Remove browser tools line
lines = content.split('\n')
lines = [l for l in lines if 'Avoid using browser tools' not in l]
content = '\n'.join(lines)
open('AGENTS.md', 'w').write(content)
"

echo "Patch applied successfully."
