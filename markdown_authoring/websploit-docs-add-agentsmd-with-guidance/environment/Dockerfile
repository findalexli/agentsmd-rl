FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && apt-get install -y --no-install-recommends \
    git ca-certificates curl \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir pytest==8.3.4 pyyaml==6.0.2

WORKDIR /workspace
RUN git init /workspace/websploit && \
    cd /workspace/websploit && \
    git remote add origin https://github.com/The-Art-of-Hacking/websploit.git && \
    git fetch --depth=1 origin f6f0047cc9598b09cfb7576aeadce3c9edaf5cfd && \
    git checkout FETCH_HEAD

RUN mkdir -p /logs/verifier

WORKDIR /workspace/websploit
