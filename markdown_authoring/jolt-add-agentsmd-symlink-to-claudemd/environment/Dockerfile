FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && apt-get install -y --no-install-recommends \
    git ca-certificates curl \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir pytest==8.3.4 pyyaml==6.0.2

WORKDIR /workspace
RUN git init /workspace/jolt && \
    cd /workspace/jolt && \
    git remote add origin https://github.com/a16z/jolt.git && \
    git fetch --depth=1 origin 63b94268b895e5077a7c4ac4b7e5e63ce2df7b13 && \
    git checkout FETCH_HEAD

RUN mkdir -p /logs/verifier

WORKDIR /workspace/jolt
