FROM node:22-slim

# Install Python for pytest
RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    git \
    && rm -rf /var/lib/apt/lists/*

# Install pytest
RUN pip3 install pytest --break-system-packages

# Clone the repository at base commit
ARG BASE_COMMIT=3c8e893cab216eb1f748ec1245aeb059a1349639
RUN git clone --filter=blob:none https://github.com/excalidraw/excalidraw.git /workspace/excalidraw \
    && cd /workspace/excalidraw \
    && git checkout ${BASE_COMMIT}

WORKDIR /workspace/excalidraw

# Install dependencies
RUN yarn install --frozen-lockfile

# Create logs directory
RUN mkdir -p /logs/verifier
