FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && apt-get install -y --no-install-recommends \
    git ca-certificates curl \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir pytest==8.3.4 pyyaml==6.0.2

WORKDIR /workspace
RUN git init /workspace/marvin && \
    cd /workspace/marvin && \
    git remote add origin https://github.com/PrefectHQ/marvin.git && \
    git fetch --depth=1 origin e8e0678f7305a2556cf76a5fe9eb2ae8006ba932 && \
    git checkout FETCH_HEAD

RUN mkdir -p /logs/verifier

WORKDIR /workspace/marvin
