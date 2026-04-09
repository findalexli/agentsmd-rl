FROM node:22-slim

# Install Python for pytest
RUN apt-get update && apt-get install -y --no-install-recommends \
    python3 python3-pip git \
    && rm -rf /var/lib/apt/lists/*

# Install pytest
RUN pip3 install pytest --break-system-packages

# Set working directory
WORKDIR /workspace

# Clone the repo at base commit (shallow clone for speed)
ENV REPO_DIR=/workspace/OpenHands
RUN git clone --filter=blob:none --single-branch --branch main \
    https://github.com/All-Hands-AI/OpenHands.git ${REPO_DIR}

WORKDIR ${REPO_DIR}

# Checkout base commit (before the fix)
ENV BASE_COMMIT=c210d5294fa82459443e6163b9b1c9c9f55073fc
RUN git checkout ${BASE_COMMIT}

# Install frontend dependencies
WORKDIR ${REPO_DIR}/frontend
RUN npm ci

# Create logs directory for verifier
RUN mkdir -p /logs/verifier

# Set working directory back to repo root
WORKDIR ${REPO_DIR}
