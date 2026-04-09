FROM node:22-slim

# Install python3 for pytest runner
RUN apt-get update && apt-get install -y python3 python3-pip git && rm -rf /var/lib/apt/lists/*

# Install pnpm
RUN npm install -g pnpm@9

# Create logs directory
RUN mkdir -p /logs/verifier

WORKDIR /workspace

# Clone the repo at base commit
RUN git clone --filter=blob:none https://github.com/TanStack/router.git && \
    cd router && \
    git checkout a0a6aa8b8ad801f0a364b6c27722d5a929c14e70

# Install dependencies
WORKDIR /workspace/router
RUN pnpm install

# Build only the router-core package (the one we're testing)
RUN pnpm nx run @tanstack/router-core:build

WORKDIR /workspace
