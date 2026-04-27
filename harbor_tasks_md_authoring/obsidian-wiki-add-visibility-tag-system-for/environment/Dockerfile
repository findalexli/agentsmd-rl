FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && apt-get install -y --no-install-recommends \
    git ca-certificates curl \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir pytest==8.3.4 pyyaml==6.0.2

WORKDIR /workspace
RUN git init /workspace/obsidian-wiki && \
    cd /workspace/obsidian-wiki && \
    git remote add origin https://github.com/Ar9av/obsidian-wiki.git && \
    git fetch --depth=1 origin 9c1b51769dee6a1bd2717e3c77cfe21e0e35ad9c && \
    git checkout FETCH_HEAD

RUN mkdir -p /logs/verifier

WORKDIR /workspace/obsidian-wiki
