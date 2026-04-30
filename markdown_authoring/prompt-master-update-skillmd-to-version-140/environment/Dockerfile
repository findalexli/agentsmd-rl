FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && apt-get install -y --no-install-recommends \
    git ca-certificates curl \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir pytest==8.3.4 pyyaml==6.0.2

WORKDIR /workspace
RUN git init /workspace/prompt-master && \
    cd /workspace/prompt-master && \
    git remote add origin https://github.com/nidhinjs/prompt-master.git && \
    git fetch --depth=1 origin a49c039da712e49cebb65c60b7d168a10e252c90 && \
    git checkout FETCH_HEAD

RUN mkdir -p /logs/verifier

WORKDIR /workspace/prompt-master
