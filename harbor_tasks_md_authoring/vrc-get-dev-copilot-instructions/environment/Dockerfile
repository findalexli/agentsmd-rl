FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && apt-get install -y --no-install-recommends \
    git ca-certificates curl \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir pytest==8.3.4 pyyaml==6.0.2

WORKDIR /workspace
RUN git init /workspace/vrc-get && \
    cd /workspace/vrc-get && \
    git remote add origin https://github.com/vrc-get/vrc-get.git && \
    git fetch --depth=1 origin a29a9bc9e23b08e772cd7ec4f26dddfb9b8b0933 && \
    git checkout FETCH_HEAD

RUN mkdir -p /logs/verifier

WORKDIR /workspace/vrc-get
