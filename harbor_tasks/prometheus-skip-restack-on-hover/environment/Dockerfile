FROM node:22-slim

# Install Python and git
RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    git \
    && rm -rf /var/lib/apt/lists/*

# Set up working directory
WORKDIR /workspace

# Clone the repository at base commit (shallow clone for efficiency)
ARG BASE_COMMIT=ac12e30f99df9d2f68025f0238c0aef95146e94b
RUN git clone --depth 100 --filter=blob:none https://github.com/prometheus/prometheus.git prometheus && \
    cd prometheus && \
    git fetch --depth 100 origin ${BASE_COMMIT} && \
    git checkout ${BASE_COMMIT}

# Set working directory to the UI package
WORKDIR /workspace/prometheus/web/ui/mantine-ui

# Install dependencies (the package.json exists here)
RUN npm ci

# Create logs directory for verifier
RUN mkdir -p /logs/verifier

# Default shell
SHELL ["/bin/bash", "-c"]
