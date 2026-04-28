FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && apt-get install -y --no-install-recommends \
    git ca-certificates curl \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir pytest==8.3.4 pyyaml==6.0.2

WORKDIR /workspace
RUN git init /workspace/seed-design && \
    cd /workspace/seed-design && \
    git remote add origin https://github.com/daangn/seed-design.git && \
    git fetch --depth=1 origin d57ae16c8c805f66de2c04cb03cbbbfbe15f5e5f && \
    git checkout FETCH_HEAD

RUN mkdir -p /logs/verifier

WORKDIR /workspace/seed-design
