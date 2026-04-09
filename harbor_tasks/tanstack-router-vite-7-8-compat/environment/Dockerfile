FROM node:22-slim

# Install Python for pytest runner
RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    git \
    && rm -rf /var/lib/apt/lists/*

# Install pnpm
RUN npm install -g pnpm

# Create logs directory
RUN mkdir -p /logs/verifier

# Clone the repo at base commit
WORKDIR /workspace
RUN git clone --filter=blob:none https://github.com/TanStack/router.git
WORKDIR /workspace/router
RUN git checkout 3bc18d4623459a56ae972de8ff969ebf7a994ca7

# Install dependencies
RUN pnpm install

# Build the affected package
RUN pnpm nx run @tanstack/start-plugin-core:build
