FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && apt-get install -y --no-install-recommends \
    git ca-certificates curl \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir pytest==8.3.4 pyyaml==6.0.2

WORKDIR /workspace
RUN git init /workspace/vltpkg && \
    cd /workspace/vltpkg && \
    git remote add origin https://github.com/vltpkg/vltpkg.git && \
    git fetch --depth=1 origin 2c41a0a17c09bb5dfba28fd2a566f62e6efed0ff && \
    git checkout FETCH_HEAD

RUN mkdir -p /logs/verifier

WORKDIR /workspace/vltpkg
