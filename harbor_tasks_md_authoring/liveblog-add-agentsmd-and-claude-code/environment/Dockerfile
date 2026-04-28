FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && apt-get install -y --no-install-recommends \
    git ca-certificates curl \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir pytest==8.3.4 pyyaml==6.0.2

WORKDIR /workspace
RUN git init /workspace/liveblog && \
    cd /workspace/liveblog && \
    git remote add origin https://github.com/Automattic/liveblog.git && \
    git fetch --depth=1 origin 56f3a6023cc373af37b190fd9d0726c0e4857cf8 && \
    git checkout FETCH_HEAD

RUN mkdir -p /logs/verifier

WORKDIR /workspace/liveblog
