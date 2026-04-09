FROM node:22-slim

# Install Python for pytest
RUN apt-get update && apt-get install -y python3 python3-pip git && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /workspace

# Clone the continue repository at base commit
ARG BASE_COMMIT=d971363a7e2711a056a2daafb4a788140bbf32a4
RUN git clone --filter=blob:none https://github.com/continuedev/continue.git && \
    cd continue && \
    git checkout ${BASE_COMMIT}

# Install dependencies
WORKDIR /workspace/continue
RUN npm install

# Install dependencies for openai-adapters package
WORKDIR /workspace/continue/packages/openai-adapters
RUN npm install

# Go back to root
WORKDIR /workspace/continue

# Create logs directory
RUN mkdir -p /logs/verifier

# Set environment
ENV NODE_ENV=development
