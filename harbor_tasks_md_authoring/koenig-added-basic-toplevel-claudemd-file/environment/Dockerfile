FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && apt-get install -y --no-install-recommends \
    git ca-certificates curl \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir pytest==8.3.4 pyyaml==6.0.2

WORKDIR /workspace
RUN git init /workspace/koenig && \
    cd /workspace/koenig && \
    git remote add origin https://github.com/TryGhost/Koenig.git && \
    git fetch --depth=1 origin b90e19a4a7b9aeb79adee4bb6caa66affc7d752a && \
    git checkout FETCH_HEAD

RUN mkdir -p /logs/verifier

WORKDIR /workspace/koenig
