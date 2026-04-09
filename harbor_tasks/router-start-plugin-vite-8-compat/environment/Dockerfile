FROM node:22-slim

# Install pnpm and Python (needed by pytest runner)
RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    git \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/* \
    && npm install -g pnpm@10.28.0 \
    && pip3 install pytest --break-system-packages

# Set working directory
WORKDIR /workspace

# Clone the router repo at base commit
ARG BASE_COMMIT=3bc18d4623459a56ae972de8ff969ebf7a994ca7
RUN git clone --filter=blob:none https://github.com/TanStack/router.git router && \
    cd router && \
    git checkout ${BASE_COMMIT}

# Install dependencies for the start-plugin-core package only
WORKDIR /workspace/router
RUN pnpm install --frozen-lockfile

# Build the start-plugin-core package and its dependencies
WORKDIR /workspace/router
RUN CI=1 NX_DAEMON=false pnpm nx run @tanstack/start-plugin-core:build --outputStyle=stream --skipRemoteCache

# Create logs directory
RUN mkdir -p /logs/verifier

# Default working directory for tests
WORKDIR /workspace/router
