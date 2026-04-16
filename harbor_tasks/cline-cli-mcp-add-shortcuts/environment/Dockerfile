FROM node:22-slim

# Install Python for pytest runner and git for cloning
RUN apt-get update && apt-get install -y --no-install-recommends \
    python3 \
    python3-pip \
    git \
    && rm -rf /var/lib/apt/lists/*

# Install pytest
RUN pip3 install pytest --break-system-packages

# Set working directory
WORKDIR /workspace

# Clone the cline repository at base commit
# Using --filter=blob:none for shallow clone, then checkout specific commit
RUN git clone --filter=blob:none https://github.com/cline/cline.git /workspace/cline && \
    cd /workspace/cline && \
    git checkout 6d29bc6551ba9af46939c610172ad797743bd0db

# Install CLI dependencies
WORKDIR /workspace/cline/cli
RUN npm install

# Create logs directory for verifier
RUN mkdir -p /logs/verifier

# Set working directory to CLI for tests
WORKDIR /workspace/cline

# Default command
CMD ["/bin/bash"]
