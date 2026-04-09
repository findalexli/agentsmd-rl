FROM node:22-slim

# Install Python for pytest runner and git for cloning
RUN apt-get update && apt-get install -y python3 python3-pip git && rm -rf /var/lib/apt/lists/*

# Install pytest
RUN pip3 install pytest --break-system-packages

# Set working directory
WORKDIR /workspace

# Clone the repo at main (which has the fix)
# We'll manually revert the script to its broken state
RUN git clone --filter=blob:none https://github.com/TanStack/router.git router && \
    cd router && \
    git checkout main

WORKDIR /workspace/router

# Revert the script to its broken state (pre-PR #6963)
RUN python3 << 'EOF'
import re

with open('scripts/create-github-release.mjs', 'r') as f:
    content = f.read()

# Remove 'breaking' from typeOrder
content = re.sub(r"'breaking',\s*\n", '', content)

# Remove 'breaking' from typeLabels
content = re.sub(r"\s*breaking:\s*'⚠️ Breaking Changes',\s*\n", '\n', content)

# Change comment back
content = content.replace('// Parse conventional commit: type(scope)!: message',
                          '// Parse conventional commit: type(scope): message')

# Revert regex to NOT capture the ! marker - note: \w in source is literal backslash-w
content = content.replace(
    r"const conventionalMatch = subject.match(/^(\w+)(?:\(([^)]*)\))?(!)?:\s*(.*)$/)",
    r"const conventionalMatch = subject.match(/^(\w+)(?:\(([^)]*)\))?:\s*(.*)$/)")

# Hardcode isBreaking to false
content = content.replace(
    'const isBreaking = conventionalMatch ? !!conventionalMatch[3] : false',
    'const isBreaking = false')

# Revert message index from 4 to 3
content = content.replace(
    'conventionalMatch ? conventionalMatch[4] : subject',
    'conventionalMatch ? conventionalMatch[3] : subject')

# Revert bucket assignment
content = content.replace(
    "const bucket = isBreaking ? 'breaking' : type",
    'const bucket = type')

# Revert groups[bucket] to groups[type]
content = content.replace('groups[bucket]', 'groups[type]')

with open('scripts/create-github-release.mjs', 'w') as f:
    f.write(content)

print("Script reverted to broken state")
EOF

# Install pnpm
RUN npm install -g pnpm

# Set up logs directory
RUN mkdir -p /logs/verifier

WORKDIR /workspace/router
