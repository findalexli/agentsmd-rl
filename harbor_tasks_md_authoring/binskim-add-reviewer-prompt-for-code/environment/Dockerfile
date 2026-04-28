FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && apt-get install -y --no-install-recommends \
    git ca-certificates curl \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir pytest==8.3.4 pyyaml==6.0.2

WORKDIR /workspace
RUN git init /workspace/binskim && \
    cd /workspace/binskim && \
    git remote add origin https://github.com/microsoft/binskim.git && \
    git fetch --depth=1 origin 7946d7c5df1961141d8e88d4fbbdd3dfc01f921a && \
    git checkout FETCH_HEAD

RUN mkdir -p /logs/verifier

WORKDIR /workspace/binskim
