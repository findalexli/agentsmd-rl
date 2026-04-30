FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && apt-get install -y --no-install-recommends \
    git ca-certificates curl \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir pytest==8.3.4 pyyaml==6.0.2

WORKDIR /workspace
RUN git init /workspace/byterover-cli && \
    cd /workspace/byterover-cli && \
    git remote add origin https://github.com/campfirein/byterover-cli.git && \
    git fetch --depth=1 origin db60441c74df0a87e00058ec435e9202b855f3c3 && \
    git checkout FETCH_HEAD

RUN mkdir -p /logs/verifier

WORKDIR /workspace/byterover-cli
