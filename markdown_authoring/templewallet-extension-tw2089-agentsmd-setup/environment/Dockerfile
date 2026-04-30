FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && apt-get install -y --no-install-recommends \
    git ca-certificates curl \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir pytest==8.3.4 pyyaml==6.0.2

WORKDIR /workspace
RUN git init /workspace/templewallet-extension && \
    cd /workspace/templewallet-extension && \
    git remote add origin https://github.com/madfish-solutions/templewallet-extension.git && \
    git fetch --depth=1 origin 865a9f21eb2a42e039b2b7e0efbeaa489b337918 && \
    git checkout FETCH_HEAD

RUN mkdir -p /logs/verifier

WORKDIR /workspace/templewallet-extension
