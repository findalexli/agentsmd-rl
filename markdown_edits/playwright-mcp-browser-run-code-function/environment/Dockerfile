FROM node:22-bookworm

# Install git and Python
RUN apt-get clean && \
    apt-get update && \
    apt-get install -y --no-install-recommends \
        git \
        python3 \
        python3-pip \
    && rm -rf /var/lib/apt/lists/* /var/cache/apt/archives/*

# Set up workspace
WORKDIR /workspace
RUN mkdir -p /logs/verifier

# Clone the repo at the base commit
ARG BASE_COMMIT=703996071cb3a7ec642b30a2b428c369c3ebb7c7
RUN git clone --depth=1 --filter=blob:none \
    https://github.com/microsoft/playwright.git /workspace/playwright && \
    cd /workspace/playwright && \
    git fetch --depth=1 origin ${BASE_COMMIT} && \
    git checkout ${BASE_COMMIT}

# Default working directory for tests
WORKDIR /workspace/playwright
