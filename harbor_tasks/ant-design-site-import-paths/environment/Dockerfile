FROM node:22-slim

# Install Python and required tools for pytest
RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    python3-venv \
    git \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /workspace

# Set Node.js memory limit for TypeScript compilation
ENV NODE_OPTIONS="--max-old-space-size=4096"

# Clone the ant-design repository at the base commit
RUN git clone --filter=blob:none https://github.com/ant-design/ant-design.git ant-design && \
    cd ant-design && \
    git checkout 310f780636ba07ab85d9997e2a54a569f56e00b4

# Install dependencies
WORKDIR /workspace/ant-design
RUN npm install

# Create logs directory for verifier
RUN mkdir -p /logs/verifier

# Set back to workspace root
WORKDIR /workspace
