FROM node:22-slim

RUN rm -rf /var/lib/apt/lists/* && apt-get update && \
    apt-get install -y --no-install-recommends \
        git curl ca-certificates build-essential tmux python3 && \
    rm -rf /var/lib/apt/lists/*

# Clone bun at the base commit (BEFORE the fix)
RUN git init /workspace/bun && \
    cd /workspace/bun && \
    git remote add origin https://github.com/oven-sh/bun.git && \
    git fetch --depth=1 origin 0de7a806d108a56a2c9f87d5974c52384059c397 && \
    git checkout FETCH_HEAD

RUN mkdir -p /logs/verifier

# Install bun v1.2.0 binary for behavioral tests
RUN apt-get update -qq && apt-get install -y -qq unzip >/dev/null 2>&1 || true && \
    curl -fsSL https://github.com/oven-sh/bun/releases/download/bun-v1.2.0/bun-linux-x64.zip -o /tmp/bun.zip && \
    unzip -o /tmp/bun.zip -d /tmp/ && \
    chmod +x /tmp/bun-linux-x64/bun && \
    mkdir -p /workspace/bun/tmp && \
    cp /tmp/bun-linux-x64/bun /workspace/bun/tmp/bun && \
    rm /tmp/bun.zip && rm -rf /tmp/bun-linux-x64

WORKDIR /workspace/bun
