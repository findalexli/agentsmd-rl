FROM node:22-slim

# Install Python for pytest runner and git
RUN apt-get update && apt-get install -y --no-install-recommends \
    python3 \
    python3-pip \
    python3-venv \
    git \
    patch \
    && rm -rf /var/lib/apt/lists/* \
    && pip3 install --break-system-packages pytest

# Clone repository with blob filter for efficiency
WORKDIR /workspace
RUN git clone --filter=blob:none https://github.com/ant-design/ant-design.git antd

# Checkout base commit
WORKDIR /workspace/antd
RUN git checkout 14e3c384e9c7d5b6096ed60ae5de3db80b8a39c9

# Install dependencies
RUN npm install --legacy-peer-deps

# Create logs directory for verifier
RUN mkdir -p /logs/verifier

WORKDIR /workspace/antd
