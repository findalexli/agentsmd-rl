FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && apt-get install -y --no-install-recommends \
    git ca-certificates curl \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir pytest==8.3.4 pyyaml==6.0.2

WORKDIR /workspace
RUN git init /workspace/sourcify && \
    cd /workspace/sourcify && \
    git remote add origin https://github.com/argotorg/sourcify.git && \
    git fetch --depth=1 origin 3fa502302ac920d680d334a6a564d7e06d2ba9ad && \
    git checkout FETCH_HEAD

RUN mkdir -p /logs/verifier

WORKDIR /workspace/sourcify
