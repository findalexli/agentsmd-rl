FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && apt-get install -y --no-install-recommends \
        git \
        ca-certificates \
        && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir \
        pytest==8.3.4 \
        pytest-json-ctrf==0.4.1 \
        pyyaml==6.0.2

WORKDIR /workspace

RUN git clone --filter=blob:none https://github.com/ant-design/ant-design.git /workspace/ant-design && \
    cd /workspace/ant-design && \
    git checkout 3db46e98f1743a2116ad90d30405136a5ff22ab5

RUN mkdir -p /logs/verifier

WORKDIR /workspace/ant-design
