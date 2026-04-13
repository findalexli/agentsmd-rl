FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        git curl ca-certificates nodejs && \
    rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir pytest pytest-json-ctrf

RUN git clone --filter=blob:none https://github.com/BerriAI/litellm.git /workspace/litellm && \
    cd /workspace/litellm && \
    git checkout a38993b871a32090caea0941427a8bc5489a5c02 && \
    git config user.email "agent@test" && \
    git config user.name "Agent"

WORKDIR /workspace/litellm

RUN mkdir -p /logs/verifier


