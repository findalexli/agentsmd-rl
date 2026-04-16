FROM node:22-slim

# Install Python for pytest runner and git for cloning
RUN apt-get update && apt-get install -y --no-install-recommends \
    python3 \
    python3-pip \
    git \
    && rm -rf /var/lib/apt/lists/*

# Install pytest
RUN pip3 install pytest --break-system-packages

# Set working directory
WORKDIR /workspace

# Clone mantine repo at base commit (shallow clone with depth 1)
# Note: Mantine is a monorepo with workspaces, need proper clone for npm to work
ARG BASE_COMMIT=5f19669395218658b58c53e228b239530ab09a50
RUN git clone --depth 1 https://github.com/mantinedev/mantine.git mantine \
    && cd mantine \
    && git fetch --depth=1 origin ${BASE_COMMIT} \
    && git checkout ${BASE_COMMIT}

# Install dependencies using yarn (monorepo with workspaces)
WORKDIR /workspace/mantine
RUN yarn install --frozen-lockfile

# Create logs directory for verifier
RUN mkdir -p /logs/verifier

# Set working directory back to repo root
WORKDIR /workspace/mantine
