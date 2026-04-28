FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && apt-get install -y --no-install-recommends \
    git ca-certificates curl \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir pytest==8.3.4 pyyaml==6.0.2

WORKDIR /workspace
RUN git init /workspace/quickadd && \
    cd /workspace/quickadd && \
    git remote add origin https://github.com/chhoumann/quickadd.git && \
    git fetch --depth=1 origin 2811c5abb3f319008ec3c70ebf27fdef03e18b7f && \
    git checkout FETCH_HEAD

RUN mkdir -p /logs/verifier

WORKDIR /workspace/quickadd
