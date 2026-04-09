FROM node:22-slim

# Install Python for pytest
RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    git \
    && rm -rf /var/lib/apt/lists/*

# Install pytest
RUN pip3 install pytest --break-system-packages

# Create working directory
WORKDIR /workspace

# Clone ant-design at base commit
RUN git clone --filter=blob:none https://github.com/ant-design/ant-design.git && \
    cd ant-design && \
    git checkout 611be598bdba1665aebd09bfedebb7001926a5c1

WORKDIR /workspace/ant-design

# Install dependencies (this may take time, so do it early)
RUN npm install --legacy-peer-deps || true

# Create verifier logs directory
RUN mkdir -p /logs/verifier

# Set environment
ENV NODE_ENV=test
ENV CI=true
