FROM node:22-slim

RUN apt-get update && apt-get install -y \
    git \
    curl \
    ca-certificates \
    build-essential \
    python3 \
    python3-pip \
    tmux \
    --no-install-recommends \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /workspace

# Clone React at the pre-fix commit and create snapshot
ARG REACT_COMMIT=90b2dd442cc05048b2a6ade5020c463ab0499eca
RUN git init react && cd react && \
    git remote add origin https://github.com/facebook/react.git && \
    git fetch --depth=1 origin ${REACT_COMMIT} && \
    git checkout FETCH_HEAD && \
    rm -rf .git && \
    git init && \
    git add -A && \
    git commit -m "snapshot"

WORKDIR /workspace/react

# Install dependencies (minimal - just what's needed for testing)
RUN yarn install --frozen-lockfile

# Configure git for any future operations
RUN git config --global user.email "agent@example.com" && \
    git config --global user.name "Agent"

# Create logs directory
RUN mkdir -p /logs/verifier

ENV NODE_ENV=development
ENV CI=true
