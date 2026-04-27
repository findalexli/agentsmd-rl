FROM node:22.13.1-slim

# python3 is required by the pytest-based test harness
RUN apt-get update && apt-get install -y --no-install-recommends \
        git \
        ca-certificates \
        python3 \
        python3-pip \
        python3-venv \
    && rm -rf /var/lib/apt/lists/*

# Pinned pytest stack (used by /tests/test.sh)
RUN python3 -m pip install --break-system-packages --no-cache-dir \
        pytest==8.3.4 \
        pytest-json-ctrf==0.4.1

WORKDIR /workspace

# Shallow clone of the upstream repo at the BASE commit (parent of the PR's merge)
ARG REPO_URL=https://github.com/tuist/tuist.git
ARG BASE_COMMIT=098406e621dd30872f0db68889983ccc25cd523e
RUN git clone --filter=blob:none --no-checkout "$REPO_URL" tuist \
    && cd tuist \
    && git fetch --depth=1 origin "$BASE_COMMIT" \
    && git checkout "$BASE_COMMIT"

# Install registry-router devDeps (typescript, @cloudflare/workers-types)
WORKDIR /workspace/tuist/infra/registry-router
RUN npm ci --no-audit --no-fund

# Test helper scripts (used by /tests/test_outputs.py via subprocess)
COPY extract_origins.cjs /opt/test-helpers/extract_origins.cjs

# Standard verifier output dir
RUN mkdir -p /logs/verifier

WORKDIR /workspace/tuist
