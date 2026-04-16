FROM node:22-slim

# Install Python for pytest runner and git
RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    python3-venv \
    git \
    && rm -rf /var/lib/apt/lists/* \
    && pip3 install pytest --break-system-packages

# Create logs directory
RUN mkdir -p /logs/verifier

# Clone repository with blob filter for efficiency
WORKDIR /workspace
RUN git clone --filter=blob:none https://github.com/ant-design/ant-design.git antd

# Checkout base commit
WORKDIR /workspace/antd
RUN git checkout 22593b0188851158d8541bcc4055a68a25f0df7e

# Install dependencies
RUN npm install --legacy-peer-deps

# Set working directory
WORKDIR /workspace/antd
