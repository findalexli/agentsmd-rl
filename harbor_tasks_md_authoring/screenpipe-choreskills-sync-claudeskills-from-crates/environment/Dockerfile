FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && apt-get install -y --no-install-recommends \
    git ca-certificates curl \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir pytest==8.3.4 pyyaml==6.0.2

WORKDIR /workspace
RUN git init /workspace/screenpipe && \
    cd /workspace/screenpipe && \
    git remote add origin https://github.com/screenpipe/screenpipe.git && \
    git fetch --depth=1 origin 30afa2e5774b28c494363e7111cc61c917c0f825 && \
    git checkout FETCH_HEAD

RUN mkdir -p /logs/verifier

WORKDIR /workspace/screenpipe
