FROM node:22.12-slim

# Install git and python for pytest runner
RUN apt-get update && apt-get install -y \
    git \
    python3 \
    python3-pip \
    && rm -rf /var/lib/apt/lists/* \
    && pip install pytest --break-system-packages

# Set working directory
WORKDIR /workspace

# Clone the OpenHands repo at base commit (shallow clone for speed)
# Use filter=blob:none to get file history without all blobs
RUN git clone --filter=blob:none https://github.com/OpenHands/OpenHands.git && \
    cd OpenHands && \
    git checkout 3cd85a07b78a2d9d2e28b2904e1b42096d47a802

# Install frontend dependencies
WORKDIR /workspace/OpenHands/frontend
RUN npm install

# Create logs directory for verifier
RUN mkdir -p /logs/verifier

# Set working directory back to /workspace for tests
WORKDIR /workspace
