FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        git curl ca-certificates build-essential tmux && \
    rm -rf /var/lib/apt/lists/*

# Slate is a large JS monorepo — tests only read file contents, no Node needed
RUN git clone --filter=blob:none https://github.com/ianstormtaylor/slate.git /workspace/slate && \
    cd /workspace/slate && \
    git checkout 33e74a822b82c4b9ce1444f456c5343970441ccb && \
    git config user.email "agent@test" && \
    git config user.name "Agent"

WORKDIR /workspace/slate

# Verifier output directory (Harbor bind-mounts this)
RUN mkdir -p /logs/verifier
