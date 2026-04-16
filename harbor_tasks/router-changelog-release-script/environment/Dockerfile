FROM node:22-slim

# Install Python for pytest runner
RUN apt-get update && apt-get install -y --no-install-recommends \
    python3 \
    python3-pip \
    git \
    && rm -rf /var/lib/apt/lists/*

# Install pytest
RUN pip3 install pytest --break-system-packages

# Set working directory
WORKDIR /workspace

# Clone the repository at the base commit (shallow clone for efficiency)
ARG BASE_COMMIT=3a2d74227f878ffd904b980c47341b4a901125f3
RUN git clone --filter=blob:none --depth=100 https://github.com/TanStack/router.git router && \
    cd router && \
    git checkout ${BASE_COMMIT}

# Install pnpm globally
RUN npm install -g pnpm

# Install dependencies in the repo
WORKDIR /workspace/router
RUN pnpm install --frozen-lockfile || pnpm install

# Create logs directory for verifier
RUN mkdir -p /logs/verifier

WORKDIR /workspace/router
