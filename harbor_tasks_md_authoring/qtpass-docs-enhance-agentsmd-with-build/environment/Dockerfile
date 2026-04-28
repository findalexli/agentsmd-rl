FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && apt-get install -y --no-install-recommends \
    git ca-certificates curl \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir pytest==8.3.4 pyyaml==6.0.2

WORKDIR /workspace
RUN git init /workspace/qtpass && \
    cd /workspace/qtpass && \
    git remote add origin https://github.com/IJHack/QtPass.git && \
    git fetch --depth=1 origin d0684a5f105d08f4bafcf736dc5e65f2d07a4c74 && \
    git checkout FETCH_HEAD

RUN mkdir -p /logs/verifier

WORKDIR /workspace/qtpass
