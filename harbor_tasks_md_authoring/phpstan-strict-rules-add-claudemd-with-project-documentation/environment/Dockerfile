FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && apt-get install -y --no-install-recommends \
    git ca-certificates curl \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir pytest==8.3.4 pyyaml==6.0.2

WORKDIR /workspace
RUN git init /workspace/phpstan-strict-rules && \
    cd /workspace/phpstan-strict-rules && \
    git remote add origin https://github.com/phpstan/phpstan-strict-rules.git && \
    git fetch --depth=1 origin 38c26a9b6e693fdc313c2eccd252f1bbaaa9011a && \
    git checkout FETCH_HEAD

RUN mkdir -p /logs/verifier

WORKDIR /workspace/phpstan-strict-rules
