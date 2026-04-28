FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && apt-get install -y --no-install-recommends \
    git ca-certificates curl \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir pytest==8.3.4 pyyaml==6.0.2

WORKDIR /workspace
RUN git init /workspace/latchkey && \
    cd /workspace/latchkey && \
    git remote add origin https://github.com/imbue-ai/latchkey.git && \
    git fetch --depth=1 origin b5c300510a5c3b24405dd00ee4598abd75bc6a55 && \
    git checkout FETCH_HEAD

RUN mkdir -p /logs/verifier

WORKDIR /workspace/latchkey
