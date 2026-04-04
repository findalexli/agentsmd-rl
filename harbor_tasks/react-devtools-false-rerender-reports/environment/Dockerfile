FROM node:22-slim

# Install dependencies
RUN apt-get update && apt-get install -y \
    git \
    curl \
    ca-certificates \
    build-essential \
    python3 \
    python3-pip \
    && rm -rf /var/lib/apt/lists/*

# Pre-install pytest so test.sh doesn't need to install at runtime
RUN pip3 install --break-system-packages pytest pytest-json-ctrf

# Set workdir
WORKDIR /workspace

# Base commit
ENV BASE_COMMIT=eab523e2a99583703b13536670dfdd8a3b1e26e0

# Clone React at base commit (shallow clone for speed)
RUN git init react && \
    cd react && \
    git remote add origin https://github.com/facebook/react.git && \
    git fetch --depth=1 origin ${BASE_COMMIT} && \
    git checkout FETCH_HEAD

WORKDIR /workspace/react

# Install dependencies (React uses yarn workspaces)
RUN yarn install --frozen-lockfile

# Configure git for any potential git operations
RUN git config --global user.email "agent@example.com" && \
    git config --global user.name "Agent"

# Create test directories
RUN mkdir -p /logs/verifier

# Set environment
ENV NODE_ENV=development
ENV CI=true

WORKDIR /workspace/react/packages/react-devtools-shared
