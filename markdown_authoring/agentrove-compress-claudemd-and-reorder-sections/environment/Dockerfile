FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && apt-get install -y --no-install-recommends \
    git ca-certificates curl \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir pytest==8.3.4 pyyaml==6.0.2

WORKDIR /workspace
RUN git init /workspace/agentrove && \
    cd /workspace/agentrove && \
    git remote add origin https://github.com/Mng-dev-ai/agentrove.git && \
    git fetch --depth=1 origin 5649c19c0b68de671fc848d40fcba30bda14ef2d && \
    git checkout FETCH_HEAD

RUN mkdir -p /logs/verifier

WORKDIR /workspace/agentrove
