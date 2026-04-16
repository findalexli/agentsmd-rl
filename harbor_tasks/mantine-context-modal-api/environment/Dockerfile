FROM node:22-slim

# Install python3 and git (needed for test runner and cloning)
RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    git \
    && rm -rf /var/lib/apt/lists/*

# Install pytest
RUN pip3 install pytest --break-system-packages

# Clone the mantine repo at base commit
WORKDIR /workspace
ARG BASE_COMMIT=c3a53eb0c345037d0b5406e925ef5a5e2926022b
RUN git clone --filter=blob:none https://github.com/mantinedev/mantine.git && \
    cd mantine && \
    git checkout ${BASE_COMMIT}

# Install dependencies (this project uses yarn)
WORKDIR /workspace/mantine
RUN yarn install

# Create logs directory for verifier
RUN mkdir -p /logs/verifier

WORKDIR /workspace/mantine
