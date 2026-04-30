FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && apt-get install -y --no-install-recommends \
    git ca-certificates curl \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir pytest==8.3.4 pyyaml==6.0.2

WORKDIR /workspace
RUN git init /workspace/h3-pg && \
    cd /workspace/h3-pg && \
    git remote add origin https://github.com/postgis/h3-pg.git && \
    git fetch --depth=1 origin edc9aa4de91d6cc91a9ad0bd9dcfd12501753834 && \
    git checkout FETCH_HEAD

RUN mkdir -p /logs/verifier

WORKDIR /workspace/h3-pg
