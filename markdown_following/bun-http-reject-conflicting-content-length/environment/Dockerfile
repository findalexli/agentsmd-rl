FROM node:22-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        git curl ca-certificates build-essential tmux python3 python3-pip unzip && \
    rm -rf /var/lib/apt/lists/*

# Install bun v1.3.13 (pinned — includes the HTTP parser Content-Length fix)
RUN curl -fsSL https://bun.sh/install | bash -s "bun-v1.3.13"
ENV PATH="/root/.bun/bin:$PATH"

# Clone repo at base commit
RUN git init /workspace/bun && \
    cd /workspace/bun && \
    git remote add origin https://github.com/oven-sh/bun.git && \
    git fetch --depth=1 origin 5b3ca83b84f90ccc9c71005db0ab9bd87850bc70 && \
    git checkout FETCH_HEAD && \
    git config user.email "agent@test" && \
    git config user.name "Agent"

WORKDIR /workspace/bun

# Verifier output directory (Harbor bind-mounts this)
RUN mkdir -p /logs/verifier
