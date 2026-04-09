FROM node:22-slim

# Install Python for pytest and required tools
RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    git \
    && rm -rf /var/lib/apt/lists/*

# Install pytest
RUN pip3 install pytest --break-system-packages

# Set up workspace
WORKDIR /workspace

# Clone ant-design at base commit (shallow clone for speed)
ARG BASE_COMMIT=501436e5f45e533679f797ee0ee58e2a391e566d
RUN git clone --filter=blob:none --single-branch --depth=100 \
    https://github.com/ant-design/ant-design.git ant-design && \
    cd ant-design && \
    git fetch --depth=100 origin ${BASE_COMMIT} && \
    git checkout ${BASE_COMMIT}

# Install dependencies
WORKDIR /workspace/ant-design
RUN npm install --legacy-peer-deps

# Create logs directory for verifier
RUN mkdir -p /logs/verifier

WORKDIR /workspace/ant-design
