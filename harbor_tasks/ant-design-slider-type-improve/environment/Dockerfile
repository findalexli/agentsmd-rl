FROM node:22-slim

# Install Python and git for the test runner
RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    git \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /workspace

# Clone the repository at base commit
ARG BASE_COMMIT
RUN git clone --depth=1 --filter=blob:none https://github.com/ant-design/ant-design.git ant-design && \
    cd ant-design && \
    git checkout ${BASE_COMMIT}

# Install dependencies
WORKDIR /workspace/ant-design
RUN npm install --legacy-peer-deps

# Create log directory for verifier
RUN mkdir -p /logs/verifier

# Return to workspace root
WORKDIR /workspace
