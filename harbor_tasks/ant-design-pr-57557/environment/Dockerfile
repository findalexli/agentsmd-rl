# Ant Design task environment
FROM node:22-slim

# Install python3 for pytest runner
RUN apt-get update && apt-get install -y --no-install-recommends \
    python3 \
    python3-pip \
    python3-venv \
    git \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/* \
    && python3 -m pip install --break-system-packages pytest

# Clone repository with filter for efficiency
WORKDIR /workspace
RUN git clone --filter=blob:none https://github.com/ant-design/ant-design.git antd

# Checkout base commit
WORKDIR /workspace/antd
RUN git checkout ffe7ccf17f689af990c4757c8197c8727c8f4184

# Install dependencies
RUN npm install --legacy-peer-deps

# Create logs directory
RUN mkdir -p /logs/verifier

WORKDIR /workspace/antd
