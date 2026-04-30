FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && apt-get install -y --no-install-recommends \
    git ca-certificates curl \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir pytest==8.3.4 pyyaml==6.0.2

WORKDIR /workspace
RUN git init /workspace/pocket-casts-ios && \
    cd /workspace/pocket-casts-ios && \
    git remote add origin https://github.com/Automattic/pocket-casts-ios.git && \
    git fetch --depth=1 origin 1077d918531229e8f19bd44b3bfcd8b316668d4e && \
    git checkout FETCH_HEAD

RUN mkdir -p /logs/verifier

WORKDIR /workspace/pocket-casts-ios
