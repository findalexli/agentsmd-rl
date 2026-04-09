FROM node:22-slim

# Install Python and required dependencies for testing
RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    git \
    && rm -rf /var/lib/apt-get/lists/*

# Install pytest for running tests
RUN pip3 install pytest --break-system-packages

# Set working directory
WORKDIR /workspace

# Clone ant-design repo at base commit (shallow clone for speed)
RUN git clone --filter=blob:none https://github.com/ant-design/ant-design.git ant-design && \
    cd ant-design && \
    git checkout b836ec3cc69a6ed64eb8d9e469790b424e5100cf

# Install dependencies
WORKDIR /workspace/ant-design
RUN npm install

# Create logs directory for verifier
RUN mkdir -p /logs/verifier

# Set up test outputs mount point
VOLUME ["/tests", "/logs/verifier"]
