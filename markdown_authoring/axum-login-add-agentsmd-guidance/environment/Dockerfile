FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && apt-get install -y --no-install-recommends \
    git ca-certificates curl \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir pytest==8.3.4 pyyaml==6.0.2

WORKDIR /workspace
RUN git init /workspace/axum-login && \
    cd /workspace/axum-login && \
    git remote add origin https://github.com/maxcountryman/axum-login.git && \
    git fetch --depth=1 origin 6dc750a9ea1cb05564822904c42a79198db9b0bf && \
    git checkout FETCH_HEAD

RUN mkdir -p /logs/verifier

WORKDIR /workspace/axum-login
