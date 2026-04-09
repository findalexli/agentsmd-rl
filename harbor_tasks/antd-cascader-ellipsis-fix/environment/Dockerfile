FROM node:18-slim

# Install Python for pytest
RUN apt-get update && apt-get install -y python3 python3-pip git && rm -rf /var/lib/apt/lists/*

# Install pytest
RUN pip3 install pytest --break-system-packages || pip3 install pytest

# Create necessary directories
RUN mkdir -p /workspace/ant-design /logs/verifier

# Clone the ant-design repo at base commit
WORKDIR /workspace
RUN git clone --filter=blob:none https://github.com/ant-design/ant-design.git && \
    cd ant-design && \
    git checkout 1ed0c62c7cbdd3ed02db8255d742c1b90dbb4299

# Set working directory
WORKDIR /workspace/ant-design
