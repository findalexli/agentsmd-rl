FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        git curl ca-certificates bash && \
    rm -rf /var/lib/apt/lists/*

# Clone repo at base commit (pre-plugin state)
RUN git init /workspace/claude-code && \
    cd /workspace/claude-code && \
    git remote add origin https://github.com/anthropics/claude-code.git && \
    git fetch --depth=1 origin 4dc23d0275ff615ba1dccbdd76ad2b12a3ede591 && \
    git checkout FETCH_HEAD \
    git config user.email "agent@test" && \
    git config user.name "Agent"

WORKDIR /workspace/claude-code

# Verifier output directory (Harbor bind-mounts this)
RUN mkdir -p /logs/verifier
