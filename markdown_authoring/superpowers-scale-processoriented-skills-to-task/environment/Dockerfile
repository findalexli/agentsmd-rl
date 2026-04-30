FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && apt-get install -y --no-install-recommends \
    git ca-certificates curl \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir pytest==8.3.4 pyyaml==6.0.2

WORKDIR /workspace
RUN git init /workspace/superpowers && \
    cd /workspace/superpowers && \
    git remote add origin https://github.com/obra/superpowers.git && \
    git fetch --depth=1 origin bf6d3369502f6a9c1901e6a02998c398be26d9ed && \
    git checkout FETCH_HEAD

RUN mkdir -p /logs/verifier

WORKDIR /workspace/superpowers
