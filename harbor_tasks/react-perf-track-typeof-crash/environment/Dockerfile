FROM node:22-slim

# Install required tools and Python for scoring
RUN apt-get update && apt-get install -y \
    git \
    curl \
    ca-certificates \
    build-essential \
    python3 \
    python3-pip \
    && rm -rf /var/lib/apt/lists/*

# Set up workspace
WORKDIR /workspace

# Base commit (parent of merge commit)
ENV BASE_COMMIT=e32c1261219a9d665f392a4799b8a24ea326f1a1
ENV REPO_NAME=react

# Clone React repo at base commit
RUN git clone --depth 1 https://github.com/facebook/react.git && \
    cd react && \
    git fetch --depth=1 origin ${BASE_COMMIT} && \
    git checkout ${BASE_COMMIT}

# Install dependencies
WORKDIR /workspace/react
RUN yarn install

# Sanitize: remove .git and re-init for clean state
RUN rm -rf .git && \
    git init && \
    git add -A && \
    git commit -m "snapshot at base commit"

# Configure git
RUN git config --global user.email "agent@example.com" && \
    git config --global user.name "Agent"

# Set up Python environment
RUN python3 -m pip install pyyaml --break-system-packages

# Create verifier directory
RUN mkdir -p /logs/verifier

WORKDIR /workspace/react
