FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && apt-get install -y --no-install-recommends \
    git ca-certificates curl \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir pytest==8.3.4 pyyaml==6.0.2

WORKDIR /workspace
RUN git init /workspace/ant-design && \
    cd /workspace/ant-design && \
    git remote add origin https://github.com/ant-design/ant-design.git && \
    git fetch --depth=1 origin dce9f138cb06cc679f889f5d20c0a0c3e5a7d268 && \
    git checkout FETCH_HEAD

RUN mkdir -p /logs/verifier

WORKDIR /workspace/ant-design
