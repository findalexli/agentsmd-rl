FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && apt-get install -y --no-install-recommends \
    git ca-certificates curl \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir pytest==8.3.4 pyyaml==6.0.2

WORKDIR /workspace
RUN git init /workspace/gh-aw && \
    cd /workspace/gh-aw && \
    git remote add origin https://github.com/github/gh-aw.git && \
    git fetch --depth=1 origin d4858ffcd13c8db5c754973f8f4a4d54a0db893b && \
    git checkout FETCH_HEAD

RUN mkdir -p /logs/verifier

WORKDIR /workspace/gh-aw
