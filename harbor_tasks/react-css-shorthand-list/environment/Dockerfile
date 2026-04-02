FROM node:22-slim

RUN apt-get update && apt-get install -y \
    git \
    curl \
    ca-certificates \
    python3 \
    python3-pip \
    && rm -rf /var/lib/apt/lists/*

# Create workspace
WORKDIR /workspace/react

# Clone repo at base commit
RUN git clone --depth=1 https://github.com/facebook/react.git . \
    && git fetch --depth=1 origin 12ba7d81297abac61012a36f20d4a9d22b9210d9 \
    && git checkout 12ba7d81297abac61012a36f20d4a9d22b9210d9 \
    && rm -rf .git \
    && git init \
    && git add -A \
    && git commit -m "snapshot"

# Install minimal dependencies (Jest + React testing only)
RUN yarn install --frozen-lockfile --network-timeout 100000 2>&1 | tail -20 || true

# Configure git user (for solve.sh)
RUN git config --global user.email "agent@example.com" \
    && git config --global user.name "Agent"

# Create logs directory
RUN mkdir -p /logs/verifier

# Set up environment
ENV NODE_ENV=development
ENV CI=true
