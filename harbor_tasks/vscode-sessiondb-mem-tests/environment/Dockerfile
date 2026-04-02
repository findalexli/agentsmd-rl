FROM node:22-slim

RUN apt-get update && apt-get install -y \
    git \
    curl \
    ca-certificates \
    build-essential \
    python3 \
    python3-pip \
    pkg-config \
    libsqlite3-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /workspace

# Clone VS Code at base commit (pre-fix)
RUN git init vscode && \
    cd vscode && \
    git remote add origin https://github.com/microsoft/vscode && \
    git -c protocol.version=2 fetch --depth=1 origin c1f3775929102459145d7a93175005e7e90b216e && \
    git checkout FETCH_HEAD

# Install npm dependencies for core modules (sqlite3 needs native build)
WORKDIR /workspace/vscode
RUN npm ci --ignore-scripts 2>/dev/null || npm install --ignore-scripts 2>/dev/null || true

# Build @vscode/sqlite3 native module specifically
WORKDIR /workspace/vscode/node_modules/@vscode/sqlite3
RUN npm run rebuild 2>/dev/null || npx node-gyp rebuild 2>/dev/null || true

WORKDIR /workspace/vscode
RUN npm run gulp vscode-sqlite3 2>/dev/null || true

# Sanitize - create snapshot without .git
RUN rm -rf .git && \
    git init && \
    git add -A && \
    git config user.email "agent@test.com" && \
    git config user.name "Agent" && \
    git commit -m "snapshot"

# Prepare test environment
ENV NODE_OPTIONS="--loader ts-node/esm"
ENV VSCODE_DEV=1

RUN mkdir -p /logs/verifier
WORKDIR /workspace/vscode
