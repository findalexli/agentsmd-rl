FROM node:22-slim

# Install Python and required packages for testing
RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    python3-pytest \
    git \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Create logs directory for verifier
RUN mkdir -p /logs/verifier

# Clone the repo at the base commit (before the fix)
WORKDIR /workspace
ARG BASE_COMMIT=679460396315ee10ad7384c5a97d441b2844db1b
RUN git clone --filter=blob:none https://github.com/OpenHands/OpenHands.git && \
    cd OpenHands && \
    git checkout ${BASE_COMMIT}

# Install frontend dependencies
WORKDIR /workspace/OpenHands/frontend
RUN npm install

# Set working directory for tests
WORKDIR /workspace
