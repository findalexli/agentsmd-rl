FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && apt-get install -y --no-install-recommends \
    git ca-certificates curl \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir pytest==8.3.4 pyyaml==6.0.2

WORKDIR /workspace
RUN git init /workspace/mailpoet && \
    cd /workspace/mailpoet && \
    git remote add origin https://github.com/mailpoet/mailpoet.git && \
    git fetch --depth=1 origin 6d2c22cc1abe049faf4275496f64e06c39b914e6 && \
    git checkout FETCH_HEAD

RUN mkdir -p /logs/verifier

WORKDIR /workspace/mailpoet
