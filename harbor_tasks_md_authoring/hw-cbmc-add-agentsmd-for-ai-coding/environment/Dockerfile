FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && apt-get install -y --no-install-recommends \
    git ca-certificates curl \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir pytest==8.3.4 pyyaml==6.0.2

WORKDIR /workspace
RUN git init /workspace/hw-cbmc && \
    cd /workspace/hw-cbmc && \
    git remote add origin https://github.com/diffblue/hw-cbmc.git && \
    git fetch --depth=1 origin 420bd6485e5242e37c8cc43a33c0949441c64fd1 && \
    git checkout FETCH_HEAD

RUN mkdir -p /logs/verifier

WORKDIR /workspace/hw-cbmc
