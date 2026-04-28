FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && apt-get install -y --no-install-recommends \
    git ca-certificates curl \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir pytest==8.3.4 pyyaml==6.0.2

WORKDIR /workspace
RUN git init /workspace/aidd && \
    cd /workspace/aidd && \
    git remote add origin https://github.com/paralleldrive/aidd.git && \
    git fetch --depth=1 origin 99e1e8fa9165de2e45fe95f3f8e0c0b64ff05e27 && \
    git checkout FETCH_HEAD

RUN mkdir -p /logs/verifier

WORKDIR /workspace/aidd
