FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && apt-get install -y --no-install-recommends \
    git ca-certificates curl \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir pytest==8.3.4 pyyaml==6.0.2

WORKDIR /workspace
RUN git init /workspace/phpstan-nette && \
    cd /workspace/phpstan-nette && \
    git remote add origin https://github.com/phpstan/phpstan-nette.git && \
    git fetch --depth=1 origin cd8d10fe7be9723e09a76e02b0cc59d0cd7344e1 && \
    git checkout FETCH_HEAD

RUN mkdir -p /logs/verifier

WORKDIR /workspace/phpstan-nette
