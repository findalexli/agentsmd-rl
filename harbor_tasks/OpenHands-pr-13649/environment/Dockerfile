FROM node:22-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    git \
    python3 \
    python3-pip \
    && rm -rf /var/lib/apt/lists/*

# Install pytest
RUN pip3 install pytest --break-system-packages

# Create working directory
WORKDIR /workspace

# Clone the repository at base commit
ARG REPO="https://github.com/All-Hands-AI/OpenHands"
ARG BASE_COMMIT="5528b01c186958bf2c92d9adaaa7f7ea0c487185"
RUN git clone --filter=blob:none --no-checkout ${REPO} openhands \
    && cd openhands \
    && git sparse-checkout set frontend/ \
    && git checkout ${BASE_COMMIT}

WORKDIR /workspace/openhands/frontend

# Install dependencies
RUN npm install

# Create logs directory
RUN mkdir -p /logs/verifier

# Set up test command
CMD ["npm", "test", "--", "--run", "billing.test.tsx"]
