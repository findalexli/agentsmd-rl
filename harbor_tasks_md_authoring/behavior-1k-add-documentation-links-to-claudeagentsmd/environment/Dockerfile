FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && apt-get install -y --no-install-recommends \
    git ca-certificates curl \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir pytest==8.3.4 pyyaml==6.0.2

WORKDIR /workspace
RUN git init /workspace/behavior-1k && \
    cd /workspace/behavior-1k && \
    git remote add origin https://github.com/StanfordVL/BEHAVIOR-1K.git && \
    git fetch --depth=1 origin 2376d97dff7f1ccc99d8b92201df702252776ce1 && \
    git checkout FETCH_HEAD

RUN mkdir -p /logs/verifier

WORKDIR /workspace/behavior-1k
