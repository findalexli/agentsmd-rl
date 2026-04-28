FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && apt-get install -y --no-install-recommends \
    git ca-certificates curl \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir pytest==8.3.4 pyyaml==6.0.2

WORKDIR /workspace
RUN git init /workspace/thetagang && \
    cd /workspace/thetagang && \
    git remote add origin https://github.com/brndnmtthws/thetagang.git && \
    git fetch --depth=1 origin 33522af4d5a3cd45f2f8915fd58146e0265d4c87 && \
    git checkout FETCH_HEAD

RUN mkdir -p /logs/verifier

WORKDIR /workspace/thetagang
