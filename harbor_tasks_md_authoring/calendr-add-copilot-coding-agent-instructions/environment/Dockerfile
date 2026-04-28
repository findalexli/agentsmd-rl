FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && apt-get install -y --no-install-recommends \
    git ca-certificates curl \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir pytest==8.3.4 pyyaml==6.0.2

WORKDIR /workspace
RUN git init /workspace/calendr && \
    cd /workspace/calendr && \
    git remote add origin https://github.com/pakerwreah/Calendr.git && \
    git fetch --depth=1 origin b83bc947d6d97b6c8eaf13bae8ed4d4bd4020055 && \
    git checkout FETCH_HEAD

RUN mkdir -p /logs/verifier

WORKDIR /workspace/calendr
