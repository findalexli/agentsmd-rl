FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        git curl ca-certificates build-essential tmux && \
    rm -rf /var/lib/apt/lists/*

# vllm is large; shallow clone then fetch the specific base commit
RUN git clone --depth=1 --filter=blob:none https://github.com/vllm-project/vllm.git /workspace/vllm && \
    cd /workspace/vllm && \
    git fetch --depth=1 origin 81994e1d0ea6e0486cfbdad02e00942614c55264 && \
    git checkout 81994e1d0ea6e0486cfbdad02e00942614c55264 && \
    git config user.email "agent@test" && \
    git config user.name "Agent"

WORKDIR /workspace/vllm

# No Python deps needed — tests only read CUDA source files
# Verifier output directory (Harbor bind-mounts this)
RUN mkdir -p /logs/verifier
