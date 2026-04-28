FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && apt-get install -y --no-install-recommends \
    git ca-certificates curl \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir pytest==8.3.4 pyyaml==6.0.2

WORKDIR /workspace
RUN git init /workspace/python-openai-demos && \
    cd /workspace/python-openai-demos && \
    git remote add origin https://github.com/Azure-Samples/python-openai-demos.git && \
    git fetch --depth=1 origin 6e20d04472af6d7a31c8041ff510b548c90d0a61 && \
    git checkout FETCH_HEAD

RUN mkdir -p /logs/verifier

WORKDIR /workspace/python-openai-demos
