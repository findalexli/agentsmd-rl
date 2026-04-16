FROM node:22-slim

RUN apt-get update && apt-get install -y --no-install-recommends \
    python3 \
    python3-pip \
    git \
    ca-certificates \
    curl \
    && rm -rf /var/lib/apt/lists/*

RUN pip3 install --no-cache-dir pytest --break-system-packages

RUN npm install -g pnpm

WORKDIR /workspace

# Clone the repo at the base commit
RUN git clone --filter=blob:none --depth=1 https://github.com/withastro/astro.git
WORKDIR /workspace/astro
RUN git fetch --filter=blob:none https://github.com/withastro/astro 335a204161f5a7293c128db570901d4f8639c6ed
RUN git checkout 335a204161f5a7293c128db570901d4f8639c6ed

# Install dependencies (skip frozen lockfile since we might be at an older commit)
RUN pnpm install

# Build the monorepo packages (needed for tests that import compiled code)
RUN pnpm run build

RUN mkdir -p /logs/verifier
