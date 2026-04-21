FROM node:22-slim

# Install Python for test runner
RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    git \
    && rm -rf /var/lib/apt/lists/*

# Install pytest
RUN pip3 install pytest --break-system-packages

# Clone the repo at base commit (before PR #7077)
WORKDIR /workspace
RUN git clone --filter=blob:none https://github.com/TanStack/router.git router

WORKDIR /workspace/router
RUN git checkout d1174179082d896a9674532994a4d6b38238c37e

# Install dependencies
RUN npm install

# Create logs directory
RUN mkdir -p /logs/verifier

WORKDIR /workspace/router
