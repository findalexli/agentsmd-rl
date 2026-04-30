FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && apt-get install -y --no-install-recommends \
    git ca-certificates curl \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir pytest==8.3.4 pyyaml==6.0.2

WORKDIR /workspace
RUN git init /workspace/nemoclaw && \
    cd /workspace/nemoclaw && \
    git remote add origin https://github.com/NVIDIA/NemoClaw.git && \
    git fetch --depth=1 origin cd195099f765d7fcba569bce6c80d07a2a8c73cf && \
    git checkout FETCH_HEAD

RUN mkdir -p /logs/verifier

WORKDIR /workspace/nemoclaw
