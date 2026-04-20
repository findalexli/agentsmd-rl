FROM node:22-slim

# Install Python3 and pip for pytest runner
RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    python3-pytest \
    git \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /workspace

# Clone the ant-design repository at base commit
RUN git clone --filter=blob:none https://github.com/ant-design/ant-design.git ant-design && \
    cd ant-design && \
    git checkout 9702dbb57d3cb8ce4346b96c895e6fd6f43e56d3

WORKDIR /workspace/ant-design

# Install dependencies (use npm install since package-lock.json may not exist)
RUN npm install --legacy-peer-deps

# Generate version file needed by tests
RUN npm run version

# Create logs directory for verifier
RUN mkdir -p /logs/verifier
