FROM node:22.12.0-slim

# Install required tools
RUN apt-get update && apt-get install -y --no-install-recommends \
        git \
        ca-certificates \
        python3 \
        python3-pip \
        python3-venv \
    && rm -rf /var/lib/apt/lists/*

# Pytest harness
RUN pip3 install --no-cache-dir --break-system-packages \
        pytest==8.3.4 \
        pytest-json-report==1.5.0

# Clone OpenHands at base commit (parent of merge commit for PR #14049)
WORKDIR /workspace
RUN git init /workspace/OpenHands && \
    cd /workspace/OpenHands && \
    git remote add origin https://github.com/All-Hands-AI/OpenHands.git && \
    git fetch --depth=1 origin f7dce9c6c0929a2e74e15499f723d376e1e98238 && \
    git checkout FETCH_HEAD && \
    git config user.email "task@example.com" && \
    git config user.name "Task Runner"

# Install npm dependencies (this is the heavy step)
WORKDIR /workspace/OpenHands/frontend
RUN npm install --no-audit --no-fund --legacy-peer-deps

# Pre-bake the binary notification.mp3 asset (agent's task is source code, not binary)
RUN mkdir -p src/assets
COPY notification.mp3 src/assets/notification.mp3

# Generate i18n declarations once so vitest does not need network during tests
RUN npm run make-i18n || true

WORKDIR /workspace/OpenHands

# Logs / verifier output
RUN mkdir -p /logs/verifier
