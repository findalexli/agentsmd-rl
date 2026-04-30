FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && apt-get install -y --no-install-recommends \
    git ca-certificates curl \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir pytest==8.3.4 pyyaml==6.0.2

WORKDIR /workspace
RUN git init /workspace/vibing-steampunk && \
    cd /workspace/vibing-steampunk && \
    git remote add origin https://github.com/oisee/vibing-steampunk.git && \
    git fetch --depth=1 origin 0826ff413dedd9943ef8c4791b21a703f8362ee8 && \
    git checkout FETCH_HEAD

RUN mkdir -p /logs/verifier

WORKDIR /workspace/vibing-steampunk
