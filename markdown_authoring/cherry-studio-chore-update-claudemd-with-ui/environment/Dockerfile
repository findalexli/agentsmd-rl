FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && apt-get install -y --no-install-recommends \
    git ca-certificates curl \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir pytest==8.3.4 pyyaml==6.0.2

WORKDIR /workspace
RUN git init /workspace/cherry-studio && \
    cd /workspace/cherry-studio && \
    git remote add origin https://github.com/CherryHQ/cherry-studio.git && \
    git fetch --depth=1 origin 95f6e4dd3b93082e29b7aa9b2669cecf35211595 && \
    git checkout FETCH_HEAD

RUN mkdir -p /logs/verifier

WORKDIR /workspace/cherry-studio
