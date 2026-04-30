FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && apt-get install -y --no-install-recommends \
    git ca-certificates curl \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir pytest==8.3.4 pyyaml==6.0.2

WORKDIR /workspace
RUN git init /workspace/vpnhide && \
    cd /workspace/vpnhide && \
    git remote add origin https://github.com/okhsunrog/vpnhide.git && \
    git fetch --depth=1 origin d26f7096f3868a0749decc186b9c92eb3f608e84 && \
    git checkout FETCH_HEAD

RUN mkdir -p /logs/verifier

WORKDIR /workspace/vpnhide
