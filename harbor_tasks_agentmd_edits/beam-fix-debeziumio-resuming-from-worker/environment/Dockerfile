FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        git curl ca-certificates build-essential tmux && \
    rm -rf /var/lib/apt/lists/*

# Apache Beam is a large monorepo — shallow clone with blob filter
RUN git init /workspace/beam && \
    cd /workspace/beam && \
    git remote add origin https://github.com/apache/beam.git && \
    git fetch --depth=1 origin 06dd48e9313ca81d8d0739b03d0850f129c08e56 && \
    git checkout FETCH_HEAD && \
    git config user.email "agent@test" && \
    git config user.name "Agent"

WORKDIR /workspace/beam

# No special Python deps needed — tests do source inspection of Java files
# Verifier output directory (Harbor bind-mounts this)
RUN mkdir -p /logs/verifier
