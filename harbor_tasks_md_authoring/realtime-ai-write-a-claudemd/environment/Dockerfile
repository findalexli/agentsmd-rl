FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && apt-get install -y --no-install-recommends \
    git ca-certificates curl \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir pytest==8.3.4 pyyaml==6.0.2

WORKDIR /workspace
RUN git init /workspace/realtime-ai && \
    cd /workspace/realtime-ai && \
    git remote add origin https://github.com/realtime-ai/realtime-ai.git && \
    git fetch --depth=1 origin b0319444019b9466dcaee08006dd3cb1b58ecf76 && \
    git checkout FETCH_HEAD

RUN mkdir -p /logs/verifier

WORKDIR /workspace/realtime-ai
