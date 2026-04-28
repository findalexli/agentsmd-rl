FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && apt-get install -y --no-install-recommends \
    git ca-certificates curl \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir pytest==8.3.4 pyyaml==6.0.2

WORKDIR /workspace
RUN git init /workspace/rsbuild && \
    cd /workspace/rsbuild && \
    git remote add origin https://github.com/web-infra-dev/rsbuild.git && \
    git fetch --depth=1 origin 81ca761d8521c7b791a0ca00e7c6ab523d1702f1 && \
    git checkout FETCH_HEAD

RUN mkdir -p /logs/verifier

WORKDIR /workspace/rsbuild
