FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        git curl ca-certificates tmux && \
    rm -rf /var/lib/apt/lists/*

# Shallow-clone only the examples/with-docker* directories (next.js is huge)
RUN git init /workspace/next.js && \
    cd /workspace/next.js && \
    git remote add origin https://github.com/vercel/next.js.git && \
    git config core.sparseCheckout true && \
    echo "examples/with-docker/" >> .git/info/sparse-checkout && \
    echo "examples/with-docker-export-output/" >> .git/info/sparse-checkout && \
    echo "CLAUDE.md" >> .git/info/sparse-checkout && \
    echo "AGENTS.md" >> .git/info/sparse-checkout && \
    git fetch --depth=1 origin 15fcfb9ce4ec73c6ff8d08d72201726b983127fa && \
    git checkout FETCH_HEAD && \
    git config user.email "agent@test" && \
    git config user.name "Agent"

WORKDIR /workspace/next.js

# Verifier output directory (Harbor bind-mounts this)
RUN mkdir -p /logs/verifier
