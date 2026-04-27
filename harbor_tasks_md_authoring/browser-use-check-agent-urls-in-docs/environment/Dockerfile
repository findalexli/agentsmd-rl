FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && apt-get install -y --no-install-recommends \
    git ca-certificates curl \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir pytest==8.3.4 pyyaml==6.0.2

WORKDIR /workspace
RUN git init /workspace/browser-use && \
    cd /workspace/browser-use && \
    git remote add origin https://github.com/browser-use/browser-use.git && \
    git fetch --depth=1 origin 1011e3e6618c0842e9b12b87ab4c3b97db139ad8 && \
    git checkout FETCH_HEAD

RUN mkdir -p /logs/verifier

WORKDIR /workspace/browser-use
