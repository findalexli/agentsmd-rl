FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && apt-get install -y --no-install-recommends \
    git ca-certificates curl \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir pytest==8.3.4 pyyaml==6.0.2

WORKDIR /workspace
RUN git init /workspace/verify-rust-std && \
    cd /workspace/verify-rust-std && \
    git remote add origin https://github.com/model-checking/verify-rust-std.git && \
    git fetch --depth=1 origin 0b8a9a9025f84964615d048093b9975c4ab248ad && \
    git checkout FETCH_HEAD

RUN mkdir -p /logs/verifier

WORKDIR /workspace/verify-rust-std
