FROM node:22-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8
ENV LC_ALL=C.UTF-8

RUN apt-get update && apt-get install -y --no-install-recommends \
    git curl ca-certificates build-essential tmux python3 \
    && rm -rf /var/lib/apt/lists/*

RUN mkdir -p /workspace /logs/verifier

RUN git config --global user.email "agent@test.com" && \
    git config --global user.name "Test Agent"

WORKDIR /workspace

# Base commit: parent of merge commit b07aa7d6
ENV BASE_COMMIT=2dd9b7cf76c31df5d7e26e5199e3c362c3e94f95

# Clone React repo at base commit (sanitized snapshot)
RUN git clone --depth=1 --filter=blob:none https://github.com/facebook/react.git /workspace/react && \
    cd /workspace/react && \
    git fetch --depth=1 origin ${BASE_COMMIT} && \
    git checkout ${BASE_COMMIT} && \
    rm -rf .git && \
    git init && \
    git add -A && \
    git commit -m "snapshot"

# Install minimal dependencies (jest + needed React deps for testing)
RUN cd /workspace/react && \
    yarn install --frozen-lockfile 2>/dev/null || npm install 2>/dev/null || true

ENV NODE_ENV=development

WORKDIR /workspace/react
