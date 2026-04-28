FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && apt-get install -y --no-install-recommends \
    git ca-certificates curl \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir pytest==8.3.4 pyyaml==6.0.2

WORKDIR /workspace
RUN git init /workspace/actionbook && \
    cd /workspace/actionbook && \
    git remote add origin https://github.com/actionbook/actionbook.git && \
    git fetch --depth=1 origin d12bfaff714fd318af5851cffa5aa2a74fbad77c && \
    git checkout FETCH_HEAD

RUN mkdir -p /logs/verifier

WORKDIR /workspace/actionbook
