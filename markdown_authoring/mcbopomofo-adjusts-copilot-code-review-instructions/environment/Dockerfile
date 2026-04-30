FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && apt-get install -y --no-install-recommends \
    git ca-certificates curl \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir pytest==8.3.4 pyyaml==6.0.2

WORKDIR /workspace
RUN git init /workspace/mcbopomofo && \
    cd /workspace/mcbopomofo && \
    git remote add origin https://github.com/openvanilla/McBopomofo.git && \
    git fetch --depth=1 origin 971d9e0e354cfa981b5dfde0757264e95d194b0d && \
    git checkout FETCH_HEAD

RUN mkdir -p /logs/verifier

WORKDIR /workspace/mcbopomofo
