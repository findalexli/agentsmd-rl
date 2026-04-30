FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && apt-get install -y --no-install-recommends \
    git ca-certificates curl \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir pytest==8.3.4 pyyaml==6.0.2

WORKDIR /workspace
RUN git init /workspace/anytype-swift && \
    cd /workspace/anytype-swift && \
    git remote add origin https://github.com/anyproto/anytype-swift.git && \
    git fetch --depth=1 origin 52de9beafa61c7ef694b909d6bdefbd2915c2d66 && \
    git checkout FETCH_HEAD

RUN mkdir -p /logs/verifier

WORKDIR /workspace/anytype-swift
