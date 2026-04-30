FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && apt-get install -y --no-install-recommends \
    git ca-certificates curl \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir pytest==8.3.4 pyyaml==6.0.2

WORKDIR /workspace
RUN git init /workspace/anarlog && \
    cd /workspace/anarlog && \
    git remote add origin https://github.com/fastrepl/anarlog.git && \
    git fetch --depth=1 origin f13ee4034b1d5d28ff76bd71ca4c01734e6c7dd7 && \
    git checkout FETCH_HEAD

RUN mkdir -p /logs/verifier

WORKDIR /workspace/anarlog
