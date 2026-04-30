FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && apt-get install -y --no-install-recommends \
    git ca-certificates curl \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir pytest==8.3.4 pyyaml==6.0.2

WORKDIR /workspace
RUN git init /workspace/quickwit && \
    cd /workspace/quickwit && \
    git remote add origin https://github.com/quickwit-oss/quickwit.git && \
    git fetch --depth=1 origin f33ea1d343dbd5550107e078b46d845564092f9e && \
    git checkout FETCH_HEAD

RUN mkdir -p /logs/verifier

WORKDIR /workspace/quickwit
