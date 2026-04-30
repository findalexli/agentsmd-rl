FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && apt-get install -y --no-install-recommends \
    git ca-certificates curl \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir pytest==8.3.4 pyyaml==6.0.2

WORKDIR /workspace
RUN git init /workspace/datastoria && \
    cd /workspace/datastoria && \
    git remote add origin https://github.com/FrankChen021/datastoria.git && \
    git fetch --depth=1 origin e1de08aa94eb0f612387622c849c76e53de5f849 && \
    git checkout FETCH_HEAD

RUN mkdir -p /logs/verifier

WORKDIR /workspace/datastoria
