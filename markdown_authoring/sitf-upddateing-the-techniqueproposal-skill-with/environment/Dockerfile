FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && apt-get install -y --no-install-recommends \
    git ca-certificates curl \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir pytest==8.3.4 pyyaml==6.0.2

WORKDIR /workspace
RUN git init /workspace/sitf && \
    cd /workspace/sitf && \
    git remote add origin https://github.com/wiz-sec-public/SITF.git && \
    git fetch --depth=1 origin 89bac32df9932d37ecbdd6b292c9bf23f3bec1de && \
    git checkout FETCH_HEAD

RUN mkdir -p /logs/verifier

WORKDIR /workspace/sitf
