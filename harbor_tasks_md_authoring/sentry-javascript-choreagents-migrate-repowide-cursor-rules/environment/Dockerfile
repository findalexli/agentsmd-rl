FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && apt-get install -y --no-install-recommends \
    git ca-certificates curl \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir pytest==8.3.4 pyyaml==6.0.2

WORKDIR /workspace
RUN git init /workspace/sentry-javascript && \
    cd /workspace/sentry-javascript && \
    git remote add origin https://github.com/getsentry/sentry-javascript.git && \
    git fetch --depth=1 origin 92694c1f2e53d9cece9c8eb8d20d59d9b4857411 && \
    git checkout FETCH_HEAD

RUN mkdir -p /logs/verifier

WORKDIR /workspace/sentry-javascript
