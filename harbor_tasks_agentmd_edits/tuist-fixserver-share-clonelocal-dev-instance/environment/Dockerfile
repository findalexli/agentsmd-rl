FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        git curl ca-certificates build-essential tmux && \
    rm -rf /var/lib/apt/lists/*

# Shallow clone at base commit
RUN git init /workspace/tuist && \
    cd /workspace/tuist && \
    git remote add origin https://github.com/tuist/tuist.git && \
    git fetch --depth=1 origin 729c4d6361931ac3612f2440bb643e340fd9e5a2 && \
    git checkout FETCH_HEAD && \
    git config user.email "agent@test" && \
    git config user.name "Agent"

WORKDIR /workspace/tuist

# Verifier output directory
RUN mkdir -p /logs/verifier
