FROM node:22-slim

# Install Python for pytest test runner, and patch for applying fixes
RUN apt-get update && apt-get install -y --no-install-recommends \
    python3 \
    python3-pip \
    git \
    patch \
    && rm -rf /var/lib/apt/lists/*

# Create logs directory for verifier
RUN mkdir -p /logs/verifier

WORKDIR /workspace

# Clone the repository at the base commit (before the fix)
RUN git clone --filter=blob:none https://github.com/TanStack/router.git router \
    && cd router \
    && git checkout cd7116b53b7ba3152129b5c656dfcaeb0d62c5b8

WORKDIR /workspace/router

# Install pnpm
RUN corepack enable && corepack prepare pnpm@latest --activate

# Install dependencies
RUN pnpm install --frozen-lockfile

CMD ["/bin/bash"]
