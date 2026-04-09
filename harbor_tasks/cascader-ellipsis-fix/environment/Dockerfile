FROM node:22-slim

# Install Python and git
RUN apt-get update && apt-get install -y git python3 python3-pip && rm -rf /var/lib/apt/lists/*

# Install pytest
RUN pip3 install pytest --break-system-packages

# Clone the ant-design repo and checkout base commit
RUN git clone --filter=blob:none https://github.com/ant-design/ant-design.git /workspace/ant-design && \
    cd /workspace/ant-design && \
    git checkout 1ed0c62c7cbdd3ed02db8255d742c1b90dbb4299

# Install npm dependencies
WORKDIR /workspace/ant-design
RUN npm install --legacy-peer-deps 2>&1 | tail -20 || npm install --force 2>&1 | tail -20

# Create logs directory
RUN mkdir -p /logs/verifier

# Set working directory
WORKDIR /workspace/ant-design
