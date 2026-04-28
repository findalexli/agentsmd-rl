FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && apt-get install -y --no-install-recommends \
    git ca-certificates curl \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir pytest==8.3.4 pyyaml==6.0.2

WORKDIR /workspace
RUN git init /workspace/kleinanzeigen-bot && \
    cd /workspace/kleinanzeigen-bot && \
    git remote add origin https://github.com/Second-Hand-Friends/kleinanzeigen-bot.git && \
    git fetch --depth=1 origin d26f39de036fdade1b704e6daa65dd94af0c1e0d && \
    git checkout FETCH_HEAD

RUN mkdir -p /logs/verifier

WORKDIR /workspace/kleinanzeigen-bot
