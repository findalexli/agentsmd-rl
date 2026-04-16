FROM node:22-slim

# Install Python for test runner
RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    git \
    && rm -rf /var/lib/apt/lists/*

# Install pytest
RUN pip3 install pytest --break-system-packages

# Clone the repository at base commit
WORKDIR /workspace
RUN git clone --filter=blob:none https://github.com/cline/cline.git cline \
    && cd cline \
    && git checkout b3fc79b8ce7df37a3dc4814281089c1866edf49c

# Install CLI dependencies
WORKDIR /workspace/cline/cli
RUN npm install

# Create logs directory for verifier
RUN mkdir -p /logs/verifier

# Set working directory for the task
WORKDIR /workspace/cline
