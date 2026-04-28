FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && apt-get install -y --no-install-recommends \
    git ca-certificates curl \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir pytest==8.3.4 pyyaml==6.0.2

WORKDIR /workspace
RUN git init /workspace/lynx-website && \
    cd /workspace/lynx-website && \
    git remote add origin https://github.com/lynx-family/lynx-website.git && \
    git fetch --depth=1 origin 8ea8e3e45bfd666f2a58567e2459bf8286ed3e9c && \
    git checkout FETCH_HEAD

RUN mkdir -p /logs/verifier

WORKDIR /workspace/lynx-website
