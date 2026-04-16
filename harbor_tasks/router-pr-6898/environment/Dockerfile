FROM node:22-slim

# Install Python for pytest runner
RUN apt-get update && apt-get install -y python3 python3-pip git && \
    rm -rf /var/lib/apt/lists/*

# Create logs directory
RUN mkdir -p /logs/verifier

WORKDIR /workspace

# Clone repository with blob filter for efficiency
RUN git clone --filter=blob:none https://github.com/TanStack/router.git router

WORKDIR /workspace/router

# Checkout the base commit (parent of merge commit)
RUN git checkout bb291c68aaf63cd57406f14d382abc4d1c5456f3

# Install pnpm
RUN npm install -g pnpm@9

# Install dependencies (needed for testing the script)
RUN pnpm install --frozen-lockfile || pnpm install
