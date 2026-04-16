FROM python:3.12-slim

# Install git, curl, basic utilities, and Node.js 22
RUN apt-get update && apt-get install -y --no-install-recommends \
    git \
    curl \
    ca-certificates \
    gnupg \
    && rm -rf /var/lib/apt/lists/*

# Install Node.js 22 from NodeSource
RUN curl -fsSL https://deb.nodesource.com/setup_22.x | bash - \
    && apt-get install -y --no-install-recommends nodejs \
    && rm -rf /var/lib/apt/lists/*

# Set up workspace
WORKDIR /workspace

# Clone the payload repository at the base commit (before the fix)
# Using --filter=blob:none for partial clone
RUN git clone --filter=blob:none https://github.com/payloadcms/payload.git
WORKDIR /workspace/payload
RUN git checkout fac59c85155f01d1ef7e9aaeddf3362631ab3419

# Install pnpm globally
RUN npm install -g pnpm@10.27.0

# Install Payload dependencies
RUN pnpm install --frozen-lockfile

# Build only the UI package (needed for clipboard action tests)
# Increased Node.js memory for TypeScript compilation
RUN NODE_OPTIONS="--max-old-space-size=4096" pnpm run build:ui

# Create logs directory
RUN mkdir -p /logs/verifier

WORKDIR /workspace