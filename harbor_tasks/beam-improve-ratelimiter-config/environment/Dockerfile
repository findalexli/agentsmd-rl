FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        git curl ca-certificates tmux && \
    rm -rf /var/lib/apt/lists/*

# Apache Beam is a large monorepo — shallow clone the specific commit
RUN git init /workspace/beam && \
    cd /workspace/beam && \
    git remote add origin https://github.com/apache/beam.git && \
    git fetch --depth=1 origin bab2374552da7a1f7fbe783408c3b4159e3f0391 && \
    git checkout FETCH_HEAD && \
    git config user.email "agent@test" && \
    git config user.name "Agent"

WORKDIR /workspace/beam

# No extra deps needed — tests only read .tf and .md files
RUN mkdir -p /logs/verifier
