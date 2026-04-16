FROM node:22-slim

# Install Python for pytest and other utilities
RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    git \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install pytest
RUN pip3 install pytest pyyaml --break-system-packages

# Set working directory
WORKDIR /workspace

# Clone the repository at the base commit
# Using --filter=blob:none to minimize download size
RUN git clone --filter=blob:none https://github.com/TanStack/router.git router && \
    cd router && \
    git checkout 3a32ad6cfbc9dce7a31842e31184955400144dec

WORKDIR /workspace/router

# Install dependencies (needed for any lint/type checks)
RUN npm install -g pnpm && \
    pnpm install --frozen-lockfile || pnpm install

# Create log directory for verifier
RUN mkdir -p /logs/verifier
