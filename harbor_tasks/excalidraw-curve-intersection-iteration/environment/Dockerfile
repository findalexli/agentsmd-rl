FROM node:22-slim

# Install Python and required dependencies for pytest
RUN apt-get update && apt-get install -y --no-install-recommends \
    python3 \
    python3-pip \
    git \
    && rm -rf /var/lib/apt/lists/*

# Install pytest
RUN pip3 install pytest --break-system-packages

# Set working directory
WORKDIR /workspace/excalidraw

# Clone the repo at base commit (shallow clone for speed)
ARG BASE_COMMIT=dfdd994dbbefc0562c0c5e42f267f23ae8d9d62d
RUN git clone --depth=100 --filter=blob:none https://github.com/excalidraw/excalidraw.git /workspace/excalidraw && \
    git checkout ${BASE_COMMIT}

# Install dependencies (Yarn workspace install)
RUN yarn install --frozen-lockfile

# Create logs directory for verifier
RUN mkdir -p /logs/verifier
