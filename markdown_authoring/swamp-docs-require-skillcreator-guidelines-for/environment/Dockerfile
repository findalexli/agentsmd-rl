FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && apt-get install -y --no-install-recommends \
    git ca-certificates curl \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir pytest==8.3.4 pyyaml==6.0.2

WORKDIR /workspace
RUN git init /workspace/swamp && \
    cd /workspace/swamp && \
    git remote add origin https://github.com/systeminit/swamp.git && \
    git fetch --depth=1 origin ef93e49991143f5044fcff6dfd7ba6fb64ccea6e && \
    git checkout FETCH_HEAD

RUN mkdir -p /logs/verifier

WORKDIR /workspace/swamp
