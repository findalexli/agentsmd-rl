FROM node:22-slim

# Install Python for pytest and git for cloning
RUN apt-get update && apt-get install -y --no-install-recommends \
    python3 \
    python3-pip \
    git \
    && rm -rf /var/lib/apt/lists/*

# Install pytest
RUN pip3 install pytest --break-system-packages

# Set up workspace
WORKDIR /workspace

# Clone the repository at the base commit
RUN git clone --filter=blob:none https://github.com/excalidraw/excalidraw.git && \
    cd excalidraw && \
    git checkout 60759d314d3d4545b22d8c6f35f5afa24efa14e4

WORKDIR /workspace/excalidraw

# Install dependencies
RUN yarn install --frozen-lockfile

# Create logs directory for verifier
RUN mkdir -p /logs/verifier

# Default shell
CMD ["bash"]
