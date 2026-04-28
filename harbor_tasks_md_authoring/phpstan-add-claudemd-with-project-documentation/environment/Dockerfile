FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && apt-get install -y --no-install-recommends \
    git ca-certificates curl \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir pytest==8.3.4 pyyaml==6.0.2

WORKDIR /workspace
RUN git init /workspace/phpstan && \
    cd /workspace/phpstan && \
    git remote add origin https://github.com/phpstan/phpstan.git && \
    git fetch --depth=1 origin bf2080c6806f505a6c3a0ee31e87cb3636b9f2a9 && \
    git checkout FETCH_HEAD

RUN mkdir -p /logs/verifier

WORKDIR /workspace/phpstan
