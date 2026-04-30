FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && apt-get install -y --no-install-recommends \
    git ca-certificates curl \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir pytest==8.3.4 pyyaml==6.0.2

WORKDIR /workspace
RUN git init /workspace/auth0.swift && \
    cd /workspace/auth0.swift && \
    git remote add origin https://github.com/auth0/Auth0.swift.git && \
    git fetch --depth=1 origin 265c209b6cce2c6b92585e18669751f64c459c1f && \
    git checkout FETCH_HEAD

RUN mkdir -p /logs/verifier

WORKDIR /workspace/auth0.swift
