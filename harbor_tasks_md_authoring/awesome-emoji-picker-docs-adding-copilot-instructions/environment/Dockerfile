FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && apt-get install -y --no-install-recommends \
    git ca-certificates curl \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir pytest==8.3.4 pyyaml==6.0.2

WORKDIR /workspace
RUN git init /workspace/awesome-emoji-picker && \
    cd /workspace/awesome-emoji-picker && \
    git remote add origin https://github.com/rugk/awesome-emoji-picker.git && \
    git fetch --depth=1 origin 5e7824c2fb907ca5b4ae3149f7d02fe5f2a0ad31 && \
    git checkout FETCH_HEAD

RUN mkdir -p /logs/verifier

WORKDIR /workspace/awesome-emoji-picker
