FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && apt-get install -y --no-install-recommends \
    git ca-certificates curl \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir pytest==8.3.4 pyyaml==6.0.2

WORKDIR /workspace
RUN git init /workspace/youtrackdb && \
    cd /workspace/youtrackdb && \
    git remote add origin https://github.com/JetBrains/youtrackdb.git && \
    git fetch --depth=1 origin 13f7a70727de9bbefea65ddb37d4c14498743070 && \
    git checkout FETCH_HEAD

RUN mkdir -p /logs/verifier

WORKDIR /workspace/youtrackdb
