FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        git curl ca-certificates build-essential tmux && \
    rm -rf /var/lib/apt/lists/*

# Clone repo at base commit (shallow — large repo, only need source files)
RUN git clone --filter=blob:none https://github.com/vllm-project/vllm.git /workspace/vllm && \
    cd /workspace/vllm && \
    git checkout 731055548262317579c35189a46cde6932fcc376 && \
    git config user.email "agent@test" && \
    git config user.name "Agent"

WORKDIR /workspace/vllm

# No heavy deps needed — tests are AST/source analysis (GPU code, can't import)

# Verifier output directory (Harbor bind-mounts this)
RUN mkdir -p /logs/verifier
