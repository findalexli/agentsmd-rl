FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && apt-get install -y --no-install-recommends \
    git ca-certificates curl \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir pytest==8.3.4 pyyaml==6.0.2

WORKDIR /workspace
RUN git init /workspace/mnelab && \
    cd /workspace/mnelab && \
    git remote add origin https://github.com/cbrnr/mnelab.git && \
    git fetch --depth=1 origin 9077a0071773e4bf3688b83ce7fe6a0c8914ca9c && \
    git checkout FETCH_HEAD

RUN mkdir -p /logs/verifier

WORKDIR /workspace/mnelab
