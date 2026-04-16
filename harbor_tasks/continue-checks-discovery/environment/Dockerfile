FROM node:22-slim

RUN apt-get update && apt-get install -y \
    git \
    python3 \
    python3-pip \
    && rm -rf /var/lib/apt/lists/*

RUN pip3 install pytest --break-system-packages

WORKDIR /workspace

# Clone the continue repo at the base commit
RUN git clone --filter=blob:none https://github.com/continuedev/continue.git && \
    cd continue && \
    git checkout 173810bab405bb1c6e3740e90207ffdc17d1065b

# Install minimal dependencies for vitest (only what's needed for testing)
WORKDIR /workspace/continue/extensions/cli

# Install only vitest and essential deps, skip the full build
RUN npm install vitest @types/node --no-save 2>/dev/null || true

# Create logs directory for verifier
RUN mkdir -p /logs/verifier

WORKDIR /workspace/continue/extensions/cli
