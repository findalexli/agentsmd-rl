FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && apt-get install -y --no-install-recommends \
    git ca-certificates curl \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir pytest==8.3.4 pyyaml==6.0.2

WORKDIR /workspace
RUN git init /workspace/marimo-pair && \
    cd /workspace/marimo-pair && \
    git remote add origin https://github.com/marimo-team/marimo-pair.git && \
    git fetch --depth=1 origin fafeb8eea79c0fb4c019aa05643ad305c44cb68d && \
    git checkout FETCH_HEAD

RUN mkdir -p /logs/verifier

WORKDIR /workspace/marimo-pair
