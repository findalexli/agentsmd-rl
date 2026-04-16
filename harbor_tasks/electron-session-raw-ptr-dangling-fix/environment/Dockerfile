FROM node:22-slim

# Install Python, git, and pytest for testing
RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    python3-pytest \
    git \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Create working directory and verifier logs
RUN mkdir -p /workspace/electron /logs/verifier
WORKDIR /workspace/electron

# Clone the Electron repository with shallow depth
# Checkout the specific base commit in one command
RUN git clone --depth=100 https://github.com/electron/electron.git /workspace/electron && \
    git fetch --depth=50 origin 7bd5de006e7a3a5eb5db0e66d79a31815abdd58d && \
    git checkout 7bd5de006e7a3a5eb5db0e66d79a31815abdd58d

# Install npm dependencies (minimal subset for testing)
RUN npm install typescript --no-save 2>/dev/null || true

WORKDIR /workspace/electron
