FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && \
    apt-get install -y --no-install-recommends git ca-certificates && \
    rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir pytest==8.3.4

WORKDIR /workspace

RUN git clone --filter=blob:none https://github.com/ant-design/ant-design.git ant-design && \
    cd ant-design && \
    git checkout 777b4affe8c0d6075ba418ecf6013b510b57d4e4

WORKDIR /workspace/ant-design

RUN mkdir -p /logs/verifier
