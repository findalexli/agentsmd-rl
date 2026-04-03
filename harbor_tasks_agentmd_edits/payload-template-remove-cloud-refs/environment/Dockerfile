FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        git curl ca-certificates build-essential tmux && \
    rm -rf /var/lib/apt/lists/*

# Clone repo at base commit
RUN git clone --filter=blob:none https://github.com/payloadcms/payload.git /workspace/payload && \
    cd /workspace/payload && \
    git checkout 39bead7e4c6c05644ad9987a6224fb8de34928de && \
    git config user.email "agent@test" && \
    git config user.name "Agent"

WORKDIR /workspace/payload

# No deps needed — tests only read file contents
RUN mkdir -p /logs/verifier
