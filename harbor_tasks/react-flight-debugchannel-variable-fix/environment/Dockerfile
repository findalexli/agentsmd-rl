FROM node:22-slim

RUN apt-get update && apt-get install -y --no-install-recommends \
    git curl ca-certificates build-essential python3 \
    && rm -rf /var/lib/apt/lists/*

# Set up workspace
WORKDIR /workspace
RUN mkdir -p /logs/verifier

# Clone React at base commit (pre-fix)
ARG BASE_COMMIT=65db1000b944c8a07b5947c06b38eb8364dce4f2
RUN git clone --depth 1 https://github.com/facebook/react.git react-repo && \
    cd react-repo && \
    git fetch --depth=1 origin ${BASE_COMMIT} && \
    git checkout ${BASE_COMMIT} && \
    rm -rf .git && \
    git init && \
    git config user.email "test@example.com" && \
    git config user.name "Test" && \
    git add -A && \
    git commit -m "snapshot" && \
    git config --global --add safe.directory /workspace/react-repo

# Install dependencies (minimal for testing)
WORKDIR /workspace/react-repo
RUN yarn install --frozen-lockfile --silent 2>/dev/null || yarn install --silent

# Set up path for tests
ENV PATH="/workspace/react-repo/node_modules/.bin:${PATH}"
WORKDIR /workspace/react-repo
