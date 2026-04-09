FROM node:22-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    git \
    python3 \
    python3-pip \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /workspace/ant-design

# Clone repo at base commit
ARG BASE_COMMIT=df5547f2ade5fe0bd9906bb9a386e7865afa4835
RUN git clone --filter=blob:none https://github.com/ant-design/ant-design.git /workspace/ant-design && \
    git checkout ${BASE_COMMIT}

# Install dependencies
RUN npm install

# Create logs directory for verifier
RUN mkdir -p /logs/verifier
