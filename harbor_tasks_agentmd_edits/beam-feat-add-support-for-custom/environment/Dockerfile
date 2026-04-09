FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        git curl ca-certificates build-essential tmux && \
    rm -rf /var/lib/apt/lists/*

RUN mkdir -p /workspace /logs/verifier

# Shallow clone — beam is a large monorepo
RUN git init /workspace/beam && \
    cd /workspace/beam && \
    git remote add origin https://github.com/apache/beam.git && \
    git fetch --depth=1 origin be8dfed0530d9192454e410b7d5842651f35ffd6 && \
    git checkout FETCH_HEAD && \
    git config user.email "agent@test" && \
    git config user.name "Agent"

WORKDIR /workspace/beam
