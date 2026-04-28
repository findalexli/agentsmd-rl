FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && apt-get install -y --no-install-recommends \
    git ca-certificates curl \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir pytest==8.3.4 pyyaml==6.0.2

WORKDIR /workspace
RUN git init /workspace/wp-calypso && \
    cd /workspace/wp-calypso && \
    git remote add origin https://github.com/Automattic/wp-calypso.git && \
    git fetch --depth=1 origin de23afacc6cf7141c9699fe6ca148bef4bf7dbf5 && \
    git checkout FETCH_HEAD

RUN mkdir -p /logs/verifier

WORKDIR /workspace/wp-calypso
