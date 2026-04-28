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
    git fetch --depth=1 origin 34938396d4d5e155c087df94e4dad4b58ff7d8db && \
    git checkout FETCH_HEAD

RUN mkdir -p /logs/verifier

WORKDIR /workspace/slack-gamebot
