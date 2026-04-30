FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && apt-get install -y --no-install-recommends \
    git ca-certificates curl \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir pytest==8.3.4 pyyaml==6.0.2

WORKDIR /workspace
RUN git init /workspace/nx.js && \
    cd /workspace/nx.js && \
    git remote add origin https://github.com/TooTallNate/nx.js.git && \
    git fetch --depth=1 origin 0b5eaf50ed66020707d4d666694dbaac489f6ca1 && \
    git checkout FETCH_HEAD

RUN mkdir -p /logs/verifier

WORKDIR /workspace/nx.js
