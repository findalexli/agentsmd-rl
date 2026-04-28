FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && apt-get install -y --no-install-recommends \
    git ca-certificates curl \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir pytest==8.3.4 pyyaml==6.0.2

WORKDIR /workspace
RUN git init /workspace/stream-chat-android && \
    cd /workspace/stream-chat-android && \
    git remote add origin https://github.com/GetStream/stream-chat-android.git && \
    git fetch --depth=1 origin 9b8c0a1feb58f162d5da3a3c22c14fef70e9e3eb && \
    git checkout FETCH_HEAD

RUN mkdir -p /logs/verifier

WORKDIR /workspace/stream-chat-android
