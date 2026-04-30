FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && apt-get install -y --no-install-recommends \
    git ca-certificates curl \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir pytest==8.3.4 pyyaml==6.0.2

WORKDIR /workspace
RUN git init /workspace/mirascope && \
    cd /workspace/mirascope && \
    git remote add origin https://github.com/Mirascope/mirascope.git && \
    git fetch --depth=1 origin 93f4b8e62ca9539a2c77c642bf84180a4e5c4cc7 && \
    git checkout FETCH_HEAD

RUN mkdir -p /logs/verifier

WORKDIR /workspace/mirascope
