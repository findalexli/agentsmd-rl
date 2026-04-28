FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && apt-get install -y --no-install-recommends \
    git ca-certificates curl \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir pytest==8.3.4 pyyaml==6.0.2

WORKDIR /workspace
RUN git init /workspace/stream-chat-swiftui && \
    cd /workspace/stream-chat-swiftui && \
    git remote add origin https://github.com/GetStream/stream-chat-swiftui.git && \
    git fetch --depth=1 origin 83885f1cbe0e0c80511903834b4cdd0d412ba89f && \
    git checkout FETCH_HEAD

RUN mkdir -p /logs/verifier

WORKDIR /workspace/stream-chat-swiftui
