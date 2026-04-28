FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && apt-get install -y --no-install-recommends \
    git ca-certificates curl \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir pytest==8.3.4 pyyaml==6.0.2

WORKDIR /workspace
RUN git init /workspace/nginx-build && \
    cd /workspace/nginx-build && \
    git remote add origin https://github.com/cubicdaiya/nginx-build.git && \
    git fetch --depth=1 origin 5248ffa966eaf02652dee0f2e7b7fb658a919758 && \
    git checkout FETCH_HEAD

RUN mkdir -p /logs/verifier

WORKDIR /workspace/nginx-build
