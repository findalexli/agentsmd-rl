FROM node:23.7.0-bookworm-slim

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && apt-get install -y --no-install-recommends \
      git=1:2.39.5-0+deb12u2 \
      ca-certificates \
      curl \
      unzip \
      python3 \
      python3-pip \
    && rm -rf /var/lib/apt/lists/*

# Bun (pinned, downloaded from a specific GitHub release — no curl|bash of moving target)
RUN curl -fsSL -o /tmp/bun.zip https://github.com/oven-sh/bun/releases/download/bun-v1.2.21/bun-linux-x64.zip \
    && unzip /tmp/bun.zip -d /tmp/ \
    && mv /tmp/bun-linux-x64/bun /usr/local/bin/bun \
    && chmod +x /usr/local/bin/bun \
    && rm -rf /tmp/bun.zip /tmp/bun-linux-x64 \
    && bun --version

# pnpm (pinned to the same version the repo uses in package.json)
RUN curl -fsSL -o /usr/local/bin/pnpm https://github.com/pnpm/pnpm/releases/download/v10.17.1/pnpm-linux-x64 \
    && chmod +x /usr/local/bin/pnpm \
    && pnpm --version

# Pinned Python tools used by tests
RUN pip3 install --no-cache-dir --break-system-packages \
      pytest==8.3.4 \
      pytest-json-report==1.5.0

WORKDIR /workspace

# Clone the repo at the parent of the merge commit so the bug is present
RUN git init /workspace/effect && \
    cd /workspace/effect && \
    git remote add origin https://github.com/effect-ts/effect.git && \
    git fetch --depth=1 origin 8e2286271a982b1cc34c78fca8b9f59de71fc790 && \
    git checkout FETCH_HEAD

WORKDIR /workspace/effect

# Workspace install (all packages, lockfile-frozen for determinism)
RUN pnpm install --frozen-lockfile --prefer-offline 2>&1 | tail -40

# Pre-create the verifier log directory the harness expects
RUN mkdir -p /logs/verifier

# Default working directory for agent edits
WORKDIR /workspace/effect
