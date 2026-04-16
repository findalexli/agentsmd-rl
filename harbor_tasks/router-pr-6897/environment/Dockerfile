FROM node:22-slim

# Install git and python for test runner
RUN apt-get update && apt-get install -y \
    git \
    python3 \
    python3-pip \
    && rm -rf /var/lib/apt/lists/*

# Install pnpm
RUN corepack enable && corepack prepare pnpm@latest --activate

WORKDIR /workspace

# Clone the repository with shallow clone for efficiency
RUN git clone --filter=blob:none https://github.com/TanStack/router.git router

WORKDIR /workspace/router

# Checkout the base commit (parent of merge commit)
RUN git checkout 3a2d74227f878ffd904b980c47341b4a901125f3

# Install dependencies
RUN pnpm install --frozen-lockfile

# Create logs directory for verifier
RUN mkdir -p /logs/verifier

WORKDIR /workspace/router
