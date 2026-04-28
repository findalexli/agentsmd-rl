FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && apt-get install -y --no-install-recommends \
    git ca-certificates curl \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir pytest==8.3.4 pyyaml==6.0.2

WORKDIR /workspace
RUN git init /workspace/indicator && \
    cd /workspace/indicator && \
    git remote add origin https://github.com/cinar/indicator.git && \
    git fetch --depth=1 origin 62ad62ec91ccf9b4267e21c8d2cde54aecb5a898 && \
    git checkout FETCH_HEAD

RUN mkdir -p /logs/verifier

WORKDIR /workspace/indicator
