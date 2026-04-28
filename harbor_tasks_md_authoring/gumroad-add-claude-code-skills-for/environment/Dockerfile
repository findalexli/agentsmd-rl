FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && apt-get install -y --no-install-recommends \
    git ca-certificates curl \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir pytest==8.3.4 pyyaml==6.0.2

WORKDIR /workspace
RUN git init /workspace/gumroad && \
    cd /workspace/gumroad && \
    git remote add origin https://github.com/antiwork/gumroad.git && \
    git fetch --depth=1 origin 5dd3f2cb254a62ad83dc7d7d0b572838e0cde13e && \
    git checkout FETCH_HEAD

RUN mkdir -p /logs/verifier

WORKDIR /workspace/gumroad
