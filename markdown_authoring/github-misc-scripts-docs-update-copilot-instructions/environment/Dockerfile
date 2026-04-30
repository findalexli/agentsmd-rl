FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && apt-get install -y --no-install-recommends \
    git ca-certificates curl \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir pytest==8.3.4 pyyaml==6.0.2

WORKDIR /workspace
RUN git init /workspace/github-misc-scripts && \
    cd /workspace/github-misc-scripts && \
    git remote add origin https://github.com/joshjohanning/github-misc-scripts.git && \
    git fetch --depth=1 origin 3c687614e383ab24d965d60ebedb83ff027229fc && \
    git checkout FETCH_HEAD

RUN mkdir -p /logs/verifier

WORKDIR /workspace/github-misc-scripts
