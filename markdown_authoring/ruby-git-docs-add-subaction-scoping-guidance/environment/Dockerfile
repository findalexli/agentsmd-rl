FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && apt-get install -y --no-install-recommends \
    git ca-certificates curl \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir pytest==8.3.4 pyyaml==6.0.2

WORKDIR /workspace
RUN git init /workspace/ruby-git && \
    cd /workspace/ruby-git && \
    git remote add origin https://github.com/ruby-git/ruby-git.git && \
    git fetch --depth=1 origin 917036b035ad29610163612e6bfc2f95642c5b1a && \
    git checkout FETCH_HEAD

RUN mkdir -p /logs/verifier

WORKDIR /workspace/ruby-git
