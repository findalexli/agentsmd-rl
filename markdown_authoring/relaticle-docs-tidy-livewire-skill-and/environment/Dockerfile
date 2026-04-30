FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && apt-get install -y --no-install-recommends \
    git ca-certificates curl \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir pytest==8.3.4 pyyaml==6.0.2

WORKDIR /workspace
RUN git init /workspace/relaticle && \
    cd /workspace/relaticle && \
    git remote add origin https://github.com/relaticle/relaticle.git && \
    git fetch --depth=1 origin 11ed71453e86739e0d94ae7e287a778ec7904801 && \
    git checkout FETCH_HEAD

RUN mkdir -p /logs/verifier

WORKDIR /workspace/relaticle
