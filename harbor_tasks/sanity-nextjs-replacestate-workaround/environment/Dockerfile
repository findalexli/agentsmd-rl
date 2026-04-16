FROM node:22-slim

# Install required dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    git \
    ca-certificates \
    python3 \
    python3-pip \
    && rm -rf /var/lib/apt/lists/*

# Install pnpm
RUN npm install -g pnpm@10

# Clone the repo at base commit
WORKDIR /workspace
RUN git clone --filter=blob:none https://github.com/sanity-io/sanity.git
WORKDIR /workspace/sanity
RUN git checkout e9f037f5afd5b6bf3feae79ea0f0f8390e2d4d65

# Install dependencies (use ci for faster, reproducible install)
RUN pnpm install --frozen-lockfile

# Install pytest
RUN pip3 install pytest --break-system-packages

# Create log directory
RUN mkdir -p /logs/verifier

# Default workdir for tests
WORKDIR /workspace/sanity
