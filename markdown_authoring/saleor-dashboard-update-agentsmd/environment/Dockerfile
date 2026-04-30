FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && apt-get install -y --no-install-recommends \
    git ca-certificates curl \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir pytest==8.3.4 pyyaml==6.0.2

WORKDIR /workspace
RUN git init /workspace/saleor-dashboard && \
    cd /workspace/saleor-dashboard && \
    git remote add origin https://github.com/saleor/saleor-dashboard.git && \
    git fetch --depth=1 origin 1c8db1560c5a78def49f345e17e0824048c18783 && \
    git checkout FETCH_HEAD

RUN mkdir -p /logs/verifier

WORKDIR /workspace/saleor-dashboard
