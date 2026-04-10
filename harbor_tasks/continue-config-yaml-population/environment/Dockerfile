FROM node:22-slim

RUN apt-get update && apt-get install -y --no-install-recommends \
    git \
    python3 \
    python3-pip \
    build-essential \
    make \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Install pytest for the test runner
RUN pip3 install pytest --break-system-packages

WORKDIR /workspace

# Clone the repo at base commit
RUN git clone --filter=blob:none https://github.com/continuedev/continue.git && \
    cd continue && \
    git checkout 16a540c3378b833931429db9bcb3ce7c98bd7a36

# Install root dependencies (includes eslint)
WORKDIR /workspace/continue
RUN npm install && npm cache clean --force

# Install core dependencies
WORKDIR /workspace/continue/core
RUN npm install && npm cache clean --force

# Create verifier logs directory
RUN mkdir -p /logs/verifier

WORKDIR /workspace
