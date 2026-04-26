FROM node:22-slim

# Install Python for test runner
RUN apt-get update && apt-get install -y python3 python3-pip git && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /workspace

# Clone the excalidraw repo at the base commit (shallow clone for speed)
RUN git init /workspace/excalidraw && \
    cd /workspace/excalidraw && \
    git remote add origin https://github.com/excalidraw/excalidraw.git && \
    git fetch --depth=1 origin 60ab14c2f633112613843eec3c049f6da0f566e8 && \
    git checkout FETCH_HEAD

# Install dependencies
WORKDIR /workspace/excalidraw
RUN yarn install --frozen-lockfile

# Create logs directory for verifier
RUN mkdir -p /logs/verifier

# Set the working directory for the task
WORKDIR /workspace/excalidraw
