FROM node:22-slim

# Install git and Python (needed by test runner)
RUN apt-get update && apt-get install -y git python3 python3-pip && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /workspace

# Clone the repo at base commit with shallow clone for speed
ARG BASE_COMMIT=e8c88f416fe0be8f9fc9e92c2f2adab82fb023d4
RUN git clone --depth 100 https://github.com/continuedev/continue.git && \
    cd continue && \
    git fetch --depth=1 origin ${BASE_COMMIT} && \
    git checkout ${BASE_COMMIT}

# Install root dependencies (package.json at root)
WORKDIR /workspace/continue
RUN yarn install --frozen-lockfile --network-timeout 100000 || yarn install --network-timeout 100000 \
    && yarn cache clean

# Install GUI dependencies
WORKDIR /workspace/continue/gui
RUN yarn install --frozen-lockfile --network-timeout 100000 || yarn install --network-timeout 100000 \
    && yarn cache clean

# Create logs directory
RUN mkdir -p /logs/verifier

WORKDIR /workspace/continue
