FROM node:22-slim

# Install Python for pytest, git for cloning, and patch for applying fixes
RUN apt-get update && apt-get install -y --no-install-recommends     python3 python3-pip git patch     && rm -rf /var/lib/apt/lists/*

# Create required directories
RUN mkdir -p /workspace/excalidraw /logs/verifier

# Clone repo at base commit (8d18078 - before PR #10479 merge)
RUN git clone --depth 100 https://github.com/excalidraw/excalidraw.git /workspace/excalidraw && \
    cd /workspace/excalidraw && \
    git checkout 8d18078

# Install dependencies
WORKDIR /workspace/excalidraw
RUN yarn install --frozen-lockfile

# Install pytest
RUN pip3 install pytest --break-system-packages

# Set environment variables
ENV NODE_ENV=development
ENV CI=true
