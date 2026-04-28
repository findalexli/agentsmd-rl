FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && apt-get install -y --no-install-recommends \
    git ca-certificates curl \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir pytest==8.3.4 pyyaml==6.0.2

WORKDIR /workspace
RUN git init /workspace/scalafix && \
    cd /workspace/scalafix && \
    git remote add origin https://github.com/scalacenter/scalafix.git && \
    git fetch --depth=1 origin 9af410d23966494416b2b9ec940b58d6a55caa9a && \
    git checkout FETCH_HEAD

RUN mkdir -p /logs/verifier

WORKDIR /workspace/scalafix
