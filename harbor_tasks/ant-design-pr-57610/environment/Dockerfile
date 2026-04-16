# Dockerfile for ant-design Image accessibility task
FROM node:22-slim

# Install Python for pytest runner and git
RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    python3-venv \
    git \
    && rm -rf /var/lib/apt/lists/*

# Create virtual environment for Python
RUN python3 -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

WORKDIR /workspace

# Clone ant-design at base commit (before PR merge)
RUN git clone --filter=blob:none https://github.com/ant-design/ant-design.git antd \
    && cd antd \
    && git checkout c87f6a960d604b2237c24c3cd233cf9286ab11e3

WORKDIR /workspace/antd

# Install dependencies
RUN npm install --legacy-peer-deps

# Create logs directory
RUN mkdir -p /logs/verifier

# Set working directory for the task
WORKDIR /workspace/antd
