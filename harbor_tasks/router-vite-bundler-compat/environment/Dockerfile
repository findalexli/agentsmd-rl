FROM node:22-slim

# Install Python for pytest runner
RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    git \
    && rm -rf /var/lib/apt/lists/*

# Install pnpm
RUN npm install -g pnpm

# Set working directory
WORKDIR /workspace

# Clone the repo at base commit (shallow clone for speed)
ARG BASE_COMMIT=3bc18d4623459a56ae972de8ff969ebf7a994ca7
RUN git clone --depth=100 --filter=blob:none https://github.com/TanStack/router.git router && \
    cd router && \
    git checkout ${BASE_COMMIT}

# Install dependencies
WORKDIR /workspace/router
RUN pnpm install --frozen-lockfile

# Create logs directory for verifier
RUN mkdir -p /logs/verifier

# Set back to workspace for tests
WORKDIR /workspace/router
