FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        git curl ca-certificates build-essential tmux && \
    rm -rf /var/lib/apt/lists/*

# Clone repo at base commit (electric-sql/electric is a medium-sized repo)
RUN git clone --filter=blob:none https://github.com/electric-sql/electric.git /workspace/electric && \
    cd /workspace/electric && \
    git checkout 7ba32193cc9f970835acdcb2de48101f1a812ae9 && \
    git config user.email "agent@test" && \
    git config user.name "Agent"

WORKDIR /workspace/electric

# Install yamllint for YAML syntax validation in tests
RUN pip install --no-cache-dir yamllint

# Verifier output directory (Harbor bind-mounts this)
RUN mkdir -p /logs/verifier
