FROM node:22-slim

# Install Python for pytest and git for cloning
RUN apt-get update && apt-get install -y python3 python3-pip git && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /workspace

# Clone the excalidraw repo at base commit (shallow clone for speed)
ARG BASE_COMMIT=0988ecfef40db7c965fd79c43454d154cf83aced
RUN git clone --depth=100 --filter=blob:none https://github.com/excalidraw/excalidraw.git && \
    cd excalidraw && \
    git fetch --depth=100 origin ${BASE_COMMIT} && \
    git checkout ${BASE_COMMIT}

# Install dependencies
WORKDIR /workspace/excalidraw
RUN yarn install --frozen-lockfile

# Create logs directory for test results
RUN mkdir -p /logs/verifier

# Set working directory for the task
WORKDIR /workspace/excalidraw
