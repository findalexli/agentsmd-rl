FROM node:22-slim

RUN apt-get update && apt-get install -y --no-install-recommends \
    git curl ca-certificates python3 python3-pytest \
    && rm -rf /var/lib/apt/lists/*

RUN git config --global http.sslVerify false || true

RUN corepack enable && corepack prepare pnpm@9 --activate

WORKDIR /workspace/router

# Clone the repo with depth=1 then fetch the specific commit
RUN git clone --filter=blob:none --depth=100 https://github.com/TanStack/router.git /workspace/router && \
    git fetch --depth=1 origin a556afa0f07c551cc0edaf17fa7d0de7014a1c68 && \
    git checkout a556afa0f07c551cc0edaf17fa7d0de7014a1c68

RUN pnpm install --frozen-lockfile 2>&1 | tail -10

# Build dependency packages first
RUN pnpm --filter @tanstack/history run build 2>&1 | tail -5
RUN pnpm --filter @tanstack/store run build 2>&1 | tail -5

# Build router-core
RUN pnpm --filter @tanstack/router-core run build 2>&1 | tail -10

RUN mkdir -p /logs/verifier && chmod 777 /logs/verifier

ENV CI=1 NX_DAEMON=false