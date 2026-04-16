FROM node:22-slim

# Install Python for pytest runner
RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    python3-pytest \
    git \
    && rm -rf /var/lib/apt/lists/*

# Install pnpm
RUN corepack enable && corepack prepare pnpm@latest --activate

WORKDIR /workspace

# Clone with blob filter for efficiency
RUN git clone --filter=blob:none https://github.com/TanStack/router.git router

WORKDIR /workspace/router

# Checkout base commit (parent of merge)
RUN git checkout 80c3196246952c437c4ed8cf892b293800e24f3b

# Install dependencies
RUN pnpm install --frozen-lockfile

# Build the packages we need for testing
RUN pnpm nx run @tanstack/router-plugin:build

# Create logs directory
RUN mkdir -p /logs/verifier
