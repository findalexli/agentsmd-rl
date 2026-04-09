FROM node:22-slim

# Install git and python3 (for pytest runner)
RUN apt-get update && apt-get install -y git python3 python3-pip python3-venv && rm -rf /var/lib/apt/lists/*

# Set up workspace
WORKDIR /workspace

# Clone the router repo at base commit (shallow clone for speed)
ARG BASE_COMMIT=d5622bb413a2d1ac99c546c5336be949dfb351d9
RUN git clone --filter=blob:none https://github.com/TanStack/router.git && \
    cd router && \
    git checkout ${BASE_COMMIT}

# Install pnpm globally
RUN npm install -g pnpm

# Install dependencies and build the necessary packages
WORKDIR /workspace/router
RUN pnpm install --frozen-lockfile

# Build the packages needed for testing
RUN pnpm build

# Create logs directory
RUN mkdir -p /logs/verifier

# Set working directory for the task
WORKDIR /workspace/router
