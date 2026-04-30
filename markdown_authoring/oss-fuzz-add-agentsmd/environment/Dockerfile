FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && apt-get install -y --no-install-recommends \
    git ca-certificates curl \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir pytest==8.3.4 pyyaml==6.0.2

WORKDIR /workspace
RUN git init /workspace/oss-fuzz && \
    cd /workspace/oss-fuzz && \
    git remote add origin https://github.com/google/oss-fuzz.git && \
    git fetch --depth=1 origin 24ddd2f93026b5a5cc5fccfe3588c2e6b3e19d35 && \
    git checkout FETCH_HEAD

RUN mkdir -p /logs/verifier

WORKDIR /workspace/oss-fuzz
