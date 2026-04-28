FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && apt-get install -y --no-install-recommends \
    git ca-certificates curl \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir pytest==8.3.4 pyyaml==6.0.2

WORKDIR /workspace
RUN git init /workspace/pollinations && \
    cd /workspace/pollinations && \
    git remote add origin https://github.com/pollinations/pollinations.git && \
    git fetch --depth=1 origin 0d8eba0e9d79d3f1dc156d78048b007adbe15de9 && \
    git checkout FETCH_HEAD

RUN mkdir -p /logs/verifier

WORKDIR /workspace/pollinations
