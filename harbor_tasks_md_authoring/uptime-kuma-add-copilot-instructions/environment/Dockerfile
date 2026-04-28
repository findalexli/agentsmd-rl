FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && apt-get install -y --no-install-recommends \
    git ca-certificates curl \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir pytest==8.3.4 pyyaml==6.0.2

WORKDIR /workspace
RUN git init /workspace/uptime-kuma && \
    cd /workspace/uptime-kuma && \
    git remote add origin https://github.com/louislam/uptime-kuma.git && \
    git fetch --depth=1 origin 79c844d598ecda3d4d339e1632a1cc18f20bd170 && \
    git checkout FETCH_HEAD

RUN mkdir -p /logs/verifier

WORKDIR /workspace/uptime-kuma
