FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && apt-get install -y --no-install-recommends \
    git ca-certificates curl \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir pytest==8.3.4 pyyaml==6.0.2

WORKDIR /workspace
RUN git init /workspace/claude-mpm && \
    cd /workspace/claude-mpm && \
    git remote add origin https://github.com/bobmatnyc/claude-mpm.git && \
    git fetch --depth=1 origin 3bbfb00cfeb9dbff600325e1ac6761bf7c300308 && \
    git checkout FETCH_HEAD

RUN mkdir -p /logs/verifier

WORKDIR /workspace/claude-mpm
