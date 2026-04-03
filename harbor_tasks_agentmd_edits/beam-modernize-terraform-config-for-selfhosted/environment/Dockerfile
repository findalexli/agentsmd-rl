FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        git curl ca-certificates build-essential tmux && \
    rm -rf /var/lib/apt/lists/*

# Sparse checkout: only .github/gh-actions-self-hosted-runners/arc/ (full repo is ~8 GB)
RUN mkdir -p /workspace/beam && cd /workspace/beam && \
    git init && \
    git remote add origin https://github.com/apache/beam.git && \
    git sparse-checkout init && \
    git sparse-checkout set .github/gh-actions-self-hosted-runners/arc/ && \
    git fetch --depth=1 origin afbbf5355303b60da4cb19085dc2970a7c9f72b1 && \
    git checkout afbbf5355303b60da4cb19085dc2970a7c9f72b1 && \
    git config user.email "agent@test" && \
    git config user.name "Agent"

WORKDIR /workspace/beam

# Install python-hcl2 for HCL parsing in tests
RUN pip install --no-cache-dir python-hcl2

# Verifier output directory (Harbor bind-mounts this)
RUN mkdir -p /logs/verifier
