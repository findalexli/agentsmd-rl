FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && apt-get install -y --no-install-recommends \
    git ca-certificates curl \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir pytest==8.3.4 pyyaml==6.0.2

WORKDIR /workspace
RUN git init /workspace/baoyu-skills && \
    cd /workspace/baoyu-skills && \
    git remote add origin https://github.com/JimLiu/baoyu-skills.git && \
    git fetch --depth=1 origin 661c74cce441d6d81393b3bd06a2fca336806279 && \
    git checkout FETCH_HEAD

RUN mkdir -p /logs/verifier

WORKDIR /workspace/baoyu-skills
