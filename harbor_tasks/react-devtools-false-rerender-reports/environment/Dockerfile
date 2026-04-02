FROM node:22-slim

# Install dependencies
RUN apt-get update && apt-get install -y \
    git \
    curl \
    ca-certificates \
    build-essential \
    python3 \
    && rm -rf /var/lib/apt-get

# Set workdir
WORKDIR /workspace

# Base commit (parent of merge commit)
ENV BASE_COMMIT=eab523e2a99583703b13536670dfdd8a3b1e26e0

# Clone React at base commit (shallow clone for speed)
RUN git clone --depth=100 https://github.com/facebook/react.git react && \
    cd react && \
    git fetch --depth=1 origin ${BASE_COMMIT} && \
    git checkout ${BASE_COMMIT}

WORKDIR /workspace/react

# The test file exists at packages/react-devtools-shared/src/__tests__/profilingCharts-test.js
# We need to install dependencies for react-devtools-shared
# React uses yarn workspaces - install top-level first

# Install dependencies
RUN yarn install --frozen-lockfile

# Build required packages (some tests need built artifacts)
RUN yarn build react-devtools-shared --type=NODE

# Configure git for any potential git operations
RUN git config --global user.email "agent@example.com" && \
    git config --global user.name "Agent"

# Create test directories
RUN mkdir -p /logs/verifier

# Set environment
ENV NODE_ENV=test
ENV CI=true

WORKDIR /workspace/react/packages/react-devtools-shared
