FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && apt-get install -y --no-install-recommends \
    git ca-certificates curl \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir pytest==8.3.4 pyyaml==6.0.2

WORKDIR /workspace
RUN git init /workspace/ai-maestro && \
    cd /workspace/ai-maestro && \
    git remote add origin https://github.com/23blocks-OS/ai-maestro.git && \
    git fetch --depth=1 origin 8f5eaa49d19e16484095ef1a1366ae20feb142bf && \
    git checkout FETCH_HEAD

RUN mkdir -p /logs/verifier

WORKDIR /workspace/ai-maestro
