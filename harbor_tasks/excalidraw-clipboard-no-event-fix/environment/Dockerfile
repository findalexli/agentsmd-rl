FROM node:22-slim

# Install Python for pytest and git for cloning
RUN apt-get update && apt-get install -y python3 python3-pip git && rm -rf /var/lib/apt/lists/*

# Install pytest
RUN pip3 install pytest --break-system-packages

# Set working directory
WORKDIR /workspace

# Clone the repository at base commit
RUN git clone --filter=blob:none https://github.com/excalidraw/excalidraw.git excalidraw && \
    cd excalidraw && \
    git checkout d29fd62e417b8cb73d1d5dc3e207735046401491

# Install dependencies
WORKDIR /workspace/excalidraw
RUN yarn install --frozen-lockfile

# Create logs directory for verifier
RUN mkdir -p /logs/verifier

# Default to excalidraw directory
WORKDIR /workspace/excalidraw
