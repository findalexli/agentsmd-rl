FROM node:22-slim

# Install Python for pytest and git for cloning
RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    git \
    && rm -rf /var/lib/apt/lists/*

# Install pytest
RUN pip3 install pytest --break-system-packages

# Set up workspace
WORKDIR /workspace/openhands

# Clone the repository at base commit
RUN git clone --filter=blob:none https://github.com/All-Hands-AI/OpenHands.git . \
    && git checkout 30b7af31b9cc6c7e1dbdb88f311ae4da3fdfb3c3

# Install frontend dependencies
WORKDIR /workspace/openhands/frontend
RUN npm install

# Generate i18n files (needed for tests)
RUN npm run make-i18n

# Create logs directory
RUN mkdir -p /logs/verifier

# Set working directory for tests
WORKDIR /workspace/openhands/frontend
