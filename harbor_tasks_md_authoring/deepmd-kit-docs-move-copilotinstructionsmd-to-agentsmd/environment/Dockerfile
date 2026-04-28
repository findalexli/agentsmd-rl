FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && apt-get install -y --no-install-recommends \
    git ca-certificates curl \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir pytest==8.3.4 pyyaml==6.0.2

WORKDIR /workspace
RUN git init /workspace/deepmd-kit && \
    cd /workspace/deepmd-kit && \
    git remote add origin https://github.com/deepmodeling/deepmd-kit.git && \
    git fetch --depth=1 origin 15c2b7d400de6f9e318f8ba37a75a6eb30c254c3 && \
    git checkout FETCH_HEAD

RUN mkdir -p /logs/verifier

WORKDIR /workspace/deepmd-kit
