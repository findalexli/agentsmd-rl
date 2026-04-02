FROM node:22-slim

RUN apt-get update && apt-get install -y \
    git \
    curl \
    ca-certificates \
    build-essential \
    python3 \
    python3-pip \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /workspace

# Clone React at the pre-fix commit (parent of merge commit)
ENV BASE_COMMIT=8f4150605449efe909822d8b20fe529d85851afe
RUN git clone --filter=blob:none --no-checkout https://github.com/facebook/react.git react \
    && cd react \
    && git fetch --depth=1 origin $BASE_COMMIT \
    && git checkout $BASE_COMMIT \
    && rm -rf .git \
    && git init \
    && git add -A \
    && git commit -m "snapshot"

WORKDIR /workspace/react

# Install dependencies (React uses yarn)
RUN npm install -g yarn

# Install minimal dependencies for testing
# Note: Running the full test suite requires extensive setup, we'll use a simpler approach
RUN yarn install --frozen-lockfile || yarn install

# Configure git user for any potential git operations
RUN git config user.email "agent@example.com" && git config user.name "Agent"

# Set environment for Node
ENV NODE_OPTIONS="--max-old-space-size=4096"

# Pre-logs directory
RUN mkdir -p /logs/verifier
