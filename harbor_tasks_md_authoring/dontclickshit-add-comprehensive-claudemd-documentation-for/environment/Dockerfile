FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && apt-get install -y --no-install-recommends \
    git ca-certificates curl \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir pytest==8.3.4 pyyaml==6.0.2

WORKDIR /workspace
RUN git init /workspace/dontclickshit && \
    cd /workspace/dontclickshit && \
    git remote add origin https://github.com/sapran/dontclickshit.git && \
    git fetch --depth=1 origin b6cc1e6f5371b423f5fb222e6ace22090dc4d15b && \
    git checkout FETCH_HEAD

RUN mkdir -p /logs/verifier

WORKDIR /workspace/dontclickshit
