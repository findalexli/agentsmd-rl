FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && apt-get install -y --no-install-recommends \
    git ca-certificates curl \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir pytest==8.3.4 pyyaml==6.0.2

WORKDIR /workspace
RUN git init /workspace/fizzy && \
    cd /workspace/fizzy && \
    git remote add origin https://github.com/basecamp/fizzy.git && \
    git fetch --depth=1 origin 72f87f2d8f1b6ee0669b174045dfefe12ea6e005 && \
    git checkout FETCH_HEAD

RUN mkdir -p /logs/verifier

WORKDIR /workspace/fizzy
