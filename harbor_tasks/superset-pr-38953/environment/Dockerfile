FROM node:22-slim

# Install Python for pytest runner and git for cloning
RUN apt-get update && apt-get install -y --no-install-recommends \
    git \
    python3 \
    python3-pip \
    python3-venv \
    && rm -rf /var/lib/apt/lists/*

# Set up working directory
WORKDIR /workspace

# Clone the repository at the base commit
ARG BASE_COMMIT=e0a0a2254265cce88e5dfca1c3b3ca8b8e155122
RUN git clone --filter=blob:none --no-checkout https://github.com/apache/superset.git superset && \
    cd superset && \
    git checkout ${BASE_COMMIT}

# Install Python dependencies for test runner
RUN pip3 install pytest --break-system-packages

# Create logs directory
RUN mkdir -p /logs/verifier

WORKDIR /workspace/superset
