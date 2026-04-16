FROM node:22-slim

# Install Python for pytest runner
RUN apt-get update && apt-get install -y --no-install-recommends \
    python3 \
    python3-pip \
    git \
    && rm -rf /var/lib/apt/lists/*

# Install pytest
RUN pip3 install pytest pyyaml --break-system-packages

# Set working directory
WORKDIR /workspace

# Clone the repository at base commit (shallow clone for efficiency)
# Base commit is 5528b01c186958bf2c92d9adaaa7f7ea0c487185 (parent of merge)
RUN git clone --filter=blob:none https://github.com/All-Hands-AI/OpenHands.git OpenHands && \
    cd OpenHands && \
    git fetch --depth=1 origin 5528b01c186958bf2c92d9adaaa7f7ea0c487185 && \
    git checkout 5528b01c186958bf2c92d9adaaa7f7ea0c487185

WORKDIR /workspace/OpenHands/frontend

# Install frontend dependencies
RUN npm ci

# Add the test file with checkout success flow tests (these will fail on base commit)
COPY billing.test.patch /tmp/
RUN cd /workspace/OpenHands && git apply /tmp/billing.test.patch || true

# Create logs directory for verifier
RUN mkdir -p /logs/verifier

# Default command
CMD ["bash"]
