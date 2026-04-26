FROM node:22-slim

# Install Python for pytest and git for cloning
RUN apt-get update && apt-get install -y --no-install-recommends \
    git \
    python3 \
    python3-pip \
    python3-venv \
    && rm -rf /var/lib/apt/lists/*

# Create virtual environment for Python
RUN python3 -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Install pytest and dependencies
RUN pip install pytest

WORKDIR /workspace

# Clone playwright repo at base commit
RUN git clone --filter=blob:none https://github.com/microsoft/playwright.git && \
    cd playwright && \
    git checkout 1ed53ac99ec225a5fc0aacb762a18e3195c61a6c

# Install dependencies (npm ci is faster and more reliable than npm install)
RUN cd /workspace/playwright && npm ci

# Ensure logs directory exists for reward file
RUN mkdir -p /logs/verifier

WORKDIR /workspace/playwright
