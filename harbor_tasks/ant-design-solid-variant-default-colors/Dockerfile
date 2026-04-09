FROM node:22-slim

# Install Python for pytest runner
RUN apt-get update && apt-get install -y python3 python3-pip git && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /workspace

# Clone the ant-design repository at base commit
# Using --depth to limit history and speed up clone
ARG BASE_COMMIT=df5547f2ade5fe0bd9906bb9a386e7865afa4835
RUN git clone --depth=100 --filter=blob:none https://github.com/ant-design/ant-design.git ant-design && \
    cd ant-design && \
    git checkout ${BASE_COMMIT}

# Install dependencies
WORKDIR /workspace/ant-design
RUN npm install

# Create verifier logs directory
RUN mkdir -p /logs/verifier

# Set back to workspace root
WORKDIR /workspace
