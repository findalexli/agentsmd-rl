FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && apt-get install -y --no-install-recommends \
    git ca-certificates curl \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir pytest==8.3.4 pyyaml==6.0.2

WORKDIR /workspace
RUN git init /workspace/bioruby && \
    cd /workspace/bioruby && \
    git remote add origin https://github.com/bioruby/bioruby.git && \
    git fetch --depth=1 origin 65a3e9ad1dcc05e095818b6d6462c142f84ec0cc && \
    git checkout FETCH_HEAD

RUN mkdir -p /logs/verifier

WORKDIR /workspace/bioruby
