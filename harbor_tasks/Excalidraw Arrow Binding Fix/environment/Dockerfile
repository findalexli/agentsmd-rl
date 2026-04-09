FROM node:22-slim

# Install Python for test runner
RUN apt-get update && apt-get install -y python3 python3-pip git && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /workspace

# Clone the excalidraw repo at the base commit (shallow clone for speed)
RUN git clone --filter=blob:none https://github.com/excalidraw/excalidraw.git excalidraw && \
    cd excalidraw && \
    git checkout 60ab14c2f633112613843eec3c049f6da0f566e8

# Install dependencies
WORKDIR /workspace/excalidraw
RUN yarn install --frozen-lockfile

# Create logs directory for verifier
RUN mkdir -p /logs/verifier

# Set the working directory for the task
WORKDIR /workspace/excalidraw
