FROM node:22-slim

# Install python3 for pytest runner and git for cloning
RUN apt-get update && apt-get install -y --no-install-recommends \
    python3 \
    python3-pip \
    python3-venv \
    git \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Create virtual environment and install pytest
RUN python3 -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"
RUN pip install --no-cache-dir pytest

WORKDIR /workspace

# Clone repo with blobless filter for faster clone
RUN git clone --filter=blob:none https://github.com/apache/superset.git superset

WORKDIR /workspace/superset

# Checkout base commit (before the fix)
RUN git checkout b8b2bdedf9bca608cbf0c4f0992be30877de300d

# Install frontend dependencies
WORKDIR /workspace/superset/superset-frontend
RUN npm ci --legacy-peer-deps

# Create logs directory
RUN mkdir -p /logs/verifier

WORKDIR /workspace/superset
