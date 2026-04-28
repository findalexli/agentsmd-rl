FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && apt-get install -y --no-install-recommends \
    git ca-certificates curl \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir pytest==8.3.4 pyyaml==6.0.2

WORKDIR /workspace
RUN git init /workspace/24pullrequests && \
    cd /workspace/24pullrequests && \
    git remote add origin https://github.com/24pullrequests/24pullrequests.git && \
    git fetch --depth=1 origin 221823325dcdb55f451ce89dfd3aedea42157342 && \
    git checkout FETCH_HEAD

RUN mkdir -p /logs/verifier

WORKDIR /workspace/24pullrequests
