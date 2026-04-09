FROM node:22-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        git ca-certificates && \
    rm -rf /var/lib/apt/lists/*

# Clone repo at base commit
RUN git clone --filter=blob:none https://github.com/facebook/react.git /workspace/react && \
    cd /workspace/react && \
    git checkout 74568e8627aa43469b74f2972f427a209639d0b6 && \
    git config user.email "agent@test" && \
    git config user.name "Agent"

# Install json5 in isolated test-deps directory for subprocess tests
RUN mkdir -p /opt/test-deps && cd /opt/test-deps && \
    npm init -y 2>/dev/null && npm install json5

WORKDIR /workspace/react

# Verifier output directory (Harbor bind-mounts this)
RUN mkdir -p /logs/verifier
