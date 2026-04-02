FROM node:22-slim

RUN apt-get update && apt-get install -y \
    git curl ca-certificates build-essential python3 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /workspace/react

# Clone repo at base commit and sanitize
RUN git init && \
    git remote add origin https://github.com/facebook/react.git && \
    git fetch --depth=1 origin bd76b456c127222f59888953348d40cf8f03e3a0 && \
    git checkout FETCH_HEAD && \
    rm -rf .git && \
    git init && \
    git add -A && \
    git commit -m "snapshot"

# Install dependencies
RUN yarn install --frozen-lockfile --silent 2>&1 | tail -5

WORKDIR /workspace/react/packages/react-devtools-core
RUN yarn link
RUN yarn build

WORKDIR /workspace/react/packages/react-devtools
RUN yarn link react-devtools-core

WORKDIR /workspace/react

# Create verifier directory
RUN mkdir -p /logs/verifier

# Configure git
RUN git config --global user.email "agent@test.com" && \
    git config --global user.name "Test Agent"

# Set environment
ENV NODE_ENV=development
ENV PATH="/workspace/react/node_modules/.bin:${PATH}"
