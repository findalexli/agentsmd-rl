FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && apt-get install -y --no-install-recommends \
    git ca-certificates curl \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir pytest==8.3.4 pyyaml==6.0.2

WORKDIR /workspace
RUN git init /workspace/mermaid.ink && \
    cd /workspace/mermaid.ink && \
    git remote add origin https://github.com/jihchi/mermaid.ink.git && \
    git fetch --depth=1 origin 700551ceec1c3959ce955d40638b51b4e092e2f9 && \
    git checkout FETCH_HEAD

RUN mkdir -p /logs/verifier

WORKDIR /workspace/mermaid.ink
