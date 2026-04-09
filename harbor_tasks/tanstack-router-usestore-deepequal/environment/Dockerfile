FROM node:22-slim

# Install Python for pytest runner
RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    git \
    && rm -rf /var/lib/apt/lists/*

# Install pytest
RUN pip3 install pytest --break-system-packages

# Set working directory
WORKDIR /workspace

# Clone the repo at the base commit
ARG BASE_COMMIT=d5622bb413a2d1ac99c546c5336be949dfb351d9
RUN git clone --filter=blob:none https://github.com/TanStack/router.git /workspace/router && \
    cd /workspace/router && \
    git checkout ${BASE_COMMIT}

# Install dependencies and build
WORKDIR /workspace/router
RUN npm install -g pnpm
RUN pnpm install
RUN pnpm build:all

# Create log directory
RUN mkdir -p /logs/verifier

# Set working directory for tests
WORKDIR /workspace
