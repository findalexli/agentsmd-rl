# Dockerfile for ant-design typography ellipsis task
FROM node:22-slim

# Install Python (needed by pytest runner), git, and patch
RUN apt-get update && apt-get install -y --no-install-recommends \
    python3 \
    python3-pip \
    python3-venv \
    git \
    ca-certificates \
    patch \
    && rm -rf /var/lib/apt/lists/*

# Create python alias
RUN ln -sf /usr/bin/python3 /usr/bin/python

WORKDIR /workspace

# Clone the repository with filter to reduce size
RUN git clone --filter=blob:none https://github.com/ant-design/ant-design.git antd

WORKDIR /workspace/antd

# Checkout base commit (before the fix)
RUN git checkout 770c522e044586e64a31d6daf95d8c8fba08fa4a

# Install dependencies
RUN npm install --legacy-peer-deps

# Create logs directory for verifier
RUN mkdir -p /logs/verifier

# Set working directory
WORKDIR /workspace/antd
