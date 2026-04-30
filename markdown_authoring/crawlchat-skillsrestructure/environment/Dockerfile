FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && apt-get install -y --no-install-recommends \
    git ca-certificates curl \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir pytest==8.3.4 pyyaml==6.0.2

WORKDIR /workspace
RUN git init /workspace/crawlchat && \
    cd /workspace/crawlchat && \
    git remote add origin https://github.com/crawlchat/crawlchat.git && \
    git fetch --depth=1 origin 65aa9f5fd98556ac8b324d390b4915a4201dd5d8 && \
    git checkout FETCH_HEAD

RUN mkdir -p /logs/verifier

WORKDIR /workspace/crawlchat
