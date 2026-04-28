FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && apt-get install -y --no-install-recommends \
    git ca-certificates curl \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir pytest==8.3.4 pyyaml==6.0.2

WORKDIR /workspace
RUN git init /workspace/gridlayout-compose && \
    cd /workspace/gridlayout-compose && \
    git remote add origin https://github.com/cheonjaeung/gridlayout-compose.git && \
    git fetch --depth=1 origin 80910a9d34bac947191d9fc8f266dd7910f8e28a && \
    git checkout FETCH_HEAD

RUN mkdir -p /logs/verifier

WORKDIR /workspace/gridlayout-compose
