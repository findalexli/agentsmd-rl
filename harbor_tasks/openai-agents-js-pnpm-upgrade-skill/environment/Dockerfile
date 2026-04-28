FROM python:3.12-slim

RUN apt-get update && apt-get install -y git curl xz-utils --no-install-recommends && rm -rf /var/lib/apt/lists/*

# Install Node.js from official binary tarball (pinned version)
RUN curl -fsSL https://nodejs.org/dist/v22.14.0/node-v22.14.0-linux-x64.tar.xz -o /tmp/node.tar.xz && \
    tar -xJf /tmp/node.tar.xz -C /usr/local --strip-components=1 && \
    rm /tmp/node.tar.xz

# Enable corepack and install pnpm at the version required by the repo
RUN corepack enable && corepack prepare pnpm@10.28.0 --activate

RUN pip install PyYAML==6.0.2 pytest==8.3.4

RUN git clone --filter=blob:none https://github.com/openai/openai-agents-js.git /workspace/openai-agents-js && \
    cd /workspace/openai-agents-js && \
    git checkout 94b4b7c55a6ada0fb0450c95ad6c47e3d6d449f9

WORKDIR /workspace/openai-agents-js

# Pre-install dependencies so CI p2p tests do not need network access
RUN pnpm install --frozen-lockfile

RUN mkdir -p /logs/verifier
