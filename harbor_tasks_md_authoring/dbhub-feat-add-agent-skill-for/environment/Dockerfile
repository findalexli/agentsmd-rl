FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && apt-get install -y --no-install-recommends \
    git ca-certificates curl \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir pytest==8.3.4 pyyaml==6.0.2

WORKDIR /workspace
RUN git init /workspace/dbhub && \
    cd /workspace/dbhub && \
    git remote add origin https://github.com/bytebase/dbhub.git && \
    git fetch --depth=1 origin eb51ab6ec11e91f4eb6b3340cd8439b780caf904 && \
    git checkout FETCH_HEAD

RUN mkdir -p /logs/verifier

WORKDIR /workspace/dbhub
