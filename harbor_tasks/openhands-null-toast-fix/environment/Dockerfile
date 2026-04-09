FROM node:22-slim

# Install Python and required packages for pytest
RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    git \
    && rm -rf /var/lib/apt/lists/*

# Install pytest
RUN pip3 install pytest --break-system-packages

# Set working directory
WORKDIR /workspace

# Clone the OpenHands repo at base commit
RUN git clone --filter=blob:none https://github.com/All-Hands-AI/OpenHands.git && \
    cd OpenHands && \
    git checkout 679460396315ee10ad7384c5a97d441b2844db1b

# Install frontend dependencies
WORKDIR /workspace/OpenHands/frontend
RUN npm install

# Create logs directory for verifier
RUN mkdir -p /logs/verifier

# Set working directory back to repo root for tests
WORKDIR /workspace/OpenHands
