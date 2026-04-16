FROM node:22-slim

# Install git, python3 and pip for pytest runner
RUN apt-get update && apt-get install -y --no-install-recommends git python3 python3-pip && rm -rf /var/lib/apt/lists/*

# Install pnpm and required tools
RUN npm install -g pnpm@10.15.1

# Create workspace directory
WORKDIR /workspace

# Clone the repository at the specific base commit
# Base commit: 6a3c3ccf9cc2db7f27bbbf6df9f050fc112dc66e
# Using blob:none filter for efficiency
RUN git clone --filter=blob:none https://github.com/prisma/prisma.git && \
    cd prisma && \
    git checkout 6a3c3ccf9cc2db7f27bbbf6df9f050fc112dc66e

WORKDIR /workspace/prisma

# Install dependencies
RUN pnpm install --frozen-lockfile || pnpm install

# Create logs directory
RUN mkdir -p /logs/verifier

# Default command
CMD ["bash"]