FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        git curl ca-certificates build-essential && \
    rm -rf /var/lib/apt/lists/*

# Clone sglang repo at base commit
ARG BASE_COMMIT=73fc87a74f5e6e2974403d95292dca9bb387b288
RUN git clone --filter=blob:none https://github.com/sgl-project/sglang.git /workspace/sglang && \
    cd /workspace/sglang && \
    git checkout ${BASE_COMMIT} && \
    git config user.email "agent@test" && \
    git config user.name "Agent"

WORKDIR /workspace/sglang

# Install minimal deps needed for test analysis (requests, pytest)
RUN pip install --no-cache-dir pytest requests

# Verifier output directory
RUN mkdir -p /logs/verifier
