FROM node:22-slim

# Install git and python3 (needed for pytest runner)
RUN apt-get update && apt-get install -y \
    git \
    python3 \
    python3-pip \
    python3-venv \
    && rm -rf /var/lib/apt/lists/*

# Install pnpm
RUN corepack enable && corepack prepare pnpm@latest --activate

WORKDIR /workspace

# Clone the repository at the base commit
RUN git clone --filter=blob:none https://github.com/TanStack/router.git router \
    && cd router \
    && git checkout 4e465e93b3d0169ed7b2f9d1a7ccb1c5414b7161

WORKDIR /workspace/router

# Create log directory
RUN mkdir -p /logs/verifier

# Note: We don't install all dependencies as that takes too long
# The script we're testing is standalone and only needs Node.js
