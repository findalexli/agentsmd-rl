FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && apt-get install -y --no-install-recommends \
    git ca-certificates curl \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir pytest==8.3.4 pyyaml==6.0.2

WORKDIR /workspace
RUN git init /workspace/homebrew-cask && \
    cd /workspace/homebrew-cask && \
    git remote add origin https://github.com/Homebrew/homebrew-cask.git && \
    git fetch --depth=1 origin 6fd186a91c654387c5923e12518f554cde229f8e && \
    git checkout FETCH_HEAD

RUN mkdir -p /logs/verifier

WORKDIR /workspace/homebrew-cask
