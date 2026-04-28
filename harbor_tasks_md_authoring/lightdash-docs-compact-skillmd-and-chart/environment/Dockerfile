FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && apt-get install -y --no-install-recommends \
    git ca-certificates curl \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir pytest==8.3.4 pyyaml==6.0.2

WORKDIR /workspace
RUN git init /workspace/lightdash && \
    cd /workspace/lightdash && \
    git remote add origin https://github.com/lightdash/lightdash.git && \
    git fetch --depth=1 origin 38b09e3ffd225f43696a444c9b5cce3d85a8d15c && \
    git checkout FETCH_HEAD

RUN mkdir -p /logs/verifier

WORKDIR /workspace/lightdash
