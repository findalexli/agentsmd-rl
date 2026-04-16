FROM node:22-slim

RUN apt-get update && apt-get install -y --no-install-recommends \
    ca-certificates \
    git \
    python3 \
    python3-pip \
    && rm -rf /var/lib/apt/lists/*

RUN pip3 install --no-cache-dir --break-system-packages pytest pytest-timeout

RUN npm install -g pnpm@9

WORKDIR /workspace

# Clone with enough history for both base and merge commits
RUN git clone --filter=blob:none --depth=100 https://github.com/electric-sql/electric.git electric

WORKDIR /workspace/electric
# Checkout base commit for NOP tests
RUN git checkout deb2a61614678fac029773a56b618382fe5b70f2

RUN pnpm install --ignore-scripts

WORKDIR /workspace/electric/packages/typescript-client
RUN pnpm install --ignore-scripts

# Build the client so imports work
RUN pnpm run build || true

RUN mkdir -p /logs/verifier

ENV NODE_ENV=test