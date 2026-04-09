FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        git curl ca-certificates build-essential tmux gcc && \
    rm -rf /var/lib/apt/lists/*

# Clone bun at the base commit (BEFORE the fix)
RUN git init /workspace/bun && \
    cd /workspace/bun && \
    git remote add origin https://github.com/oven-sh/bun.git && \
    git fetch --depth=1 origin 159a285841539c8f166509116c12b11e15b47fdf && \
    git checkout FETCH_HEAD && \
    git config user.email "agent@test" && \
    git config user.name "Agent"

RUN mkdir -p /logs/verifier

WORKDIR /workspace/bun
