FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && apt-get install -y --no-install-recommends \
    git ca-certificates curl \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir pytest==8.3.4 pyyaml==6.0.2

WORKDIR /workspace
RUN git init /workspace/tds-fdw && \
    cd /workspace/tds-fdw && \
    git remote add origin https://github.com/tds-fdw/tds_fdw.git && \
    git fetch --depth=1 origin f2c87420781372bd7c7d1771517bd955443b2dbc && \
    git checkout FETCH_HEAD

RUN mkdir -p /logs/verifier

WORKDIR /workspace/tds-fdw
