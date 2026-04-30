FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && apt-get install -y --no-install-recommends \
    git ca-certificates curl \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir pytest==8.3.4 pyyaml==6.0.2

WORKDIR /workspace
RUN git init /workspace/stream-chat-js && \
    cd /workspace/stream-chat-js && \
    git remote add origin https://github.com/GetStream/stream-chat-js.git && \
    git fetch --depth=1 origin 663f5fbea2011177870a133e2771f0bb8eafd317 && \
    git checkout FETCH_HEAD

RUN mkdir -p /logs/verifier

WORKDIR /workspace/stream-chat-js
