FROM node:22-slim

# Install Python for test runner
RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    git \
    && rm -rf /var/lib/apt/lists/*

# Install pytest
RUN pip3 install pytest --break-system-packages

# Clone the repo at base commit
WORKDIR /workspace
RUN git clone --filter=blob:none https://github.com/TanStack/router.git router

WORKDIR /workspace/router
RUN git checkout cd7116b53b7ba3152129b5c656dfcaeb0d62c5b8

# Install dependencies
RUN npm install

# Create logs directory
RUN mkdir -p /logs/verifier

WORKDIR /workspace/router
