FROM node:22-slim

# Install Python for test runner
ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        python3 python3-pip git curl ca-certificates && \
    rm -rf /var/lib/apt/lists/*

# Create python symlink for convenience
RUN ln -sf /usr/bin/python3 /usr/bin/python

# Clone repo at base commit (use --depth for faster clone)
RUN git init /workspace/next.js && \
    cd /workspace/next.js && \
    git remote add origin https://github.com/vercel/next.js.git && \
    git fetch --depth=1 origin c5b19eb7f5cf48dffa1b8bf87cd089f079fb031a && \
    git checkout FETCH_HEAD && \
    git config user.email "agent@test" && \
    git config user.name "Agent"

WORKDIR /workspace/next.js

# Verifier output directory (Harbor bind-mounts this)
RUN mkdir -p /logs/verifier
