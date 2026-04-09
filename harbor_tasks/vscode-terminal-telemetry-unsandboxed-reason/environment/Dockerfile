FROM node:20-slim

RUN apt-get update && apt-get install -y     git     curl     ca-certificates     build-essential     python3     python3-pip     tmux     && rm -rf /var/lib/apt/lists/*

WORKDIR /workspace

# Clone VS Code at base commit (parent of merge commit)
# merge: 0705ebef87428a3a1d38df65b38da286a7b9174c
# base:  a2d7b9e13bdbe52233ea06b2ca6bc69a81083772
RUN git clone --depth 1 https://github.com/microsoft/vscode.git vscode &&     cd vscode &&     git fetch --depth=1 origin a2d7b9e13bdbe52233ea06b2ca6bc69a81083772 &&     git checkout a2d7b9e13bdbe52233ea06b2ca6bc69a81083772

WORKDIR /workspace/vscode

# Sanitize git history (snapshot only, no history to reduce size)
RUN rm -rf .git &&     git init &&     git config user.email "agent@example.com" &&     git config user.name "Agent" &&     git add -A &&     git commit -m "snapshot"

# Install minimal dependencies for type checking (just TypeScript compiler)
RUN npm ci --ignore-scripts --prefer-offline 2>&1 | tail -5 || true

# Warm up TypeScript compilation caches for faster p2p test execution
RUN npx tsc --noEmit --project src/tsconfig.json --skipLibCheck 2>&1 || true

# Set up Python for test runner
RUN mkdir -p /logs/verifier

ENV NODE_OPTIONS="--max-old-space-size=4096"
WORKDIR /workspace/vscode
