FROM node:22-slim

# Install Python for pytest and git for cloning
RUN apt-get update && apt-get install -y --no-install-recommends \
    python3 python3-pip git \
    && rm -rf /var/lib/apt/lists/*

# Create required directories
RUN mkdir -p /workspace/excalidraw /logs/verifier

# Clone repo at base commit (will be done at runtime to ensure clean state)
# For now, set up the environment
WORKDIR /workspace

# Install pytest
RUN pip3 install pytest --break-system-packages

# Set environment variables
ENV NODE_ENV=development
ENV CI=true
