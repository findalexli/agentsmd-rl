FROM node:22-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

# Install python3 for pytest runner + system deps for playwright/chromium
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        git curl ca-certificates python3 python3-pip python3-venv \
        libnss3 libnspr4 libdbus-1-3 libatk1.0-0 libatk-bridge2.0-0 \
        libcups2 libdrm2 libxkbcommon0 libxcomposite1 libxdamage1 \
        libxrandr2 libgbm1 libpango-1.0-0 libcairo2 libasound2 \
        libxshmfence1 && \
    rm -rf /var/lib/apt/lists/*

# Install pnpm
RUN corepack enable && corepack prepare pnpm@latest --activate

WORKDIR /workspace

# Clone repo at base commit (shallow for speed)
RUN git clone --depth=100 https://github.com/remix-run/remix.git remix && \
    cd remix && \
    git checkout 649aecadeb54fc3027a2b6a85020dd31421b5327 && \
    git config user.email "agent@test" && \
    git config user.name "Agent"

WORKDIR /workspace/remix

# Install monorepo dependencies
RUN pnpm install --frozen-lockfile 2>/dev/null || pnpm install

# Install playwright chromium for vitest browser mode
RUN npx playwright install chromium 2>&1 || true

# Verifier output directory (Harbor bind-mounts this)
RUN mkdir -p /logs/verifier
