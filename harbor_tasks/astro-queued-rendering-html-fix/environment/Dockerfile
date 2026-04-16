FROM node:22-slim

# Install Python for pytest and git for cloning
RUN apt-get update && apt-get install -y --no-install-recommends \
    python3 \
    python3-pip \
    git \
    && rm -rf /var/lib/apt-get/lists/*

# Install pnpm
RUN npm install -g pnpm

# Set working directory
WORKDIR /workspace

# Clone the Astro repo at base commit (before the fix)
# Using depth to reduce clone size but we need enough history
RUN git clone --filter=blob:none https://github.com/withastro/astro.git astro

WORKDIR /workspace/astro

# Checkout the base commit (parent of merge commit)
RUN git checkout be661fb9fd1348ffb038f561f9f053b1c64a3696

# Install dependencies
RUN pnpm install --frozen-lockfile

# Build the packages (needed for tests to work)
RUN pnpm run build

# Install pytest
RUN pip3 install pytest --break-system-packages

# Create logs directory for verifier
RUN mkdir -p /logs/verifier

# Set working directory to the astro package for tests
WORKDIR /workspace/astro/packages/astro
