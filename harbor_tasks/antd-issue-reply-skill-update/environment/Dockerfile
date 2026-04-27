FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && apt-get install -y --no-install-recommends \
        git \
        ca-certificates \
        grep \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir \
        pytest==8.3.4 \
        PyYAML==6.0.2

WORKDIR /workspace

RUN mkdir -p ant-design && cd ant-design && \
    git init -q && \
    git remote add origin https://github.com/ant-design/ant-design.git && \
    git -c protocol.version=2 fetch --depth 1 --filter=blob:none origin 15df8e60f14be71095dff1640933b92b770e9217 && \
    git checkout -q FETCH_HEAD

WORKDIR /workspace/ant-design

RUN mkdir -p /logs/verifier
