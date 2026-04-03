FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        git curl ca-certificates build-essential tmux && \
    rm -rf /var/lib/apt/lists/*

# workerd is a large monorepo — use git init + fetch --depth=1
RUN git init /workspace/workerd && \
    cd /workspace/workerd && \
    git remote add origin https://github.com/cloudflare/workerd.git && \
    git fetch --depth=1 origin dce7afd9ef1c45cd56bda8ac393358d381e41dd5 && \
    git checkout dce7afd9ef1c45cd56bda8ac393358d381e41dd5 && \
    git config user.email "agent@test" && \
    git config user.name "Agent"

WORKDIR /workspace/workerd

# No compilation deps needed — tests are content-based checks on Rust/Markdown sources

# Verifier output directory (Harbor bind-mounts this)
RUN mkdir -p /logs/verifier
