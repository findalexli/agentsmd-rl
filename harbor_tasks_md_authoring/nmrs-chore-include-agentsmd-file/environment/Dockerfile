FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && apt-get install -y --no-install-recommends \
    git ca-certificates curl \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir pytest==8.3.4 pyyaml==6.0.2

WORKDIR /workspace
RUN git init /workspace/nmrs && \
    cd /workspace/nmrs && \
    git remote add origin https://github.com/cachebag/nmrs.git && \
    git fetch --depth=1 origin fdd5ccb268bd48a0c6cb7adf44663bb825a8fc63 && \
    git checkout FETCH_HEAD

RUN mkdir -p /logs/verifier

WORKDIR /workspace/nmrs
