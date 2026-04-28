FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && apt-get install -y --no-install-recommends \
    git ca-certificates curl \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir pytest==8.3.4 pyyaml==6.0.2

WORKDIR /workspace
RUN git init /workspace/huggingface-hub && \
    cd /workspace/huggingface-hub && \
    git remote add origin https://github.com/huggingface/huggingface_hub.git && \
    git fetch --depth=1 origin b3a8eb58e4931bd6124e684fe1c4cf6cc1209b5a && \
    git checkout FETCH_HEAD

RUN mkdir -p /logs/verifier

WORKDIR /workspace/huggingface-hub
