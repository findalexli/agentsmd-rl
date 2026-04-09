FROM node:22-slim

# Install Python for pytest and yarn
RUN apt-get update && apt-get install -y --no-install-recommends \
    python3 \
    python3-pip \
    git \
    && rm -rf /var/lib/apt/lists/*

# Install pytest
RUN pip3 install pytest --break-system-packages

# Set working directory
WORKDIR /workspace

# Clone the repository at base commit
ARG BASE_COMMIT=d5e37cda812094bb103d53f9b122faa941f5b5bf
RUN git clone --filter=blob:none https://github.com/excalidraw/excalidraw.git excalidraw && \
    cd excalidraw && \
    git checkout ${BASE_COMMIT}

# Install dependencies
WORKDIR /workspace/excalidraw
RUN yarn install --frozen-lockfile

# Create log directory
RUN mkdir -p /logs/verifier

# Set working directory for the task
WORKDIR /workspace
