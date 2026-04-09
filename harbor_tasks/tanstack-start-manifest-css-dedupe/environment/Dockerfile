FROM node:22-slim

# Install Python for pytest runner and git for cloning
RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    git \
    && rm -rf /var/lib/apt/lists/*

# Set up workspace
WORKDIR /workspace

# Clone the repo at the base commit (filter=blob:none for speed)
RUN git clone --filter=blob:none https://github.com/TanStack/router.git /workspace/router && \
    cd /workspace/router && \
    git checkout 7640f6e3f5d946ca1fd32729050d12642cf38502

# Install pnpm
RUN npm install -g pnpm

# Create logs directory for verifier
RUN mkdir -p /logs/verifier

# Install dependencies for the specific package and build
WORKDIR /workspace/router
RUN pnpm install --frozen-lockfile

# Build the packages needed for testing
RUN CI=1 NX_DAEMON=false pnpm nx run @tanstack/start-plugin-core:build --outputStyle=stream --skipRemoteCache || true

WORKDIR /workspace
