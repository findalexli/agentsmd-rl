FROM node:22-slim

# Install base dependencies
RUN apt-get update && apt-get install -y \
    git curl ca-certificates build-essential python3 \
    && rm -rf /var/lib/apt/lists/*

# Set up workspace
WORKDIR /workspace

# Clone at the pre-fix base commit (0930f054ee7006081f7eecdd11c3a55fa940e604)
# This is a snapshot - no git history
RUN git clone --depth=1 --single-branch \
    https://github.com/microsoft/vscode.git vscode && \
    cd vscode && \
    git fetch --depth=1 origin 0930f054ee7006081f7eecdd11c3a55fa940e604 && \
    git checkout 0930f054ee7006081f7eecdd11c3a55fa940e604

WORKDIR /workspace/vscode

# Sanitize: remove .git, re-init to snapshot
RUN rm -rf .git && \
    git init && \
    git config user.email "agent@example.com" && \
    git config user.name "Agent" && \
    git add -A && \
    git commit -m "snapshot at 0930f054ee7006081f7eecdd11c3a55fa940e604"

# Install dependencies (needed to run build and tests)
# Use --legacy-peer-deps to handle any peer dependency issues
RUN npm ci --legacy-peer-deps || npm install --legacy-peer-deps

# Compile TypeScript - we need the compiled JS for the agentHost server
# This will compile the TypeScript files to out/
RUN npm run compile 2>&1 || true

# Ensure test output directories exist
RUN mkdir -p /logs/verifier

# Set environment variables for the test harness
ENV NODE_ENV=test
ENV VSCODE_AGENT_HOST_PORT=8081
