FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && apt-get install -y --no-install-recommends \
    git ca-certificates curl \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir pytest==8.3.4 pyyaml==6.0.2

WORKDIR /workspace
RUN git init /workspace/slack-gamebot && \
    cd /workspace/slack-gamebot && \
    git remote add origin https://github.com/dblock/slack-gamebot.git && \
    git fetch --depth=1 origin 23c0bcabec984ccc1f0229fd643b5581a9788dc2 && \
    git checkout FETCH_HEAD

RUN mkdir -p /logs/verifier

WORKDIR /workspace/slack-gamebot
