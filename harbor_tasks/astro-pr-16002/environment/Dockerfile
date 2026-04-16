FROM node:22-slim

# Install git, python3, and other required dependencies
RUN apt-get update && apt-get install -y \
    git \
    python3 \
    python3-pip \
    python3-venv \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install pnpm
RUN npm install -g pnpm@10.28.0

# Create logs directory for verifier
RUN mkdir -p /logs/verifier

# Clone the Astro repo at base commit
WORKDIR /workspace
RUN git clone --filter=blob:none https://github.com/withastro/astro.git

WORKDIR /workspace/astro

# Checkout the base commit (before the fix)
RUN git checkout 47694d0db98ef899dd5e0d337964f476d01d7904

# Install dependencies and build
RUN pnpm install
RUN pnpm run build

# Keep container running
CMD ["bash"]
