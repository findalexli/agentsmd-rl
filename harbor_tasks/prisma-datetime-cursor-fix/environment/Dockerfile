FROM node:22-slim

RUN apt-get update && apt-get install -y \
    git \
    python3 \
    python3-pip \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Install pnpm (repo requires >=10.15 <11)
RUN npm install -g pnpm@10.15

WORKDIR /workspace

# Clone the prisma monorepo at the base commit (filter=blob:none for speed)
RUN git clone --filter=blob:none https://github.com/prisma/prisma.git

WORKDIR /workspace/prisma

RUN git checkout f8e742a8de6878a206d8493b61d911dac97e11df

# Install all workspace dependencies (creates symlinks, no build yet)
RUN pnpm install --frozen-lockfile

# Build workspace packages that client-engine-runtime depends on, in topological order.
# These are needed so vitest can resolve @prisma/* imports when running tests.
RUN pnpm --filter @prisma/debug build
RUN pnpm --filter @prisma/driver-adapter-utils build
RUN pnpm --filter @prisma/client-runtime-utils build
# Note: @prisma/sqlcommenter is not in the render-query.ts import chain, so we skip it.
# Its build fails at the base commit due to a tsc type-checking issue unrelated to this task.

RUN mkdir -p /logs/verifier
