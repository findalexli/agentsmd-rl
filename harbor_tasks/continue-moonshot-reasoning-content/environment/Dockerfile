FROM node:22-slim

# Install required packages including Python for pytest and build tools for native modules
RUN apt-get update && apt-get install -y --no-install-recommends \
    git \
    python3 \
    python3-pip \
    python3-venv \
    python3-dev \
    build-essential \
    curl \
    ca-certificates \
    pkg-config \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /workspace

# Clone the repository at the base commit (parent of merge commit)
ARG BASE_COMMIT=f7437593fdeb85fceb81d069835c6a3a90276c3a
RUN git clone --filter=blob:none --depth=100 https://github.com/continuedev/continue.git /workspace/continue && \
    cd /workspace/continue && \
    git checkout ${BASE_COMMIT}

# Install dependencies in the core directory - skip optional deps
WORKDIR /workspace/continue/core
RUN npm install --no-optional || npm install --ignore-scripts

# Install pytest for running tests
RUN pip3 install pytest --break-system-packages

# Create logs directory
RUN mkdir -p /logs/verifier

WORKDIR /workspace/continue
