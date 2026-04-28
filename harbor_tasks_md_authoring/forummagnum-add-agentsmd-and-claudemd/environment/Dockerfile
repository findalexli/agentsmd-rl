FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && apt-get install -y --no-install-recommends \
    git ca-certificates curl \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir pytest==8.3.4 pyyaml==6.0.2

WORKDIR /workspace
RUN git init /workspace/forummagnum && \
    cd /workspace/forummagnum && \
    git remote add origin https://github.com/ForumMagnum/ForumMagnum.git && \
    git fetch --depth=1 origin c0439d57e17f88664f70aff85f57fa65d45e7c88 && \
    git checkout FETCH_HEAD

RUN mkdir -p /logs/verifier

WORKDIR /workspace/forummagnum
