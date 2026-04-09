FROM node:22-slim

# Install Python for pytest runner
RUN apt-get update && apt-get install -y python3 python3-pip git && rm -rf /var/lib/apt/lists/*

# Install pytest
RUN pip3 install pytest --break-system-packages

# Set working directory
WORKDIR /workspace

# Clone the OpenHands repo at base commit (shallow clone for speed)
ARG BASE_COMMIT=df64ce9668ebd0116d0b6864a410adfedc615e96
RUN git clone --depth 100 --filter=blob:none https://github.com/All-Hands-AI/OpenHands.git && \
    cd OpenHands && \
    git fetch --depth 100 origin ${BASE_COMMIT} && \
    git checkout ${BASE_COMMIT}

# Install frontend dependencies
WORKDIR /workspace/OpenHands/frontend
RUN npm ci

# Create logs directory for verifier
RUN mkdir -p /logs/verifier

# Set back to workspace
WORKDIR /workspace
