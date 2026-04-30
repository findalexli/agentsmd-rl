FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && apt-get install -y --no-install-recommends \
    git ca-certificates curl \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir pytest==8.3.4 pyyaml==6.0.2

WORKDIR /workspace
RUN git init /workspace/sshpiper && \
    cd /workspace/sshpiper && \
    git remote add origin https://github.com/tg123/sshpiper.git && \
    git fetch --depth=1 origin 7773e2f7fec6c02feb3241b980e1a8de9a47bf1b && \
    git checkout FETCH_HEAD

RUN mkdir -p /logs/verifier

WORKDIR /workspace/sshpiper
