FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && apt-get install -y --no-install-recommends \
    git ca-certificates curl \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir pytest==8.3.4 pyyaml==6.0.2

WORKDIR /workspace
RUN git init /workspace/client-sdk-android && \
    cd /workspace/client-sdk-android && \
    git remote add origin https://github.com/livekit/client-sdk-android.git && \
    git fetch --depth=1 origin 8e5897e74a2a314cb516d0a9e77db7972d9c440a && \
    git checkout FETCH_HEAD

RUN mkdir -p /logs/verifier

WORKDIR /workspace/client-sdk-android
