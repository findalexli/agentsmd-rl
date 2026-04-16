FROM node:22-slim

# Install Python for pytest and git for cloning
RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    git \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /workspace

# Clone the repository at the base commit
ARG BASE_COMMIT=3c8e893cab216eb1f748ec1245aeb059a1349639
RUN git clone --filter=blob:none https://github.com/excalidraw/excalidraw.git /workspace/excalidraw && \
    cd /workspace/excalidraw && \
    git checkout ${BASE_COMMIT}

# Install dependencies
WORKDIR /workspace/excalidraw
RUN yarn install --frozen-lockfile

# Create logs directory for verifier
RUN mkdir -p /logs/verifier

# Set the working directory for the task
WORKDIR /workspace/excalidraw
