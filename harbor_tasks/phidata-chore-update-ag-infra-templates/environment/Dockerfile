FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        git curl ca-certificates build-essential tmux && \
    rm -rf /var/lib/apt/lists/*

# Clone repo at base commit
RUN git clone --filter=blob:none https://github.com/phidatahq/phidata.git /workspace/phidata && \
    cd /workspace/phidata && \
    git checkout 156d4e43e6281d0ff65a2351379df732348ffadc && \
    git config user.email "agent@test" && \
    git config user.name "Agent"

WORKDIR /workspace/phidata

# Verifier output directory (Harbor bind-mounts this)
RUN mkdir -p /logs/verifier
