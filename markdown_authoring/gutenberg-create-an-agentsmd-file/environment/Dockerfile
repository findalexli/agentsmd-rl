FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && apt-get install -y --no-install-recommends \
    git ca-certificates curl \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir pytest==8.3.4 pyyaml==6.0.2

WORKDIR /workspace
RUN git init /workspace/gutenberg && \
    cd /workspace/gutenberg && \
    git remote add origin https://github.com/WordPress/gutenberg.git && \
    git fetch --depth=1 origin 24b48886eec82287eef3e7b31f2122933f1ad038 && \
    git checkout FETCH_HEAD

RUN mkdir -p /logs/verifier

WORKDIR /workspace/gutenberg
