FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && apt-get install -y --no-install-recommends \
    git ca-certificates curl \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir pytest==8.3.4 pyyaml==6.0.2

WORKDIR /workspace
RUN git init /workspace/human-skill-tree && \
    cd /workspace/human-skill-tree && \
    git remote add origin https://github.com/24kchengYe/human-skill-tree.git && \
    git fetch --depth=1 origin b001e58650ae96c4929bca768a8ade9a6ce32f1c && \
    git checkout FETCH_HEAD

RUN mkdir -p /logs/verifier

WORKDIR /workspace/human-skill-tree
