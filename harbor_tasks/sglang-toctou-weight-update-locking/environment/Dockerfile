FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        git curl ca-certificates build-essential && \
    rm -rf /var/lib/apt/lists/*

# Clone sglang at base commit (shallow clone for faster setup)
RUN git clone --depth=100 https://github.com/sgl-project/sglang.git /workspace/sglang && \
    cd /workspace/sglang && \
    git checkout eca62ab8f48359bfc8d1602c36aa88f7ba84a46c && \
    git config user.email "agent@test" && \
    git config user.name "Agent"

WORKDIR /workspace/sglang

# Verifier output directory (Harbor bind-mounts this)
RUN mkdir -p /logs/verifier
