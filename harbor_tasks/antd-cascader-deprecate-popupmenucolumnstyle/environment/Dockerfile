FROM node:22-slim

# Install Python and required dependencies
RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    git \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /workspace

# Clone the ant-design repository at base commit
# Using depth to reduce clone size, then fetch specific commit
RUN git clone --filter=blob:none --depth=1000 https://github.com/ant-design/ant-design.git && \
    cd ant-design && \
    git fetch --depth=1000 origin ffe7ccf17f689af990c4757c8197c8727c8f4184 && \
    git checkout ffe7ccf17f689af990c4757c8197c8727c8f4184

WORKDIR /workspace/ant-design

# Install dependencies (skip postinstall scripts for faster build)
RUN npm install --ignore-scripts --legacy-peer-deps

# Create logs directory for verifier
RUN mkdir -p /logs/verifier

# Default command
CMD ["bash"]
