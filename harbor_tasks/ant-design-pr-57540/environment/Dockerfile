FROM node:22-slim

# Install git, python3 for pytest runner, and other essentials
RUN apt-get update && apt-get install -y \
    git \
    python3 \
    python3-pip \
    python3-venv \
    && rm -rf /var/lib/apt/lists/* \
    && python3 -m pip install pytest --break-system-packages

# Create logs directory
RUN mkdir -p /logs/verifier

# Clone repository with shallow filter
WORKDIR /workspace
RUN git clone --filter=blob:none https://github.com/ant-design/ant-design.git antd

# Checkout base commit (parent of merge)
WORKDIR /workspace/antd
RUN git checkout 1ed0c62c7cbdd3ed02db8255d742c1b90dbb4299

# Install dependencies
RUN npm install --legacy-peer-deps

# Set working directory
WORKDIR /workspace/antd
