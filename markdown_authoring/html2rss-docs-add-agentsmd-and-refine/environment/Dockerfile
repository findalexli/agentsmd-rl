FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && apt-get install -y --no-install-recommends \
    git ca-certificates curl \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir pytest==8.3.4 pyyaml==6.0.2

WORKDIR /workspace
RUN git init /workspace/html2rss && \
    cd /workspace/html2rss && \
    git remote add origin https://github.com/html2rss/html2rss.git && \
    git fetch --depth=1 origin 29660a74c2ac9330f60a99a1670241dde32a7222 && \
    git checkout FETCH_HEAD

RUN mkdir -p /logs/verifier

WORKDIR /workspace/html2rss
