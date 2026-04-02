FROM node:22-slim

RUN apt-get update && apt-get install -y \
    git \
    curl \
    ca-certificates \
    build-essential \
    python3 \
    && rm -rf /var/lib/apt/lists/*

# Clone React repo at the pre-fix commit
WORKDIR /workspace
RUN git clone --filter=blob:none --depth=1000 https://github.com/facebook/react.git react

WORKDIR /workspace/react

# Checkout base commit and clean git history (sanitized snapshot)
RUN git fetch --depth=1 origin bb53387716e96912cbfb48d92655bc23882798ff && \
    git checkout bb53387716e96912cbfb48d92655bc23882798ff && \
    rm -rf .git && \
    git init && \
    git add -A && \
    git -c user.email="agent@example.com" -c user.name="Agent" commit -m "snapshot"

# Install minimal dependencies (just what's needed for testing)
RUN npm install --legacy-peer-deps 2>&1 || yarn install 2>&1 || true

# Configure git for any future operations
RUN git config --global user.email "agent@example.com" && \
    git config --global user.name "Agent"

# Create logs directory
RUN mkdir -p /logs/verifier

WORKDIR /workspace/react
