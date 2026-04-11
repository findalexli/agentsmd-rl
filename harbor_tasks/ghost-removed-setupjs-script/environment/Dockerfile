FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        git curl ca-certificates tmux && \
    rm -rf /var/lib/apt/lists/*

# Ghost is huge — shallow clone only. We only need files, not build.
RUN git clone --depth=1 https://github.com/TryGhost/Ghost.git /workspace/Ghost && \
    cd /workspace/Ghost && \
    git fetch --depth=1 origin c1e86e6dd150e7ab1a226cfce8f73bc4ee441787 && \
    git checkout c1e86e6dd150e7ab1a226cfce8f73bc4ee441787 && \
    git config user.email "agent@test" && \
    git config user.name "Agent"

WORKDIR /workspace/Ghost

# Verifier output directory (Harbor bind-mounts this)
RUN mkdir -p /logs/verifier
