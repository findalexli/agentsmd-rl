FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && apt-get install -y --no-install-recommends \
    git ca-certificates curl \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir pytest==8.3.4 pyyaml==6.0.2

WORKDIR /workspace
RUN git init /workspace/css-modules-kit && \
    cd /workspace/css-modules-kit && \
    git remote add origin https://github.com/mizdra/css-modules-kit.git && \
    git fetch --depth=1 origin 944361ea5a76a99f0da062a8aaf9dbc29a55fb3f && \
    git checkout FETCH_HEAD

RUN mkdir -p /logs/verifier

WORKDIR /workspace/css-modules-kit
