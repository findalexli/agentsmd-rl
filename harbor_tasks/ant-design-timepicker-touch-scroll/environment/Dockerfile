FROM node:22-slim

# Install Python for pytest and git for cloning
RUN apt-get update && apt-get install -y --no-install-recommends \
    python3 \
    python3-pip \
    git \
    && rm -rf /var/lib/apt-get/lists/*

# Install pytest
RUN pip3 install pytest --break-system-packages

# Set working directory
WORKDIR /workspace

# Clone ant-design repo at base commit (shallow clone for efficiency)
ARG REPO=ant-design
ARG BASE_COMMIT=14e3c384e9c7d5b6096ed60ae5de3db80b8a39c9

RUN git clone --filter=blob:none --depth=100 https://github.com/ant-design/ant-design.git && \
    cd ant-design && \
    git checkout ${BASE_COMMIT}

# Create logs directory
RUN mkdir -p /logs/verifier

# Set permissions
RUN chmod -R 755 /workspace/ant-design

WORKDIR /workspace/ant-design
