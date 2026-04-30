FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && apt-get install -y --no-install-recommends \
    git ca-certificates curl \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir pytest==8.3.4 pyyaml==6.0.2

WORKDIR /workspace
RUN git init /workspace/tikmatrix-desktop && \
    cd /workspace/tikmatrix-desktop && \
    git remote add origin https://github.com/tikmatrix/tikmatrix-desktop.git && \
    git fetch --depth=1 origin 4fac268b8e9ce67abccd2c74cd64c7d1d73c57e6 && \
    git checkout FETCH_HEAD

RUN mkdir -p /logs/verifier

WORKDIR /workspace/tikmatrix-desktop
