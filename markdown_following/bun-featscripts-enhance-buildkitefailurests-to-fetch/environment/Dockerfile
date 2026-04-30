FROM node:22-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        git curl ca-certificates unzip python3 python3-pip && \
    rm -rf /var/lib/apt/lists/*

# Install bun (needed to run and test the TypeScript script)
# Pin to a specific version to avoid floating-latest breakage
ENV BUN_VERSION=bun-v1.2.9
RUN curl -fsSL https://bun.sh/install | bash -s -- "$BUN_VERSION"
ENV BUN_INSTALL="/root/.bun"
ENV PATH="$BUN_INSTALL/bin:$PATH"

# Clone repo at base commit (shallow — bun is a very large repo)
RUN git init /workspace/bun && \
    cd /workspace/bun && \
    git remote add origin https://github.com/oven-sh/bun.git && \
    git fetch origin 6f6f76f0c07d592ad14b1d64a2e7037deb587c21 --depth=1 && \
    git checkout FETCH_HEAD && \
    git config user.email "agent@test" && \
    git config user.name "Agent"

WORKDIR /workspace/bun

# Verifier output directory (Harbor bind-mounts this)
RUN mkdir -p /logs/verifier
