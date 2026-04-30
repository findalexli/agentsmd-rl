# Bun SQL undefined filter task
# Tests the sql() helper fix for filtering undefined values in INSERT statements

FROM node:22-slim

# Install required dependencies
RUN apt-get update && apt-get install -y \
    git \
    python3 \
    python3-pip \
    curl \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Install bun for running tests
RUN curl -fsSL https://bun.sh/install | bash
ENV PATH="/root/.bun/bin:${PATH}"

# Set working directory
WORKDIR /workspace

# Create logs directory for verifier
RUN mkdir -p /logs/verifier

# Clone the Bun repository at the base commit (before the fix)
# Using shallow clone for faster checkout
ARG BASE_COMMIT=27ff6aaae0e925659c8f82ab6a4be17ec9c35a4a
RUN git clone --depth 100 --filter=blob:none https://github.com/oven-sh/bun.git bun \
    && cd bun \
    && git fetch --depth=100 origin ${BASE_COMMIT} \
    && git checkout ${BASE_COMMIT}

# Install pytest for test execution
RUN pip3 install pytest --break-system-packages

WORKDIR /workspace/bun
