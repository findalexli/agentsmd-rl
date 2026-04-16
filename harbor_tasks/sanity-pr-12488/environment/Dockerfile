FROM node:22-slim

# Install pnpm (required package manager for this repo)
RUN npm install -g pnpm@10

# Install git and python3 (for pytest runner)
RUN apt-get update && apt-get install -y git python3 python3-pip && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /workspace

# Clone the sanity repo at the base commit (before the fix)
# Base commit: d5c2b1ca31014526cf1178c34443879131bd9452
RUN git clone --filter=blob:none --depth 100 https://github.com/sanity-io/sanity.git && \
    cd sanity && \
    git checkout d5c2b1ca31014526cf1178c34443879131bd9452

WORKDIR /workspace/sanity

# Install dependencies using pnpm (MUST use pnpm, not npm)
# The repo enforces pnpm via preinstall hook
RUN pnpm install

# Build required packages (build is needed before tests can run)
RUN pnpm build

# Create logs directory for verifier
RUN mkdir -p /logs/verifier

# Default command
CMD ["bash"]
