FROM node:22-slim

# Install python3, git, and other utilities
RUN apt-get update && apt-get install -y --no-install-recommends \
    python3 python3-pip git curl patch \
    && rm -rf /var/lib/apt/lists/*

# Create workspace
RUN mkdir -p /workspace /logs/verifier

# Clone turborepo at base commit (filter blob:none for efficiency)
WORKDIR /workspace
RUN git clone --filter=blob:none --depth=1 https://github.com/vercel/turborepo.git turborepo
WORKDIR /workspace/turborepo
ARG BASE_COMMIT=a7c6dd92e7be2618c5377bdf6921b4a58e497fb2
RUN git fetch --filter=blob:none origin ${BASE_COMMIT}
RUN git checkout ${BASE_COMMIT}

# Install pnpm globally and install dependencies
RUN npm install -g pnpm
RUN pnpm install --frozen-lockfile

# Build the codemod package
RUN cd packages/turbo-codemod && pnpm build

# Create logs directory
RUN mkdir -p /logs/verifier

WORKDIR /workspace