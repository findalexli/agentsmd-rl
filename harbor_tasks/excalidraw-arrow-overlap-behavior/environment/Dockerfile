FROM node:22-slim

# Install git and python3 (needed for pytest runner)
RUN apt-get update && apt-get install -y --no-install-recommends \
    git \
    python3 \
    python3-pip \
    && rm -rf /var/lib/apt/lists/*

# Install pytest
RUN pip3 install pytest --break-system-packages

# Set working directory
WORKDIR /workspace

# Clone the excalidraw repo at base commit
ARG BASE_COMMIT=c1e00c44f57841b18ea14bde30b8d1f5aff95c7e
RUN git clone --filter=blob:none https://github.com/excalidraw/excalidraw.git excalidraw \
    && cd excalidraw \
    && git fetch --depth=1 origin ${BASE_COMMIT} \
    && git checkout ${BASE_COMMIT}

# Install dependencies
WORKDIR /workspace/excalidraw
RUN yarn install --frozen-lockfile

# Create logs directory
RUN mkdir -p /logs/verifier

WORKDIR /workspace/excalidraw
