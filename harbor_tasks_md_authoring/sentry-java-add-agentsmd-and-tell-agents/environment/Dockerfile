FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && apt-get install -y --no-install-recommends \
    git ca-certificates curl \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir pytest==8.3.4 pyyaml==6.0.2

WORKDIR /workspace
RUN git init /workspace/sentry-java && \
    cd /workspace/sentry-java && \
    git remote add origin https://github.com/getsentry/sentry-java.git && \
    git fetch --depth=1 origin 22f43457e436a2b0eff84aac3f3f85f335398c46 && \
    git checkout FETCH_HEAD

RUN mkdir -p /logs/verifier

WORKDIR /workspace/sentry-java
