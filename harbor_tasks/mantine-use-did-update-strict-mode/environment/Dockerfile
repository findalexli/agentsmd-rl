FROM node:22-slim

# Install Python 3 and pip for pytest
RUN apt-get update && apt-get install -y --no-install-recommends \
    python3 \
    python3-pip \
    git \
    && rm -rf /var/lib/apt/lists/*

# Install pytest
RUN pip3 install pytest --break-system-packages

# Set working directory
WORKDIR /workspace

# Clone the mantine repository at base commit
ARG BASE_COMMIT=1fe6e29d77f6a9dd36cf6e5a59e60ecda7f36892
RUN git clone --filter=blob:none https://github.com/mantinedev/mantine.git mantine && \
    cd mantine && \
    git checkout ${BASE_COMMIT}

# Install dependencies for the hooks package and testing
WORKDIR /workspace/mantine

# Install yarn dependencies (this repo uses yarn, not pnpm)
# Use --frozen-lockfile to ensure consistent installs
RUN yarn install --frozen-lockfile 2>&1 || yarn install 2>&1

# Install TypeScript globally for compilation checks
RUN npm install -g typescript

# Create logs directory for verifier
RUN mkdir -p /logs/verifier

# Default workdir is the hooks package
WORKDIR /workspace/mantine/packages/@mantine/hooks
