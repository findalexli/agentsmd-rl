FROM node:22-slim

RUN apt-get update && apt-get install -y \
    git \
    curl \
    ca-certificates \
    build-essential \
    python3 \
    && rm -rf /var/lib/apt/lists/*

# Configure git user for snapshot
RUN git config --global user.email "agent@example.com" && \
    git config --global user.name "Agent"

WORKDIR /workspace

# Base commit (parent of merge commit)
ENV BASE_COMMIT=03ca38e6e7b84cf20438c1d333636b3d662ca726

# Clone React repo and checkout base commit
RUN git clone --depth 1 https://github.com/facebook/react.git react && \
    cd react && \
    git fetch --depth 1 origin ${BASE_COMMIT} && \
    git checkout ${BASE_COMMIT}

# Sanitize snapshot: remove .git history and re-init
RUN cd react && \
    rm -rf .git && \
    git init && \
    git add -A && \
    git commit -m "snapshot"

# Install minimal dependencies for eslint-plugin-react-hooks tests
WORKDIR /workspace/react
RUN yarn install --frozen-lockfile --prefer-offline 2>&1 | tail -20 || true

# Ensure logging directory exists
RUN mkdir -p /logs/verifier

WORKDIR /workspace/react
