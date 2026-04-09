FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        git curl ca-certificates build-essential tmux && \
    rm -rf /var/lib/apt/lists/*

# apache/beam is huge — use git init + sparse checkout to fetch only the ratelimiter dir
RUN git init /workspace/beam && \
    cd /workspace/beam && \
    git remote add origin https://github.com/apache/beam.git && \
    git fetch --depth=1 origin 67c3183913af13afa3c98d219f8882e278cdea0b && \
    git checkout FETCH_HEAD && \
    git config user.email "agent@test" && \
    git config user.name "Agent"

WORKDIR /workspace/beam

# Verifier output directory (Harbor bind-mounts this)
RUN mkdir -p /logs/verifier
