FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && apt-get install -y --no-install-recommends \
    git ca-certificates curl \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir pytest==8.3.4 pyyaml==6.0.2

WORKDIR /workspace
RUN git init /workspace/tsgolint && \
    cd /workspace/tsgolint && \
    git remote add origin https://github.com/oxc-project/tsgolint.git && \
    git fetch --depth=1 origin 42a817b2ac39c364e8b054d00bd1fb0947d0aa3a && \
    git checkout FETCH_HEAD

RUN mkdir -p /logs/verifier

WORKDIR /workspace/tsgolint
