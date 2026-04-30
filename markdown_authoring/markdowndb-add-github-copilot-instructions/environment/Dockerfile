FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && apt-get install -y --no-install-recommends \
    git ca-certificates curl \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir pytest==8.3.4 pyyaml==6.0.2

WORKDIR /workspace
RUN git init /workspace/markdowndb && \
    cd /workspace/markdowndb && \
    git remote add origin https://github.com/flowershow/markdowndb.git && \
    git fetch --depth=1 origin 979775ec0b47307fc3a99a754d4e9133a53b48ae && \
    git checkout FETCH_HEAD

RUN mkdir -p /logs/verifier

WORKDIR /workspace/markdowndb
