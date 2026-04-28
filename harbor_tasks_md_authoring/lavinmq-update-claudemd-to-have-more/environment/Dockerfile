FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && apt-get install -y --no-install-recommends \
    git ca-certificates curl \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir pytest==8.3.4 pyyaml==6.0.2

WORKDIR /workspace
RUN git init /workspace/lavinmq && \
    cd /workspace/lavinmq && \
    git remote add origin https://github.com/cloudamqp/lavinmq.git && \
    git fetch --depth=1 origin 3fdc288c09e66032315291b7e9a8c9dc7d6ddcf1 && \
    git checkout FETCH_HEAD

RUN mkdir -p /logs/verifier

WORKDIR /workspace/lavinmq
