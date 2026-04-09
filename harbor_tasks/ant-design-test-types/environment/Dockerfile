FROM node:22-slim

# Install Python for pytest runner
RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    git \
    && rm -rf /var/lib/apt/lists/*

# Install pytest
RUN pip3 install pytest --break-system-packages

# Set working directory
WORKDIR /workspace

# Clone ant-design repo at base commit
RUN git clone --filter=blob:none https://github.com/ant-design/ant-design.git ant-design && \
    cd ant-design && \
    git checkout 227f2ba440c36ccec4afe7487c7b2b946b83de4e

WORKDIR /workspace/ant-design

# Install dependencies (use npm install --legacy-peer-deps for antd)
RUN npm install --legacy-peer-deps || npm install

# Create logs directory
RUN mkdir -p /logs/verifier

# Set NODE_OPTIONS for memory (needed for tsc compilation on large repos)
ENV NODE_OPTIONS="--max-old-space-size=4096"

# Default shell
CMD ["bash"]
