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
    git fetch --depth=1 origin a539397a6d6d3322bf39d96fc424a5ddd4e59d0c && \
    git checkout FETCH_HEAD

RUN mkdir -p /logs/verifier

WORKDIR /workspace/ant-design
