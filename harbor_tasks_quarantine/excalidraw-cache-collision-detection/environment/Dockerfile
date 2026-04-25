FROM node:22-slim

# Install Python for pytest
RUN apt-get update && apt-get install -y python3 python3-pip git curl && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /workspace

# Clone the repository at base commit
RUN git clone --filter=blob:none https://github.com/excalidraw/excalidraw.git excalidraw && \
    cd excalidraw && \
    git checkout 3b97f5a10cc576cbe7863a2e4772203ebb13b606

# Install dependencies (using yarn in the monorepo)
WORKDIR /workspace/excalidraw
RUN yarn install --frozen-lockfile

# Create logs directory
RUN mkdir -p /logs/verifier

# Set default working directory for tests
WORKDIR /workspace/excalidraw
