FROM golang:1.25-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        git curl ca-certificates python3 python3-pip python3-venv && \
    rm -rf /var/lib/apt/lists/*

RUN git clone --filter=blob:none https://github.com/docker/compose.git /workspace/compose && \
    cd /workspace/compose && \
    git checkout 27d9d506306e808965d99b70c1f59308dcabca13 && \
    git config user.email "agent@test" && \
    git config user.name "Agent"

WORKDIR /workspace/compose

RUN mkdir -p /logs/verifier
