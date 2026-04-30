FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && apt-get install -y --no-install-recommends \
    git ca-certificates curl \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir pytest==8.3.4 pyyaml==6.0.2

WORKDIR /workspace
RUN git init /workspace/developer-kit && \
    cd /workspace/developer-kit && \
    git remote add origin https://github.com/giuseppe-trisciuoglio/developer-kit.git && \
    git fetch --depth=1 origin 4b100337c3d7579b1d1fd952acdf61130ccf4b2e && \
    git checkout FETCH_HEAD

RUN mkdir -p /logs/verifier

WORKDIR /workspace/developer-kit
