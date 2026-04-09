FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        git curl ca-certificates build-essential && \
    rm -rf /var/lib/apt/lists/*

# Clone repo at base commit
RUN git clone --filter=blob:none https://github.com/huggingface/transformers.git /workspace/transformers && \
    cd /workspace/transformers && \
    git checkout d4895f0810fd57bf5ee8cf65c3fe20d2f622cd0a && \
    git config user.email "agent@test" && \
    git config user.name "Agent"

WORKDIR /workspace/transformers

# Install pytest for test runner
RUN pip install --no-cache-dir pytest

# Verifier output directory
RUN mkdir -p /logs/verifier
