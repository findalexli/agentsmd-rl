FROM node:22-slim

# Install Python and git
RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    python3-venv \
    git \
    make \
    && rm -rf /var/lib/apt/lists/*

# Set up Python symlink
RUN ln -sf /usr/bin/python3 /usr/bin/python

# Set workdir
WORKDIR /workspace

# Clone repo at base commit (shallow clone for speed)
ARG BASE_COMMIT=3cd85a07b78a2d9d2e28b2904e1b42096d47a802
RUN git clone --filter=blob:none --depth=100 https://github.com/All-Hands-AI/OpenHands.git openhands && \
    cd openhands && \
    git fetch --depth=100 origin ${BASE_COMMIT} && \
    git checkout ${BASE_COMMIT}

# Install frontend dependencies
WORKDIR /workspace/openhands/frontend
RUN npm install

# Install Python dependencies for testing
RUN pip install pytest --break-system-packages

# Create logs directory
RUN mkdir -p /logs/verifier

# Reset to workdir
WORKDIR /workspace/openhands
