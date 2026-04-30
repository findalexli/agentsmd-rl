FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && apt-get install -y --no-install-recommends \
    git ca-certificates curl \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir pytest==8.3.4 pyyaml==6.0.2

WORKDIR /workspace
RUN git init /workspace/fuxt && \
    cd /workspace/fuxt && \
    git remote add origin https://github.com/funkhaus/fuxt.git && \
    git fetch --depth=1 origin 4bdc65b2f2d4bfc22cb6e2ef5e872c5593d192a9 && \
    git checkout FETCH_HEAD

RUN mkdir -p /logs/verifier

WORKDIR /workspace/fuxt
