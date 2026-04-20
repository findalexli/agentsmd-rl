FROM python:3.12-slim

# Install Node.js, pnpm, and git
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    git \
    ca-certificates \
    && curl -fsSL https://deb.nodesource.com/setup_22.x | bash - \
    && apt-get install -y nodejs \
    && npm install -g pnpm@9.12.2 \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Clone the repo at base commit
WORKDIR /workspace
RUN git clone --filter=blob:none https://github.com/trpc/trpc.git
WORKDIR /workspace/trpc
RUN git checkout 5b0a4378f4bc5613ffc499c4781c549570799fbd

# Install dependencies
RUN pnpm install --frozen-lockfile

# Build the server package (needed for tests)
RUN pnpm build --filter=@trpc/server

# Create logs directory
RUN mkdir -p /logs/verifier

WORKDIR /workspace/trpc