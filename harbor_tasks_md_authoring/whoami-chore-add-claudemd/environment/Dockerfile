FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && apt-get install -y --no-install-recommends \
    git ca-certificates curl \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir pytest==8.3.4 pyyaml==6.0.2

WORKDIR /workspace
RUN git init /workspace/whoami && \
    cd /workspace/whoami && \
    git remote add origin https://github.com/whoami-wiki/whoami.git && \
    git fetch --depth=1 origin 7b9f9f8cfea4698587c193b22a888c351b8a80b6 && \
    git checkout FETCH_HEAD

RUN mkdir -p /logs/verifier

WORKDIR /workspace/whoami
