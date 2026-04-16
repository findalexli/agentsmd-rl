FROM node:22-slim

# Install git and python3 for pytest
RUN apt-get update && apt-get install -y \
    git \
    python3 \
    python3-pip \
    && rm -rf /var/lib/apt/lists/*

# Install pytest
RUN pip3 install pytest --break-system-packages

# Create logs directory
RUN mkdir -p /logs/verifier

# Set working directory
WORKDIR /workspace

# Clone the repo at base commit (shallow clone for speed)
ARG BASE_COMMIT=5a10ab2d17f4e5a8fc02e38cee31b6f63118d89b
RUN git clone --filter=blob:none --depth=50 https://github.com/mantinedev/mantine.git mantine && \
    cd mantine && \
    git checkout ${BASE_COMMIT}

# Install dependencies (yarn is already included in node:22-slim)
WORKDIR /workspace/mantine
RUN yarn install

WORKDIR /workspace/mantine
