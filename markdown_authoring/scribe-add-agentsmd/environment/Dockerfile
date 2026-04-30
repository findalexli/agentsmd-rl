FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && apt-get install -y --no-install-recommends \
    git ca-certificates curl \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir pytest==8.3.4 pyyaml==6.0.2

WORKDIR /workspace
RUN git init /workspace/scribe && \
    cd /workspace/scribe && \
    git remote add origin https://github.com/knuckleswtf/scribe.git && \
    git fetch --depth=1 origin b11b9b67699aedb357b6dafb2ec044156f813ca7 && \
    git checkout FETCH_HEAD

RUN mkdir -p /logs/verifier

WORKDIR /workspace/scribe
