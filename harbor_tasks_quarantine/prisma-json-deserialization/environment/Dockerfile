FROM python:3.12-slim

# Install Node.js 22, pnpm, and git
RUN apt-get update && apt-get install -y curl git \
    && curl -fsSL https://deb.nodesource.com/setup_22.x | bash - \
    && apt-get install -y nodejs \
    && npm install -g pnpm@10 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /workspace

# Clone the repo at base commit (partial clone)
RUN git clone --filter=blob:none --no-checkout https://github.com/prisma/prisma.git prisma_repo
WORKDIR /workspace/prisma_repo
RUN git checkout 6587f54b0ebd862e13ef68e2febcdeefcc432b63

# Install dependencies
RUN pnpm install --frozen-lockfile || pnpm install

# Install tsx globally for running TypeScript tests directly
RUN npm install -g tsx

# Build all required packages for json-protocol tests
RUN pnpm --filter @prisma/client-runtime-utils build
RUN DEV=true pnpm --filter @prisma/debug build || true
RUN DEV=true pnpm --filter @prisma/driver-adapter-utils build || true
RUN DEV=true pnpm --filter @prisma/client-engine-runtime build

RUN mkdir -p /logs/verifier
