FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        git curl ca-certificates build-essential tmux && \
    rm -rf /var/lib/apt/lists/*

# Clone repo at base commit
RUN git clone --filter=blob:none https://github.com/THUDM/slime.git /workspace/slime && \
    cd /workspace/slime && \
    git checkout e4d22dc929169fcc2cdf538d1798d9a5473f4d1d && \
    git config user.email "agent@test" && \
    git config user.name "Agent"

WORKDIR /workspace/slime

# Verifier output directory (Harbor bind-mounts this)
RUN mkdir -p /logs/verifier
