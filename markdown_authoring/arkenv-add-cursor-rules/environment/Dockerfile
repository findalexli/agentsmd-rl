FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && apt-get install -y --no-install-recommends \
    git ca-certificates curl \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir pytest==8.3.4 pyyaml==6.0.2

WORKDIR /workspace
RUN git init /workspace/arkenv && \
    cd /workspace/arkenv && \
    git remote add origin https://github.com/yamcodes/arkenv.git && \
    git fetch --depth=1 origin f1f3c5e1e65a727bbf46387b8b3e5ee9cc502a9e && \
    git checkout FETCH_HEAD

RUN mkdir -p /logs/verifier

WORKDIR /workspace/arkenv
