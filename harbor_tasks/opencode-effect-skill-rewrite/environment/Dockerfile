FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
RUN apt-get update && apt-get install -y --no-install-recommends \
    git \
    ca-certificates \
    curl \
    unzip \
    && rm -rf /var/lib/apt/lists/*

# Install bun v1.3.13 (pinned to repo's packageManager version)
RUN curl -fsSL -o /tmp/bun.zip \
    "https://github.com/oven-sh/bun/releases/download/bun-v1.3.13/bun-linux-x64-baseline.zip" \
    && unzip -q /tmp/bun.zip -d /usr/local \
    && rm /tmp/bun.zip \
    && ln -s /usr/local/bun-linux-x64-baseline/bun /usr/local/bin/bun

RUN pip install --no-cache-dir \
    pytest==8.3.4 \
    pytest-json-ctrf==0.4.1

WORKDIR /workspace

RUN git clone --filter=blob:none https://github.com/anomalyco/opencode.git /workspace/opencode \
    && cd /workspace/opencode \
    && git checkout 58c65874ba6aff2f16f5310dacddc3a89eb7b2cd

# Install JS dependencies for CI tests
# --ignore-scripts skips native module compilation (tree-sitter, etc.)
# which is not needed for typecheck — TypeScript only needs .d.ts files
WORKDIR /workspace/opencode
RUN bun install --ignore-scripts

RUN mkdir -p /logs/verifier

WORKDIR /workspace/opencode
