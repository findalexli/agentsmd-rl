FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && apt-get install -y --no-install-recommends \
    git ca-certificates curl \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir pytest==8.3.4 pyyaml==6.0.2

WORKDIR /workspace
RUN git init /workspace/hanzi-browse && \
    cd /workspace/hanzi-browse && \
    git remote add origin https://github.com/hanzili/hanzi-browse.git && \
    git fetch --depth=1 origin e3ff93970d9447520efc4565f5e3286d58089d98 && \
    git checkout FETCH_HEAD

RUN mkdir -p /logs/verifier

WORKDIR /workspace/hanzi-browse
