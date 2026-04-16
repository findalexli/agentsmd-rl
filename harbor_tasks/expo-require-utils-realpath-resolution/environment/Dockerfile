FROM node:22-slim

# Install git and python3 for pytest
RUN apt-get update && apt-get install -y \
    git \
    python3 \
    python3-pip \
    && rm -rf /var/lib/apt/lists/*

# Create working directory
WORKDIR /workspace

# Clone the expo repository at base commit
# Clone full packages directory since require-utils depends on some other packages
RUN git clone --filter=blob:none --no-checkout https://github.com/expo/expo.git /workspace/expo && \
    cd /workspace/expo && \
    git sparse-checkout init --cone && \
    git sparse-checkout set packages/@expo/require-utils packages/expo-module-scripts && \
    git checkout 25749d7dec5676f2f23d0454030598487d79a6c7

# Install dependencies in the package
WORKDIR /workspace/expo/packages/@expo/require-utils

# Install TypeScript globally for building
RUN npm install -g typescript @babel/cli @babel/core

# Install the package dependencies with full dependency tree
RUN npm install --legacy-peer-deps 2>&1 || yarn install 2>&1 || true

# Install pytest for running tests
RUN pip3 install pytest --break-system-packages || pip3 install pytest

# Create logs directory for test results
RUN mkdir -p /logs/verifier

# Default command
CMD ["bash"]
