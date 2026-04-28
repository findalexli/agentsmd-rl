FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && apt-get install -y --no-install-recommends \
    git ca-certificates curl \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir pytest==8.3.4 pyyaml==6.0.2

WORKDIR /workspace
RUN git init /workspace/tfplan2md && \
    cd /workspace/tfplan2md && \
    git remote add origin https://github.com/oocx/tfplan2md.git && \
    git fetch --depth=1 origin dbb43f94f202017b97039640a6f3d10abb47331a && \
    git checkout FETCH_HEAD

RUN mkdir -p /logs/verifier

WORKDIR /workspace/tfplan2md
