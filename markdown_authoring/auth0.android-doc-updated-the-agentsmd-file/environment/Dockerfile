FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && apt-get install -y --no-install-recommends \
    git ca-certificates curl \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir pytest==8.3.4 pyyaml==6.0.2

WORKDIR /workspace
RUN git init /workspace/auth0.android && \
    cd /workspace/auth0.android && \
    git remote add origin https://github.com/auth0/Auth0.Android.git && \
    git fetch --depth=1 origin b8fc19ea7b097c87f025008c894495a0e48f7650 && \
    git checkout FETCH_HEAD

RUN mkdir -p /logs/verifier

WORKDIR /workspace/auth0.android
