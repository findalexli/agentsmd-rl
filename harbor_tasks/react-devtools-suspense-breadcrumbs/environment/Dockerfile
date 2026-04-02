FROM node:22-slim

RUN apt-get update && apt-get install -y \
    git \
    curl \
    ca-certificates \
    build-essential \
    python3 \
    python3-pip \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /workspace

# Clone React repo at the base commit (pre-fix)
# Commit 95ffd6cd9c794842e5c8ab36150296afab1ae70c is the parent of the merge commit
RUN git clone --depth=1 https://github.com/facebook/react.git && \
    cd react && \
    git fetch --depth=1 origin 95ffd6cd9c794842e5c8ab36150296afab1ae70c && \
    git checkout 95ffd6cd9c794842e5c8ab36150296afab1ae70c

# Sanitize snapshot - remove .git history to prevent cheating, re-init
RUN cd react && \
    rm -rf .git && \
    git init && \
    git add -A && \
    git config user.email "agent@example.com" && \
    git config user.name "Agent" && \
    git commit -m "snapshot"

# Install minimal dependencies for the DevTools package
WORKDIR /workspace/react/packages/react-devtools-shared
RUN npm install --legacy-peer-deps 2>/dev/null || yarn install --frozen-lockfile 2>/dev/null || true

WORKDIR /workspace/react

# Create logs directory
RUN mkdir -p /logs/verifier

ENV NODE_ENV=test
ENV CI=true
