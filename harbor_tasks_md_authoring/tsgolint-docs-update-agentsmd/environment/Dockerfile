FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && apt-get install -y --no-install-recommends \
    git ca-certificates curl \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir pytest==8.3.4 pyyaml==6.0.2

WORKDIR /workspace
RUN git init /workspace/tsgolint && \
    cd /workspace/tsgolint && \
    git remote add origin https://github.com/oxc-project/tsgolint.git && \
    git fetch --depth=1 origin 18cfce16537d034168f658fa7842f110d9b527b0 && \
    git checkout FETCH_HEAD

RUN mkdir -p /logs/verifier

WORKDIR /workspace/tsgolint
