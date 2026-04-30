FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && apt-get install -y --no-install-recommends \
    git ca-certificates curl \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir pytest==8.3.4 pyyaml==6.0.2

WORKDIR /workspace
RUN git init /workspace/stream-video-android && \
    cd /workspace/stream-video-android && \
    git remote add origin https://github.com/GetStream/stream-video-android.git && \
    git fetch --depth=1 origin 4296d8368eab3dba1c3daaf9e5c85762f9318bd1 && \
    git checkout FETCH_HEAD

RUN mkdir -p /logs/verifier

WORKDIR /workspace/stream-video-android
